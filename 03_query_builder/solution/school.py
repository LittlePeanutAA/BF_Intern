"""Nghiệp vụ quản lý lớp, sinh viên, giáo viên, viết lại trên minidb.DBQuery.

So với bài 02: không còn đọc/ghi file ở đây. Kiểu dữ liệu (int, str) do minidb lo,
file này chỉ giữ các quy tắc nghiệp vụ (ngày sinh, số điện thoại, ràng buộc giữa các bảng).
"""
import re
from datetime import date
from pathlib import Path

from minidb import Database, DBError, DBQuery

SCHEMA = {
    "class": {"id": int, "class_name": str},
    "student": {"id": int, "name": str, "birthday": str, "phone": str, "class_id": int},
    "teacher": {"id": int, "name": str, "birthday": str, "phone": str, "head_of_class": int},
}
OPTIONAL = {"head_of_class"}
PHONE = re.compile(r"0\d{9}")


class SchoolError(Exception):
    """Lỗi nghiệp vụ, CLI in ra cho người dùng thay vì traceback."""


def validate(values: dict[str, str | None]) -> dict[str, str | None]:
    out = {}
    for key, value in values.items():
        value = None if value is None else value.strip() or None
        if value is None and key not in OPTIONAL:
            raise SchoolError(f"{key}: không được để trống")
        if value is not None and key == "birthday":
            try:
                value = date.fromisoformat(value).isoformat()
            except ValueError:
                raise SchoolError(f"birthday: cần dạng YYYY-MM-DD, nhận '{value}'") from None
        if value is not None and key == "phone" and not PHONE.fullmatch(value):
            raise SchoolError(f"phone: cần 10 chữ số bắt đầu bằng 0, nhận '{value}'")
        out[key] = value
    return out


class School:
    def __init__(self, data_dir: Path):
        self.db = Database(data_dir)
        for name, columns in SCHEMA.items():
            if not self.db.has_table(name):
                self.db.create_table(name, columns)
        self.q = DBQuery(self.db)

    def rows(self, entity: str, **where) -> list[dict]:
        query = self.q.from_(entity)
        for column, value in where.items():
            query = query.where(column, value)
        return query.get()

    def _exists(self, entity: str, id_) -> bool:
        return self.q.from_(entity).where("id", id_).first() is not None

    def _check_references(self, entity: str, row: dict) -> None:
        if entity == "student" and not self._exists("class", row["class_id"]):
            raise SchoolError(f"lớp id={row['class_id']} không tồn tại")
        if entity == "teacher" and row.get("head_of_class") is not None:
            if not self._exists("class", row["head_of_class"]):
                raise SchoolError(f"lớp id={row['head_of_class']} không tồn tại")
            head = self.q.from_("teacher").where("head_of_class", row["head_of_class"]).where("id", row["id"], "!=").first()
            if head:
                raise SchoolError(f"lớp id={row['head_of_class']} đã có chủ nhiệm (giáo viên id={head['id']})")

    def add(self, entity: str, values: dict[str, str | None]) -> dict:
        row = validate({k: values.get(k) for k in SCHEMA[entity]})
        try:
            row = {k: self.db.table(entity).convert(k, v) for k, v in row.items()}
            self._check_references(entity, row)
            self.q.insert(entity, row)
        except DBError as e:
            raise SchoolError(str(e)) from None
        return row

    def edit(self, entity: str, id_: str, changes: dict[str, str | None]) -> dict:
        changes = validate({k: v for k, v in changes.items() if v is not None and k != "id"})
        if not changes:
            raise SchoolError("không có trường nào để sửa")
        try:
            target = self.q.from_(entity).where("id", id_)
            row = target.first()
            if row is None:
                raise SchoolError(f"không có {entity} với id={id_}")
            row.update({k: self.db.table(entity).convert(k, v) for k, v in changes.items()})
            self._check_references(entity, row)
            target.update(entity, changes)
        except DBError as e:
            raise SchoolError(str(e)) from None
        return row

    def remove(self, entity: str, id_: str) -> None:
        try:
            target = self.q.from_(entity).where("id", id_)
            if target.first() is None:
                raise SchoolError(f"không có {entity} với id={id_}")
            if entity == "class":
                students = [r["id"] for r in self.rows("student", class_id=id_)]
                heads = [r["id"] for r in self.rows("teacher", head_of_class=id_)]
                if students or heads:
                    raise SchoolError(f"lớp id={id_} còn sinh viên {students} / chủ nhiệm {heads}, chuyển họ đi trước")
            target.delete(entity)
        except DBError as e:
            raise SchoolError(str(e)) from None
