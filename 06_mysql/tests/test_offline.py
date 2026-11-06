"""Test không cần MySQL: kiểm tra dữ liệu đầu vào, đổi lỗi MySQL thành thông báo, CLI khi không kết nối được."""
from datetime import date

import pymysql
import pytest
from pymysql.constants import ER

from qlsv import main
from school import ENTITIES, SchoolError, explain, normalize

COLS = {c.key: c for e in ENTITIES.values() for c in e.columns}


def test_normalize_converts_types():
    assert normalize(COLS["id"], " 007 ", True) == 7
    assert normalize(COLS["birthday"], "2004-02-29", True) == date(2004, 2, 29)
    assert normalize(COLS["head_of_class"], "", False) is None
    # Bài 02 cấm '|': với MySQL thì không cần nữa
    assert normalize(COLS["name"], "Nguyễn | Văn A", True) == "Nguyễn | Văn A"


@pytest.mark.parametrize("key, value, message", [
    ("id", "-1", "số nguyên dương"),
    ("birthday", "2005-02-30", "YYYY-MM-DD"),
    ("phone", "912345678", "10 chữ số"),
    ("name", "x" * 101, "dài quá 100"),
    ("class_name", "  ", "không được để trống"),
])
def test_normalize_rejects(key, value, message):
    with pytest.raises(SchoolError, match=message):
        normalize(COLS[key], value, True)


@pytest.mark.parametrize("code, text, row, expected", [
    (ER.DUP_ENTRY, "Duplicate entry '3' for key 'students.PRIMARY'", {"id": 3}, "student id=3 đã tồn tại"),
    (ER.DUP_ENTRY, "Duplicate entry '1' for key 'teachers.one_head_per_class'", {"id": 9, "head_of_class": 1},
     "lớp id=1 đã có chủ nhiệm"),
    (ER.NO_REFERENCED_ROW_2, "Cannot add or update a child row", {"class_id": 99}, "lớp id=99 không tồn tại"),
    (ER.ROW_IS_REFERENCED_2, "Cannot delete or update a parent row", {"id": 1}, "còn sinh viên"),
])
def test_explain(code, text, row, expected):
    entity = "student"
    assert expected in str(explain(pymysql.err.IntegrityError(code, text), entity, row))


def test_cli_reports_connection_failure(capsys):
    # Cổng 1 không có MySQL nào: CLI phải báo lỗi gọn, mã thoát 2, không traceback
    assert main(["--db", "mysql://u:p@127.0.0.1:1/qlsv", "list_class"]) == 2
    assert "không kết nối được MySQL" in capsys.readouterr().err


def test_cli_rejects_bad_input_before_touching_db(capsys):
    class NoDB:
        def cursor(self):
            raise AssertionError("không được chạm vào DB khi dữ liệu sai")

    assert main(["add_class", "--id", "abc", "--class_name", "K1"], conn=NoDB()) == 1
    assert "số nguyên dương" in capsys.readouterr().err
