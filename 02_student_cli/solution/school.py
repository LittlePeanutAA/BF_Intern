"""Nghiệp vụ quản lý lớp, sinh viên, giáo viên. Không phụ thuộc vào CLI."""
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from storage import read_table, write_table


class SchoolError(Exception):
    """Lỗi nghiệp vụ, CLI in ra cho người dùng thay vì traceback."""


@dataclass(frozen=True)
class Column:
    key: str      # tên dùng trong code và trên dòng lệnh
    title: str    # tên cột trong file
    kind: str = "text"   # text | id | ref | date | phone


@dataclass(frozen=True)
class Entity:
    name: str
    file: str
    columns: tuple[Column, ...]

    @property
    def header(self) -> list[str]:
        return [c.title for c in self.columns]

    @property
    def keys(self) -> list[str]:
        return [c.key for c in self.columns]


PERSON = (Column("name", "Name"), Column("birthday", "Birthday", "date"), Column("phone", "Phone Number", "phone"))
ENTITIES = {
    "class": Entity("class", "Class.txt", (Column("id", "ID", "id"), Column("class_name", "Class Name"))),
    "student": Entity("student", "Student.txt", (Column("id", "ID", "id"), *PERSON, Column("class_id", "Class ID", "ref"))),
    "teacher": Entity("teacher", "Teacher.txt", (Column("id", "ID", "id"), *PERSON, Column("head_of_class", "Head Of Class", "ref"))),
}
PHONE = re.compile(r"0\d{9}")


def normalize(column: Column, value: str, required: bool) -> str:
    """Kiểm tra và chuẩn hoá một giá trị trước khi ghi vào file."""
    value = value.strip()
    if "|" in value or "\n" in value:
        raise SchoolError(f"{column.key}: không được chứa '|' hoặc xuống dòng")
    if not value:
        if required:
            raise SchoolError(f"{column.key}: không được để trống")
        return ""
    if column.kind in ("id", "ref"):
        if not value.isdigit() or int(value) <= 0:
            raise SchoolError(f"{column.key}: phải là số nguyên dương, nhận '{value}'")
        return str(int(value))  # "007" -> "7" để so sánh ID nhất quán
    if column.kind == "date":
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            raise SchoolError(f"{column.key}: cần dạng YYYY-MM-DD, nhận '{value}'") from None
    if column.kind == "phone" and not PHONE.fullmatch(value):
        raise SchoolError(f"{column.key}: cần 10 chữ số bắt đầu bằng 0, nhận '{value}'")
    return value


class School:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

    # --- đọc / ghi ---
    def rows(self, entity: str) -> list[dict[str, str]]:
        e = ENTITIES[entity]
        return [dict(zip(e.keys, r)) for r in read_table(self.data_dir / e.file, e.header)]

    def _save(self, entity: str, rows: list[dict[str, str]]) -> None:
        e = ENTITIES[entity]
        rows = sorted(rows, key=lambda r: int(r["id"]))
        write_table(self.data_dir / e.file, e.header, [[r[k] for k in e.keys] for r in rows])

    def _find(self, rows: list[dict[str, str]], entity: str, id_: str) -> dict[str, str]:
        for r in rows:
            if r["id"] == id_:
                return r
        raise SchoolError(f"không có {entity} với id={id_}")

    # --- ràng buộc giữa các bảng ---
    def _check_references(self, entity: str, row: dict[str, str]) -> None:
        class_ids = {r["id"] for r in self.rows("class")}
        if entity == "student" and row["class_id"] not in class_ids:
            raise SchoolError(f"lớp id={row['class_id']} không tồn tại")
        if entity == "teacher" and row["head_of_class"]:
            if row["head_of_class"] not in class_ids:
                raise SchoolError(f"lớp id={row['head_of_class']} không tồn tại")
            for t in self.rows("teacher"):
                if t["head_of_class"] == row["head_of_class"] and t["id"] != row["id"]:
                    raise SchoolError(f"lớp id={row['head_of_class']} đã có chủ nhiệm (giáo viên id={t['id']})")

    # --- thao tác ---
    def add(self, entity: str, values: dict[str, str]) -> dict[str, str]:
        e = ENTITIES[entity]
        row = {c.key: normalize(c, values.get(c.key) or "", required=c.key != "head_of_class") for c in e.columns}
        rows = self.rows(entity)
        if any(r["id"] == row["id"] for r in rows):
            raise SchoolError(f"{entity} id={row['id']} đã tồn tại")
        self._check_references(entity, row)
        self._save(entity, [*rows, row])
        return row

    def edit(self, entity: str, id_: str, changes: dict[str, str]) -> dict[str, str]:
        e = ENTITIES[entity]
        id_ = normalize(e.columns[0], id_, required=True)
        changes = {k: v for k, v in changes.items() if v is not None and k != "id"}
        if not changes:
            raise SchoolError("không có trường nào để sửa")
        rows = self.rows(entity)
        row = self._find(rows, entity, id_)
        for c in e.columns:
            if c.key in changes:
                row[c.key] = normalize(c, changes[c.key], required=c.key != "head_of_class")
        self._check_references(entity, row)
        self._save(entity, rows)
        return row

    def remove(self, entity: str, id_: str) -> None:
        id_ = normalize(ENTITIES[entity].columns[0], id_, required=True)
        rows = self.rows(entity)
        self._find(rows, entity, id_)
        if entity == "class":
            students = [s["id"] for s in self.rows("student") if s["class_id"] == id_]
            heads = [t["id"] for t in self.rows("teacher") if t["head_of_class"] == id_]
            if students or heads:
                raise SchoolError(f"lớp id={id_} còn sinh viên {students} / chủ nhiệm {heads}, chuyển họ đi trước")
        self._save(entity, [r for r in rows if r["id"] != id_])
