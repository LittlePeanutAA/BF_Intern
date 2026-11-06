"""Test các thao tác ghi: insert, update, delete, và việc dữ liệu được lưu xuống file."""
import pytest
from conftest import ids

from minidb import Database, DBError, DBQuery


class TestInsert:
    def test_example_from_assignment(self, db):
        q = DBQuery(db)
        status = q.insert("class", {"id": 1, "name": "Class 1"})
        assert status == 1
        assert q.where("id", 1).from_("class").select("id").get() == [{"id": 1}]

    def test_missing_columns_become_none(self, q):
        q.insert("student", {"id": 5, "name": "Em", "class_id": 1})
        assert q.from_("student").where("id", 5).first()["gpa"] is None

    def test_values_are_converted(self, q):
        q.insert("student", {"id": "5", "name": "Em", "gpa": "3.5", "class_id": "1"})
        assert q.from_("student").where("id", 5).first() == {"id": 5, "name": "Em", "gpa": 3.5, "class_id": 1}

    @pytest.mark.parametrize("row, message", [
        ({"id": 1, "name": "Trùng"}, "đã tồn tại"),
        ({"name": "Không id"}, "thiếu id"),
        ({"id": 9, "email": "a@b.c"}, "không có cột"),
        ({"id": "chín"}, "không phải int"),
        ({"id": 9, "gpa": "cao"}, "không phải float"),
        ({"id": 9, "name": "A|B"}, "không được chứa"),
        ({"id": 9, "name": "dòng 1\ndòng 2"}, "không được chứa"),
    ])
    def test_rejects_invalid_rows(self, q, row, message):
        with pytest.raises(DBError, match=message):
            q.insert("student", row)
        assert ids(q.from_("student").get()) == [1, 2, 3, 4]  # bảng không đổi

    def test_from_must_match_table(self, q):
        with pytest.raises(DBError, match="khác với bảng"):
            q.from_("class").insert("student", {"id": 9})

    def test_table_without_id_allows_duplicates(self, db):
        db.create_table("log", {"message": str})
        q = DBQuery(db)
        assert q.insert("log", {"message": "hi"}) == q.insert("log", {"message": "hi"}) == 1
        assert len(q.from_("log").get()) == 2


class TestUpdate:
    def test_updates_matching_rows_and_returns_count(self, q):
        assert q.from_("student").where("class_id", 1).update("student", {"gpa": 4.0}) == 2
        assert [r["gpa"] for r in q.from_("student").get()] == [4.0, 4.0, 3.8, None]

    def test_where_without_from(self, q):
        assert q.where("id", 3).update("student", {"name": "Cường mới"}) == 1
        assert q.from_("student").where("id", 3).first()["name"] == "Cường mới"

    def test_no_match_returns_zero(self, q):
        assert q.where("id", 99).update("student", {"name": "X"}) == 0

    def test_requires_where(self, q):
        with pytest.raises(DBError, match="cần where"):
            q.update("student", {"gpa": 0})
        assert q.from_("student").where("id", 1).first()["gpa"] == 3.2

    def test_explicit_update_all(self, q):
        assert q.where("id", None, "!=").update("student", {"gpa": 1.0}) == 4

    def test_change_id(self, q):
        assert q.where("id", 4).update("student", {"id": 40}) == 1
        assert ids(q.from_("student").get()) == [1, 2, 3, 40]

    def test_cannot_change_id_to_existing_one(self, q):
        with pytest.raises(DBError, match="đã tồn tại"):
            q.where("id", 4).update("student", {"id": 1})

    def test_cannot_give_same_id_to_many_rows(self, q):
        with pytest.raises(DBError, match="nhiều dòng"):
            q.where("class_id", 1).update("student", {"id": 9})

    def test_invalid_value_changes_nothing(self, q):
        with pytest.raises(DBError):
            q.where("id", 1).update("student", {"name": "Mới", "gpa": "cao"})
        assert q.from_("student").where("id", 1).first()["name"] == "An"


class TestDelete:
    def test_deletes_matching_rows_and_returns_count(self, q):
        assert q.where("class_id", 2).delete("student") == 2
        assert ids(q.from_("student").get()) == [1, 2]

    def test_no_match_returns_zero(self, q):
        assert q.where("id", 99).delete("student") == 0

    def test_requires_where(self, q):
        with pytest.raises(DBError, match="cần where"):
            q.delete("student")
        assert len(q.from_("student").get()) == 4

    def test_from_must_match_table(self, q):
        with pytest.raises(DBError, match="khác với bảng"):
            q.from_("class").where("id", 1).delete("student")


class TestPersistence:
    """Dữ liệu phải còn nguyên khi mở lại CSDL từ file (giả lập chạy lại chương trình)."""

    def test_reload_after_writes(self, q, db):
        q.insert("student", {"id": 5, "name": "Em", "gpa": 2.0, "class_id": 2})
        q.where("id", 1).update("student", {"gpa": 3.3})
        q.where("id", 2).delete("student")
        reloaded = DBQuery(Database(db.data_dir)).from_("student").get()
        assert reloaded == q.from_("student").get()

    def test_file_format(self, q, db):
        lines = (db.data_dir / "student.txt").read_text(encoding="utf-8").splitlines()
        assert lines[0] == "id:int|name:str|gpa:float|class_id:int"
        assert lines[4] == "4|Dung||2"  # None ghi thành ô rỗng

    def test_failed_write_keeps_old_file(self, q, db, monkeypatch):
        """Giả lập lỗi đúng lúc đổi tên file: file cũ còn nguyên, không sót file tạm."""
        before = (db.data_dir / "class.txt").read_text(encoding="utf-8")

        def broken_replace(*args):
            raise OSError("đĩa đầy")

        monkeypatch.setattr("minidb.os.replace", broken_replace)
        with pytest.raises(OSError):
            q.insert("class", {"id": 3, "name": "K66CC"})
        assert (db.data_dir / "class.txt").read_text(encoding="utf-8") == before
        assert sorted(p.name for p in db.data_dir.iterdir()) == ["class.txt", "student.txt"]


class TestDatabase:
    def test_create_existing_table(self, db):
        with pytest.raises(DBError, match="đã tồn tại"):
            db.create_table("class", {"id": int})

    def test_create_table_with_bad_type(self, db):
        with pytest.raises(DBError, match="kiểu cột"):
            db.create_table("t", {"id": list})

    @pytest.mark.parametrize("content, message", [
        ("id|name\n", "thiếu kiểu"),
        ("id:int|name:str\n1|A|thừa\n", "có 3 cột"),
        ("id:int|name:str\nx|A\n", "không phải int"),
    ])
    def test_corrupted_files(self, tmp_path, content, message):
        (tmp_path / "t.txt").write_text(content, encoding="utf-8")
        with pytest.raises(DBError, match=message):
            DBQuery(Database(tmp_path)).from_("t").get()
