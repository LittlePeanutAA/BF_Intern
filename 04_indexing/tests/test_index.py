import bisect
import random

import pytest

import disk_index
from benchmark import SCHEMA, make_students
from minidb import Database, DBQuery, lower_bound, upper_bound


def test_bounds_match_bisect():
    rng = random.Random(0)
    for _ in range(500):
        keys = sorted(rng.choices(range(20), k=rng.randint(0, 30)))
        x = rng.randint(-2, 22)
        assert lower_bound(keys, x) == bisect.bisect_left(keys, x)
        assert upper_bound(keys, x) == bisect.bisect_right(keys, x)


@pytest.fixture
def q(tmp_path):
    db = Database(tmp_path)
    db.create_table("student", SCHEMA)
    query = DBQuery(db)
    query.insert_many("student", make_students(2000, seed=1))
    return query


OPS = ["=", "!=", "<", "<=", ">", ">="]


def test_index_gives_same_results_as_scan(q):
    """Kết quả có index phải giống hệt khi duyệt cả bảng, với mọi toán tử."""
    rng = random.Random(2)
    cases = [(col, op, rng.randint(-5, 2005 if col == "id" else 505))
             for _ in range(150) for col in ("id", "class_id") for op in OPS]
    cases += [("class_id", "in", rng.sample(range(1, 500), 5)) for _ in range(20)]
    before = [sorted(r["id"] for r in q.from_("student").where(c, v, op).get()) for c, op, v in cases]
    q.create_index("student", "id")
    q.create_index("student", "class_id")
    after = [sorted(r["id"] for r in q.from_("student").where(c, v, op).get()) for c, op, v in cases]
    assert after == before


def test_index_combined_with_other_conditions(q):
    q.create_index("student", "class_id")
    rows = q.from_("student").where("class_id", 7).where("id", 1000, "<").get()
    assert rows and all(r["class_id"] == 7 and r["id"] < 1000 for r in rows)


def test_index_follows_insert_update_delete(q):
    q.create_index("student", "id")
    q.insert("student", {"id": 5000, "name": "Mới", "birthday": "2004-01-01", "phone": "0900000000", "class_id": 1})
    assert q.from_("student").where("id", 5000).first()["name"] == "Mới"

    q.from_("student").where("id", 5000).update("student", {"id": 6000})
    assert q.from_("student").where("id", 5000).first() is None
    assert q.from_("student").where("id", 6000).first()["name"] == "Mới"

    q.from_("student").where("id", 6000).delete("student")
    assert q.from_("student").where("id", 6000).first() is None


def test_index_skips_none(tmp_path):
    db = Database(tmp_path)
    db.create_table("t", {"id": int, "x": int})
    q = DBQuery(db)
    q.insert_many("t", [{"id": 1, "x": 5}, {"id": 2, "x": None}, {"id": 3, "x": 1}])
    q.create_index("t", "x")
    assert [r["id"] for r in q.from_("t").where("x", 3, "<").get()] == [3]
    assert [r["id"] for r in q.from_("t").where("x", None).get()] == [2]


def test_index_survives_reload(q, tmp_path):
    """Index nằm trong RAM: mở lại Database thì phải create_index lại, kết quả vẫn đúng."""
    db = Database(tmp_path)
    fresh = DBQuery(db)
    fresh.create_index("student", "id")
    assert fresh.from_("student").where("id", 1234).first() == q.from_("student").where("id", 1234).first()


def test_disk_index(q, tmp_path):
    table_file = tmp_path / "student.txt"
    index_file = disk_index.build(table_file, "id")
    for key in (1, 777, 2000):
        line, reads = disk_index.lookup(table_file, index_file, key)
        assert line.split("|")[0] == str(key)
        assert reads <= 11  # log2(2000) ≈ 11
    assert disk_index.lookup(table_file, index_file, 0)[0] is None
    assert disk_index.lookup(table_file, index_file, 2001)[0] is None
