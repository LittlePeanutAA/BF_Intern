"""Fixture dùng chung. Code được test là minidb của bài 03, không chép sang đây."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "03_query_builder" / "solution"))

from minidb import Database, DBQuery  # noqa: E402

SCHEMA = {
    "class": {"id": int, "name": str},
    "student": {"id": int, "name": str, "gpa": float, "class_id": int},
}
CLASSES = [{"id": 1, "name": "K66CA"}, {"id": 2, "name": "K66CB"}]
STUDENTS = [
    {"id": 1, "name": "An", "gpa": 3.2, "class_id": 1},
    {"id": 2, "name": "Bình", "gpa": 2.5, "class_id": 1},
    {"id": 3, "name": "Cường", "gpa": 3.8, "class_id": 2},
    {"id": 4, "name": "Dung", "gpa": None, "class_id": 2},  # chưa có điểm
]


@pytest.fixture
def db(tmp_path) -> Database:
    """CSDL mới trong thư mục tạm cho mỗi test: các test không ảnh hưởng nhau."""
    database = Database(tmp_path)
    for name, columns in SCHEMA.items():
        database.create_table(name, columns)
    return database


@pytest.fixture
def q(db) -> DBQuery:
    query = DBQuery(db)
    for row in CLASSES:
        query.insert("class", row)
    for row in STUDENTS:
        query.insert("student", row)
    return query


def ids(rows):
    return [r["id"] for r in rows]
