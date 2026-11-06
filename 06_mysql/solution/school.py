"""Nghiệp vụ quản lý lớp, sinh viên, giáo viên, lưu trên MySQL. Cùng giao diện với School của bài 02."""
import os
import re
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from urllib.parse import unquote, urlparse

import pymysql
from pymysql.constants import CLIENT, ER

DEFAULT_URL = "mysql://qlsv:qlsv@127.0.0.1:3306/qlsv"


class SchoolError(Exception):
    """Lỗi nghiệp vụ, CLI in ra cho người dùng thay vì traceback."""


@dataclass(frozen=True)
class Column:
    key: str      # tên cột trong bảng, cũng là tên tham số dòng lệnh
    title: str    # tiêu đề khi in bảng
    kind: str = "text"   # text | id | ref | date | phone


@dataclass(frozen=True)
class Entity:
    name: str
    table: str
    columns: tuple[Column, ...]

    @property
    def keys(self) -> list[str]:
        return [c.key for c in self.columns]

    @property
    def header(self) -> list[str]:
        return [c.title for c in self.columns]


PERSON = (Column("name", "Name"), Column("birthday", "Birthday", "date"), Column("phone", "Phone Number", "phone"))
ENTITIES = {
    "class": Entity("class", "classes", (Column("id", "ID", "id"), Column("class_name", "Class Name"))),
    "student": Entity("student", "students", (Column("id", "ID", "id"), *PERSON, Column("class_id", "Class ID", "ref"))),
    "teacher": Entity("teacher", "teachers", (Column("id", "ID", "id"), *PERSON,
                                              Column("head_of_class", "Head Of Class", "ref"))),
}
PHONE = re.compile(r"0\d{9}")
MAX_LENGTH = {"class_name": 50, "name": 100}


def normalize(column: Column, value: str, required: bool):
    """Kiểm tra và đổi giá trị dòng lệnh sang kiểu của cột. Trả None cho ô trống không bắt buộc.

    Không còn cấm ký tự '|' và xuống dòng như bài 02: đó là giới hạn của định dạng file,
    không phải của dữ liệu. Với tham số SQL, tên chứa bất kỳ ký tự nào cũng lưu được an toàn.
    """
    value = value.strip()
    if not value:
        if required:
            raise SchoolError(f"{column.key}: không được để trống")
        return None
    if column.kind in ("id", "ref"):
        if not value.isdigit() or int(value) <= 0:
            raise SchoolError(f"{column.key}: phải là số nguyên dương, nhận '{value}'")
        return int(value)
    if column.kind == "date":
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise SchoolError(f"{column.key}: cần dạng YYYY-MM-DD, nhận '{value}'") from None
    if column.kind == "phone" and not PHONE.fullmatch(value):
        raise SchoolError(f"{column.key}: cần 10 chữ số bắt đầu bằng 0, nhận '{value}'")
    if len(value) > MAX_LENGTH.get(column.key, 255):
        raise SchoolError(f"{column.key}: dài quá {MAX_LENGTH[column.key]} ký tự")
    return value


def connect(url: str | None = None) -> pymysql.connections.Connection:
    """Kết nối theo URL dạng mysql://user:password@host:port/database (mặc định lấy từ QLSV_DB_URL)."""
    u = urlparse(url or os.environ.get("QLSV_DB_URL", DEFAULT_URL))
    return pymysql.connect(
        host=u.hostname or "127.0.0.1", port=u.port or 3306,
        user=unquote(u.username or ""), password=unquote(u.password or ""), database=u.path.lstrip("/"),
        charset="utf8mb4", autocommit=False, cursorclass=pymysql.cursors.DictCursor,
        # Mặc định MySQL trả rowcount = số dòng THỰC SỰ thay đổi: UPDATE ghi đè giá trị y hệt sẽ ra 0,
        # trông như "không tìm thấy". FOUND_ROWS đổi thành số dòng khớp điều kiện WHERE.
        client_flag=CLIENT.FOUND_ROWS,
    )


def explain(error: pymysql.err.MySQLError, entity: str, row: dict) -> SchoolError:
    """Đổi lỗi ràng buộc của MySQL thành thông báo cho người dùng."""
    code = error.args[0]
    message = str(error.args[1]) if len(error.args) > 1 else ""
    if code == ER.DUP_ENTRY:
        if "one_head_per_class" in message:
            return SchoolError(f"lớp id={row.get('head_of_class')} đã có chủ nhiệm")
        return SchoolError(f"{entity} id={row.get('id')} đã tồn tại")
    if code == ER.NO_REFERENCED_ROW_2:
        ref = row.get("class_id") or row.get("head_of_class")
        return SchoolError(f"lớp id={ref} không tồn tại")
    if code == ER.ROW_IS_REFERENCED_2:
        return SchoolError(f"lớp id={row.get('id')} còn sinh viên hoặc giáo viên chủ nhiệm, chuyển họ đi trước")
    if code == ER.CHECK_CONSTRAINT_VIOLATED:
        return SchoolError(f"dữ liệu vi phạm ràng buộc: {message}")
    return SchoolError(f"lỗi cơ sở dữ liệu ({code}): {message}")


class School:
    def __init__(self, conn: pymysql.connections.Connection):
        self.conn = conn

    @contextmanager
    def _transaction(self, entity: str, row: dict):
        """Mọi thay đổi của một lệnh nằm trong một transaction: lỗi giữa chừng thì không ghi gì cả."""
        try:
            with self.conn.cursor() as cur:
                yield cur
            self.conn.commit()
        except pymysql.err.IntegrityError as e:
            self.conn.rollback()
            raise explain(e, entity, row) from None
        except pymysql.err.OperationalError as e:
            self.conn.rollback()
            if e.args[0] == ER.CHECK_CONSTRAINT_VIOLATED:
                raise explain(e, entity, row) from None
            raise
        except BaseException:
            self.conn.rollback()
            raise

    def rows(self, entity: str, class_id: int | None = None) -> list[dict]:
        e = ENTITIES[entity]
        # Tên bảng và tên cột lấy từ ENTITIES (do code định nghĩa), không bao giờ từ input người dùng.
        # Chỉ GIÁ TRỊ mới được truyền qua tham số %s.
        sql = f"SELECT {', '.join(e.keys)} FROM {e.table}"
        params: tuple = ()
        if class_id is not None:
            sql += " WHERE class_id = %s"
            params = (class_id,)
        with self.conn.cursor() as cur:
            cur.execute(sql + " ORDER BY id", params)
            result = cur.fetchall()
        self.conn.commit()  # kết thúc transaction đọc, để lần đọc sau thấy dữ liệu mới
        return list(result)

    def add(self, entity: str, values: dict[str, str]) -> dict:
        e = ENTITIES[entity]
        row = {c.key: normalize(c, values.get(c.key) or "", required=c.key != "head_of_class") for c in e.columns}
        sql = f"INSERT INTO {e.table} ({', '.join(row)}) VALUES ({', '.join(['%s'] * len(row))})"
        with self._transaction(entity, row) as cur:
            cur.execute(sql, tuple(row.values()))
        return row

    def edit(self, entity: str, id_: str, changes: dict[str, str | None]) -> dict:
        e = ENTITIES[entity]
        key = normalize(e.columns[0], id_, required=True)
        columns = {c.key: c for c in e.columns}
        updates = {k: normalize(columns[k], v, required=k != "head_of_class")
                   for k, v in changes.items() if v is not None and k != "id"}
        if not updates:
            raise SchoolError("không có trường nào để sửa")
        sql = f"UPDATE {e.table} SET {', '.join(f'{k} = %s' for k in updates)} WHERE id = %s"
        with self._transaction(entity, {"id": key, **updates}) as cur:
            if cur.execute(sql, (*updates.values(), key)) == 0:
                raise SchoolError(f"không có {entity} với id={key}")
            cur.execute(f"SELECT {', '.join(e.keys)} FROM {e.table} WHERE id = %s", (key,))
            return cur.fetchone()

    def remove(self, entity: str, id_: str) -> None:
        e = ENTITIES[entity]
        key = normalize(e.columns[0], id_, required=True)
        with self._transaction(entity, {"id": key}) as cur:
            if cur.execute(f"DELETE FROM {e.table} WHERE id = %s", (key,)) == 0:
                raise SchoolError(f"không có {entity} với id={key}")
