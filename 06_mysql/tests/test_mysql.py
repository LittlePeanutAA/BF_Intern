"""Test tích hợp trên MySQL thật. Mỗi test chạy trên một database sạch đã nạp sample_data.

    docker compose up -d
    QLSV_TEST_DB_URL=mysql://root:root@127.0.0.1:3306/qlsv_test pytest -q

CẢNH BÁO: database trong QLSV_TEST_DB_URL bị xoá sạch và tạo lại ở mỗi test.
"""
import os
import re
from pathlib import Path

import pymysql
import pytest

from import_txt import import_dir
from qlsv import main
from school import School, SchoolError, connect

URL = os.environ.get("QLSV_TEST_DB_URL")
ROOT = Path(__file__).parents[1]
pytestmark = pytest.mark.skipif(not URL, reason="đặt QLSV_TEST_DB_URL để chạy test trên MySQL")


def schema_statements() -> list[str]:
    sql = re.sub(r"--[^\n]*", "", (ROOT / "schema.sql").read_text(encoding="utf-8"))
    return [s.strip() for s in sql.split(";") if s.strip()]


@pytest.fixture
def conn():
    database = URL.rsplit("/", 1)[1]
    admin = connect(URL.rsplit("/", 1)[0] + "/")
    with admin.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS `{database}`")
        cur.execute(f"CREATE DATABASE `{database}` CHARACTER SET utf8mb4")
    admin.close()
    c = connect(URL)
    with c.cursor() as cur:
        for statement in schema_statements():
            cur.execute(statement)
    c.commit()
    import_dir(School(c), ROOT / "sample_data")
    yield c
    c.close()


@pytest.fixture
def run(conn, capsys):
    def _run(*argv):
        code = main(list(argv), conn=conn)
        out, err = capsys.readouterr()
        return code, out, err
    return _run


def count(conn, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS n FROM {table}")
        n = cur.fetchone()["n"]
    conn.commit()
    return n


def test_import_and_list_by_class(run):
    code, out, _ = run("list_student", "--class_id", "1")
    assert code == 0
    assert "Nguyễn Văn An" in out and "Trần Thị Bình" in out and "Lê Hoàng Cường" not in out
    assert "(2 dòng)" in out


def test_add_edit_remove(run, conn):
    assert run("add_class", "--id", "4", "--class_name", "K67CA")[0] == 0
    assert run("edit_class", "--id", "4", "--class_name", "K67CB")[0] == 0
    assert "K67CB" in run("list_class")[1]
    assert run("remove_class", "--id", "4")[0] == 0
    assert count(conn, "classes") == 3


def test_edit_only_given_fields_and_unchanged_value_is_not_not_found(run):
    assert run("edit_student", "--id", "1", "--phone", "0999999999")[0] == 0
    # Ghi lại đúng giá trị cũ: nhờ CLIENT.FOUND_ROWS, không bị báo nhầm "không có student"
    code, out, err = run("edit_student", "--id", "1", "--phone", "0999999999")
    assert code == 0, err
    assert "'name': 'Nguyễn Văn An'" in out and "'phone': '0999999999'" in out


@pytest.mark.parametrize("argv, message", [
    (["add_class", "--id", "1", "--class_name", "X"], "class id=1 đã tồn tại"),
    (["add_student", "--id", "9", "--name", "A", "--birthday", "2004-01-01", "--phone", "0912000009",
      "--class_id", "99"], "lớp id=99 không tồn tại"),
    (["add_teacher", "--id", "9", "--name", "B", "--birthday", "1980-01-01", "--phone", "0903000009",
      "--head_of_class", "1"], "lớp id=1 đã có chủ nhiệm"),
    (["edit_teacher", "--id", "3", "--head_of_class", "2"], "lớp id=2 đã có chủ nhiệm"),
    (["remove_class", "--id", "1"], "còn sinh viên"),
    (["remove_student", "--id", "42"], "không có student với id=42"),
    (["edit_class", "--id", "42", "--class_name", "X"], "không có class với id=42"),
])
def test_constraints(run, argv, message):
    code, _, err = run(*argv)
    assert code == 1 and message in err


def test_teacher_without_class_is_allowed_many_times(run):
    for i in (10, 11):
        assert run("add_teacher", "--id", str(i), "--name", "GV", "--birthday", "1990-01-01",
                   "--phone", "0903000010")[0] == 0


def test_sql_injection_is_stored_as_plain_text(run, conn):
    evil = "x'); DROP TABLE students; --"
    assert run("add_class", "--id", "5", "--class_name", evil)[0] == 0
    assert count(conn, "students") == 4
    assert evil in run("list_class")[1]


def test_check_constraint_is_last_line_of_defense(conn):
    """Kể cả khi code Python bị bỏ qua (ghi thẳng SQL), DB vẫn chặn số điện thoại sai."""
    with pytest.raises(pymysql.err.OperationalError):
        with conn.cursor() as cur:
            cur.execute("INSERT INTO students VALUES (20, 'A', '2004-01-01', 'abcdefghij', 1)")
    conn.rollback()


def test_import_is_all_or_nothing(conn, tmp_path):
    data = tmp_path / "bad"
    data.mkdir()
    (data / "Class.txt").write_text("ID|Class Name\n10|A\n11|B\n", encoding="utf-8")
    (data / "Student.txt").write_text("ID|Name|Birthday|Phone Number|Class ID\n"
                                      "10|C|2004-01-01|0912000010|10\n"
                                      "11|D|2004-01-01|0912000011|77\n", encoding="utf-8")
    with pytest.raises(SchoolError, match="Student.txt dòng 3: lớp id=77 không tồn tại"):
        import_dir(School(conn), data)
    assert count(conn, "classes") == 3 and count(conn, "students") == 4   # lớp 10, 11 cũng không được ghi
