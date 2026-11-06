"""Test các method dựng và chạy truy vấn: from_, select, where, get, first."""
import pytest
from conftest import STUDENTS, ids

from minidb import DBError


class TestGet:
    def test_returns_all_rows_and_columns(self, q):
        assert q.from_("student").get() == STUDENTS

    def test_empty_table(self, db):
        from minidb import DBQuery
        assert DBQuery(db).from_("class").get() == []

    def test_requires_from(self, q):
        with pytest.raises(DBError, match="chưa chọn bảng"):
            q.get()

    def test_unknown_table(self, q):
        with pytest.raises(DBError, match="không có bảng"):
            q.from_("teacher").get()

    def test_rows_are_copies(self, q):
        """Sửa kết quả trả về không được làm hỏng dữ liệu trong bảng."""
        q.from_("student").get()[0]["name"] = "Hacker"
        assert q.from_("student").where("id", 1).first()["name"] == "An"


class TestSelect:
    def test_list_of_columns_keeps_order(self, q):
        assert q.select(["name", "id"]).from_("class").get() == [
            {"name": "K66CA", "id": 1}, {"name": "K66CB", "id": 2}]

    def test_single_column_as_string(self, q):
        assert q.select("name").from_("class").get() == [{"name": "K66CA"}, {"name": "K66CB"}]

    def test_unknown_column(self, q):
        with pytest.raises(DBError, match="không có cột 'email'"):
            q.select(["id", "email"]).from_("student").get()


class TestWhere:
    def test_example_from_assignment(self, q):
        assert q.select(["id", "name"]).where("class_id", 1).from_("student").get() == [
            {"id": 1, "name": "An"}, {"id": 2, "name": "Bình"}]

    def test_value_is_converted_to_column_type(self, q):
        assert ids(q.from_("student").where("class_id", "1").get()) == [1, 2]
        assert ids(q.from_("student").where("id", "03").get()) == [3]

    def test_value_of_wrong_type(self, q):
        with pytest.raises(DBError, match="không phải int"):
            q.from_("student").where("class_id", "một").get()

    def test_several_conditions_are_and(self, q):
        assert ids(q.from_("student").where("class_id", 1).where("gpa", 3.0, ">").get()) == [1]

    def test_no_match(self, q):
        assert q.from_("student").where("id", 99).get() == []

    @pytest.mark.parametrize("op, value, expected", [
        ("=", 2.5, [2]),
        ("!=", 2.5, [1, 3, 4]),      # None khác 2.5 nên vẫn được tính
        ("<", 3.2, [2]),
        ("<=", 3.2, [1, 2]),
        (">", 3.2, [3]),
        (">=", 3.2, [1, 3]),
        ("in", [2.5, 3.8, 9.9], [2, 3]),
    ])
    def test_operators(self, q, op, value, expected):
        assert ids(q.from_("student").where("gpa", value, op).get()) == expected

    def test_none_behaves_like_sql_null(self, q):
        assert ids(q.from_("student").where("gpa", None).get()) == [4]
        assert ids(q.from_("student").where("gpa", None, "!=").get()) == [1, 2, 3]
        assert ids(q.from_("student").where("gpa", 0, ">=").get()) == [1, 2, 3]  # NULL không >= 0

    def test_unknown_operator(self, q):
        with pytest.raises(DBError, match="toán tử 'LIKE'"):
            q.where("name", "A%", "LIKE")

    def test_unknown_column(self, q):
        with pytest.raises(DBError, match="không có cột 'age'"):
            q.from_("student").where("age", 20).get()


class TestImmutability:
    def test_builder_returns_new_query(self, q):
        students = q.from_("student")
        class1 = students.where("class_id", 1)
        assert students is not class1
        assert len(students.get()) == 4 and len(class1.get()) == 2

    def test_previous_where_does_not_leak(self, q):
        """Lỗi của bản cũ: where() của lần trước còn sót lại cho lần sau."""
        q.where("class_id", 1)   # dựng dở rồi bỏ
        assert len(q.from_("student").get()) == 4

    def test_order_of_calls_does_not_matter(self, q):
        a = q.from_("student").select("name").where("id", 1).get()
        b = q.where("id", 1).select("name").from_("student").get()
        assert a == b == [{"name": "An"}]

    def test_reusing_query_twice_gives_same_result(self, q):
        query = q.from_("student").where("class_id", 2)
        assert query.get() == query.get()


class TestFirst:
    def test_first_row(self, q):
        assert q.from_("student").where("class_id", 2).first()["id"] == 3

    def test_none_when_empty(self, q):
        assert q.from_("student").where("id", 99).first() is None
