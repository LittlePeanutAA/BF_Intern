"""minidb: CSDL nhỏ lưu mỗi bảng thành một file text, truy vấn bằng DBQuery kiểu chain.

    db = Database("data")
    q = DBQuery(db)
    q.select(["id", "name"]).where("class_id", 1).from_("student").get()

Định dạng file `<bảng>.txt`: dòng đầu là `cột:kiểu|cột:kiểu|...` (kiểu int, float, str),
các dòng sau là dữ liệu ngăn cách bằng '|'. Ô rỗng là None.
"""
from __future__ import annotations

import operator
import os
import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable

SEP = "|"
TYPES: dict[str, type] = {"int": int, "float": float, "str": str}
OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "=": operator.eq, "!=": operator.ne, "<": operator.lt, "<=": operator.le,
    ">": operator.gt, ">=": operator.ge, "in": lambda a, b: a in b,
}
Row = dict[str, Any]


class DBError(Exception):
    """Lỗi khi dùng sai API hoặc dữ liệu vi phạm schema."""


@dataclass
class Table:
    name: str
    columns: dict[str, type]
    rows: list[Row] = field(default_factory=list)

    def require(self, column: str) -> None:
        if column not in self.columns:
            raise DBError(f"bảng {self.name} không có cột '{column}'")

    def convert(self, column: str, value: Any) -> Any:
        """Đưa giá trị về đúng kiểu của cột; None giữ nguyên."""
        self.require(column)
        if value is None or value == "":
            return None
        kind = self.columns[column]
        try:
            value = kind(value)
        except (TypeError, ValueError):
            raise DBError(f"{self.name}.{column}: '{value}' không phải {kind.__name__}") from None
        if kind is str and (SEP in value or "\n" in value):
            raise DBError(f"{self.name}.{column}: không được chứa '{SEP}' hoặc xuống dòng")
        return value


class Database:
    """Quản lý các bảng trong một thư mục. Bảng được đọc khi dùng lần đầu rồi giữ trong bộ nhớ."""

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self._tables: dict[str, Table] = {}

    def _path(self, name: str) -> Path:
        return self.data_dir / f"{name}.txt"

    def has_table(self, name: str) -> bool:
        return name in self._tables or self._path(name).exists()

    def create_table(self, name: str, columns: dict[str, type]) -> Table:
        if self.has_table(name):
            raise DBError(f"bảng {name} đã tồn tại")
        if not columns or any(t not in TYPES.values() for t in columns.values()):
            raise DBError(f"kiểu cột phải là một trong {list(TYPES)}")
        self._tables[name] = Table(name, dict(columns))
        self.save(name)
        return self._tables[name]

    def table(self, name: str) -> Table:
        if name not in self._tables:
            self._tables[name] = self._load(name)
        return self._tables[name]

    def _load(self, name: str) -> Table:
        path = self._path(name)
        if not path.exists():
            raise DBError(f"không có bảng {name}")
        with path.open(encoding="utf-8") as f:
            header = f.readline().rstrip("\n").split(SEP)
            columns = {}
            for spec in header:
                col, _, kind = spec.partition(":")
                if kind not in TYPES:
                    raise DBError(f"{path.name}: cột '{spec}' thiếu kiểu hợp lệ (int/float/str)")
                columns[col] = TYPES[kind]
            table = Table(name, columns)
            names = list(columns)
            for lineno, line in enumerate(f, start=2):
                cells = line.rstrip("\n").split(SEP)
                if len(cells) != len(names):
                    raise DBError(f"{path.name}:{lineno}: có {len(cells)} cột, cần {len(names)}")
                table.rows.append({c: table.convert(c, v) for c, v in zip(names, cells)})
        return table

    def save(self, name: str) -> None:
        """Ghi file tạm rồi đổi tên, để file cũ không bao giờ bị ghi dở."""
        table = self._tables[name]
        type_name = {t: n for n, t in TYPES.items()}
        lines = [SEP.join(f"{c}:{type_name[t]}" for c, t in table.columns.items())]
        lines += [SEP.join("" if r[c] is None else str(r[c]) for c in table.columns) for r in table.rows]
        self.data_dir.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.data_dir, prefix=f".{name}.")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            os.replace(tmp, self._path(name))
        except BaseException:
            os.unlink(tmp)
            raise


@dataclass(frozen=True)
class DBQuery:
    """Bộ dựng câu truy vấn. Mỗi method trả về một DBQuery mới, không sửa đối tượng cũ,
    nên có thể tái sử dụng một truy vấn dở dang mà không sợ điều kiện cũ còn sót lại."""

    db: Database
    table_name: str | None = None
    columns: tuple[str, ...] | None = None
    conditions: tuple[tuple[str, str, Any], ...] = ()

    # --- các bước dựng truy vấn ---
    def from_(self, table_name: str) -> DBQuery:
        return replace(self, table_name=table_name)

    def select(self, columns: list[str] | str) -> DBQuery:
        return replace(self, columns=(columns,) if isinstance(columns, str) else tuple(columns))

    def where(self, column: str, value: Any, op: str = "=") -> DBQuery:
        """Thêm điều kiện; gọi nhiều lần thì các điều kiện nối bằng AND."""
        if op not in OPERATORS:
            raise DBError(f"toán tử '{op}' không hỗ trợ, dùng một trong {list(OPERATORS)}")
        return replace(self, conditions=(*self.conditions, (column, op, value)))

    # --- thực thi ---
    def get(self) -> list[Row]:
        table = self._table(self.table_name)
        columns = list(self.columns or table.columns)
        for c in columns:
            table.require(c)
        return [{c: row[c] for c in columns} for row in self._matching(table)]

    def first(self) -> Row | None:
        rows = self.get()
        return rows[0] if rows else None

    def insert(self, table_name: str, data: Row) -> int:
        table = self._table(table_name)
        unknown = set(data) - set(table.columns)
        if unknown:
            raise DBError(f"bảng {table_name} không có cột {sorted(unknown)}")
        row = {c: table.convert(c, data.get(c)) for c in table.columns}
        if "id" in table.columns:
            if row["id"] is None:
                raise DBError("thiếu id")
            if any(r["id"] == row["id"] for r in table.rows):
                raise DBError(f"{table_name} id={row['id']} đã tồn tại")
        table.rows.append(row)
        self.db.save(table_name)
        return 1

    def update(self, table_name: str, data: Row) -> int:
        table = self._table(table_name, need_where=True)
        changes = {c: table.convert(c, v) for c, v in data.items()}
        targets = self._matching(table)
        if "id" in changes and len(targets) > 1:
            raise DBError("không thể đặt cùng một id cho nhiều dòng")
        if "id" in changes and targets and any(
                r["id"] == changes["id"] and r is not targets[0] for r in table.rows):
            raise DBError(f"{table_name} id={changes['id']} đã tồn tại")
        for row in targets:
            row.update(changes)
        if targets:
            self.db.save(table_name)
        return len(targets)

    def delete(self, table_name: str) -> int:
        table = self._table(table_name, need_where=True)
        targets = {id(r) for r in self._matching(table)}
        if targets:
            table.rows = [r for r in table.rows if id(r) not in targets]
            self.db.save(table_name)
        return len(targets)

    # --- nội bộ ---
    def _table(self, table_name: str | None, need_where: bool = False) -> Table:
        if table_name is None:
            raise DBError("chưa chọn bảng, gọi from_(tên bảng) trước get()")
        if self.table_name not in (None, table_name):
            raise DBError(f"from_('{self.table_name}') khác với bảng '{table_name}'")
        if need_where and not self.conditions:
            # Chặn lỗi kinh điển "UPDATE/DELETE quên WHERE" làm hỏng cả bảng.
            raise DBError("update/delete cần where(); muốn áp dụng cho mọi dòng thì dùng where('id', None, '!=')")
        return self.db.table(table_name)

    def _matching(self, table: Table) -> list[Row]:
        tests = []
        for column, op, value in self.conditions:
            if op == "in":
                value = {table.convert(column, v) for v in value}
            else:
                value = table.convert(column, value)
            tests.append((column, OPERATORS[op], value))
        return [r for r in table.rows if all(self._check(r[c], fn, v) for c, fn, v in tests)]

    @staticmethod
    def _check(cell: Any, fn: Callable[[Any, Any], bool], value: Any) -> bool:
        if fn in (operator.eq, operator.ne):
            return fn(cell, value)
        if cell is None:  # None không so sánh lớn/nhỏ được, coi như không khớp (giống NULL trong SQL)
            return False
        return fn(cell, value)
