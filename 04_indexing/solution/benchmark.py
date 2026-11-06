"""Đo thời gian tìm sinh viên id=669416 trong 1 triệu bản ghi: không index, index trong RAM, index trên đĩa.

    python benchmark.py                  # 1 triệu dòng, ghi vào ./bench_data
    python benchmark.py --n 100000       # chạy nhanh hơn
"""
import argparse
import random
import time
from pathlib import Path

import disk_index
from minidb import Database, DBQuery

FIRST = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đặng", "Bùi", "Đỗ", "Ngô"]
MIDDLE = ["Văn", "Thị", "Minh", "Thu", "Hoàng", "Gia", "Quốc", "Thanh"]
LAST = ["An", "Bình", "Cường", "Dung", "Hải", "Lan", "Nam", "Phương", "Quân", "Trang"]
SCHEMA = {"id": int, "name": str, "birthday": str, "phone": str, "class_id": int}


def timed(fn, repeat: int = 1):
    """Chạy fn `repeat` lần, trả về (kết quả lần cuối, thời gian trung bình mỗi lần, giây)."""
    start = time.perf_counter()
    for _ in range(repeat):
        result = fn()
    return result, (time.perf_counter() - start) / repeat


def fmt(seconds: float) -> str:
    if seconds >= 1:
        return f"{seconds:.2f} s"
    if seconds >= 1e-3:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds * 1e6:.1f} µs"


def report(label: str, seconds: float, note: str = "") -> None:
    print(f"{label:<34}{fmt(seconds):>10}   {note}".rstrip())


def make_students(n: int, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    ids = list(range(1, n + 1))
    rng.shuffle(ids)  # thứ tự ngẫu nhiên trong file, để index thực sự phải sắp xếp
    return [{"id": i, "name": f"{rng.choice(FIRST)} {rng.choice(MIDDLE)} {rng.choice(LAST)}",
             "birthday": f"200{rng.randint(0, 6)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
             "phone": f"09{rng.randrange(10**8):08d}", "class_id": rng.randint(1, 500)} for i in ids]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=1_000_000)
    parser.add_argument("--target", type=int, default=669_416)
    parser.add_argument("--data-dir", type=Path, default=Path("bench_data"))
    args = parser.parse_args()
    target = min(args.target, args.n)
    for f in args.data_dir.glob("student*"):
        f.unlink()

    print(f"== {args.n:,} sinh viên, tìm id={target}")
    students = make_students(args.n)
    db = Database(args.data_dir)
    db.create_table("student", SCHEMA)
    _, t = timed(lambda: DBQuery(db).insert_many("student", students))
    size = (args.data_dir / "student.txt").stat().st_size / 2**20
    report("ghi file", t, f"({size:.0f} MB)")

    db = Database(args.data_dir)  # giả lập một tiến trình mới: phải đọc lại file
    _, t = timed(lambda: db.table("student"))
    report("đọc file vào RAM", t)

    query = DBQuery(db).from_("student").where("id", target)
    row, t_scan = timed(query.get, repeat=5)
    report("tìm, không index (duyệt cả bảng)", t_scan, f"-> {row[0]['name']}")

    _, t = timed(lambda: DBQuery(db).create_index("student", "id"))
    report("create_index('student', 'id')", t)
    row2, t_idx = timed(query.get, repeat=10_000)
    assert row2 == row
    report("tìm, có index (tìm nhị phân)", t_idx, f"nhanh hơn {t_scan / t_idx:,.0f} lần")

    _, t = timed(lambda: disk_index.build(args.data_dir / "student.txt", "id"))
    report("dựng index trên đĩa", t)
    (line, reads), t_disk = timed(lambda: disk_index.lookup(
        args.data_dir / "student.txt", args.data_dir / "student.id.idx", target), repeat=1000)
    report("tìm bằng index trên đĩa", t_disk, f"({reads} lần đọc index, không nạp bảng vào RAM)")
    print(f"  -> {line}")


if __name__ == "__main__":
    main()
