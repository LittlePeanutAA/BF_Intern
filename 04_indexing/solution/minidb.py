"""minidb (bài 04): bài 03 + index sắp xếp để tìm kiếm bằng tìm nhị phân.

    db = Database("data")
    q = DBQuery(db)
    q.select(["id", "name"]).where("class_id", 1).from_("student").get()

Định dạng file `<bảng>.txt`: dòng đầu là `cột:kiểu|cột:kiểu|...` (kiểu int, float, str),
các dòng sau là dữ liệu ngăn cách bằng '|'. Ô rỗng là None.

    q.create_index("student", "id")   # từ giờ where("id", ...) tìm nhị phân thay vì duyệt cả bảng
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


def lower_bound(keys: list, target: Any) -> int:
    """Vị trí đầu tiên có keys[i] >= target, trên danh sách đã sắp xếp. O(log n).
    Tương đương bisect.bisect_left, viết tay để thấy rõ thuật toán."""
    lo, hi = 0, len(keys)
    while lo < hi:  # bất biến: mọi keys[< lo] < target, mọi keys[>= hi] >= target
        mid = (lo + hi) // 2
        if keys[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(keys: list, target: Any) -> int:
    """Vị trí đầu tiên có keys[i] > target (giống bisect.bisect_right)."""
    lo, hi = 0, len(keys)
    while lo < hi:
        mid = (lo + hi) // 2
        if keys[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo


class SortedIndex:
    """Index trên một cột: các giá trị đã sắp xếp tăng dần, đi kèm dòng tương ứng.

    keys = [1, 2, 3, ...]      rows = [dòng có id 1, dòng có id 2, ...]
    Tìm một giá trị chỉ cần tìm nhị phân trên keys thay vì duyệt mọi dòng.
    Dòng có giá trị None không vào index (giống phần lớn CSDL).
    """

    def __init__(self, column: str, rows: list[Row]):
        self.column = column
        pairs = sorted(((r[column], i) for i, r in enumerate(rows) if r[column] is not None))
        self.keys = [k for k, _ in pairs]
        self.rows = [rows[i] for _, i in pairs]

    def range(self, lo: Any = None, hi: Any = None, lo_open: bool = False, hi_open: bool = False) -> list[Row]:
        """Các dòng có lo <= giá trị <= hi (lo_open/hi_open đổi thành < ). None là không giới hạn."""
        start = 0 if lo is None else (upper_bound if lo_open else lower_bound)(self.keys, lo)
        end = len(self.keys) if hi is None else (lower_bound if hi_open else upper_bound)(self.keys, hi)
        return self.rows[start:end]

    def lookup(self, op: str, value: Any) -> list[Row] | None:
        """Các dòng thoả `cột op value`; None nếu index không giúp được với toán tử này."""
        if value is None:
            return None
        if op == "=":
            return self.range(value, value)
        if op == "in":
            return [r for v in sorted(set(value) - {None}) for r in self.range(v, v)]
        bounds = {"<": dict(hi=value, hi_open=True), "<=": dict(hi=value),
                  ">": dict(lo=value, lo_open=True), ">=": dict(lo=value)}
        return self.range(**bounds[op]) if op in bounds else None


@dataclass
class Table:
    name: str
    columns: dict[str, type]
    rows: list[Row] = field(default_factory=list)
    indexed: set[str] = field(default_factory=set)      # các cột đã create_index
    _indexes: dict[str, SortedIndex] = field(default_factory=dict, repr=False)

    def index(self, column: str) -> SortedIndex | None:
        """Index của cột (dựng lại nếu dữ liệu đã đổi); None nếu cột chưa được đánh index."""
        if column not in self.indexed:
            return None
        if column not in self._indexes:
            self._indexes[column] = SortedIndex(column, self.rows)
        return self._indexes[column]

    def changed(self) -> None:
        """Gọi sau mỗi lần sửa dữ liệu: bỏ index cũ, lần truy vấn sau sẽ dựng lại.
        Đơn giản và luôn đúng; đổi lại mỗi lần ghi tốn O(n log n) ở lần đọc kế tiếp."""
        self._indexes.clear()

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
            if DBQuery(self.db).from_(table_name).where("id", row["id"]).first():
                raise DBError(f"{table_name} id={row['id']} đã tồn tại")
        table.rows.append(row)
        table.changed()
        self.db.save(table_name)
        return 1

    def insert_many(self, table_name: str, data: list[Row]) -> int:
        """Thêm nhiều dòng rồi ghi file một lần; nhanh hơn rất nhiều so với gọi insert() n lần."""
        table = self._table(table_name)
        rows = []
        for item in data:
            unknown = set(item) - set(table.columns)
            if unknown:
                raise DBError(f"bảng {table_name} không có cột {sorted(unknown)}")
            rows.append({c: table.convert(c, item.get(c)) for c in table.columns})
        if "id" in table.columns:
            ids = [r["id"] for r in rows]
            if None in ids:
                raise DBError("thiếu id")
            existing = {r["id"] for r in table.rows}
            if len(set(ids)) != len(ids) or existing.intersection(ids):
                raise DBError("id bị trùng")
        table.rows.extend(rows)
        table.changed()
        self.db.save(table_name)
        return len(rows)

    def create_index(self, table_name: str, column: str) -> None:
        """Đánh index cho một cột; các truy vấn where() trên cột đó sẽ dùng tìm nhị phân."""
        table = self._table(table_name)
        table.require(column)
        table.indexed.add(column)
        table.index(column)  # dựng ngay để thời gian dựng không tính vào truy vấn đầu tiên

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
            table.changed()
            self.db.save(table_name)
        return len(targets)

    def delete(self, table_name: str) -> int:
        table = self._table(table_name, need_where=True)
        targets = {id(r) for r in self._matching(table)}
        if targets:
            table.rows = [r for r in table.rows if id(r) not in targets]
            table.changed()
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
            tests.append((column, op, value))
        # Nếu có điều kiện trên cột đã đánh index: lấy ứng viên bằng tìm nhị phân,
        # rồi chỉ kiểm tra các điều kiện còn lại trên số ít ứng viên đó.
        candidates = table.rows
        for column, op, value in tests:
            index = table.index(column)
            found = index.lookup(op, value) if index else None
            if found is not None:
                candidates = found
                break
        checks = [(c, OPERATORS[op], v) for c, op, v in tests]
        return [r for r in candidates if all(self._check(r[c], fn, v) for c, fn, v in checks)]

    @staticmethod
    def _check(cell: Any, fn: Callable[[Any, Any], bool], value: Any) -> bool:
        if fn in (operator.eq, operator.ne):
            return fn(cell, value)
        if cell is None:  # None không so sánh lớn/nhỏ được, coi như không khớp (giống NULL trong SQL)
            return False
        return fn(cell, value)
