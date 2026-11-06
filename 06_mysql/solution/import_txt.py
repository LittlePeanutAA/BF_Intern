"""Chuyển dữ liệu từ các file text của bài 02 sang MySQL, trong MỘT transaction.

    python import_txt.py ../sample_data
    python import_txt.py ../sample_data --db mysql://user:pass@host:3306/qlsv

Nếu một dòng bất kỳ sai (trùng ID, lớp không tồn tại...), không dòng nào được ghi.
"""
import argparse
import os
import sys
from pathlib import Path

import pymysql

from school import DEFAULT_URL, ENTITIES, School, SchoolError, connect, explain, normalize

FILES = {"class": "Class.txt", "student": "Student.txt", "teacher": "Teacher.txt"}


def read_txt(path: Path) -> list[list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.split("|") for line in lines[1:] if line.strip()]


def import_dir(school: School, data_dir: Path) -> dict[str, int]:
    counts = {}
    conn = school.conn
    try:
        with conn.cursor() as cur:
            # Thứ tự quan trọng: lớp trước, vì sinh viên và giáo viên tham chiếu tới lớp
            for entity in ("class", "student", "teacher"):
                e = ENTITIES[entity]
                path = data_dir / FILES[entity]
                rows = read_txt(path) if path.exists() else []
                sql = f"INSERT INTO {e.table} ({', '.join(e.keys)}) VALUES ({', '.join(['%s'] * len(e.keys))})"
                for n, cells in enumerate(rows, 2):
                    if len(cells) != len(e.columns):
                        raise SchoolError(f"{path.name} dòng {n}: cần {len(e.columns)} cột, có {len(cells)}")
                    try:
                        row = {c.key: normalize(c, v, required=c.key != "head_of_class")
                               for c, v in zip(e.columns, cells)}
                    except SchoolError as err:
                        raise SchoolError(f"{path.name} dòng {n}: {err}") from None
                    try:
                        cur.execute(sql, tuple(row.values()))
                    except (pymysql.err.IntegrityError, pymysql.err.OperationalError) as err:
                        raise SchoolError(f"{path.name} dòng {n}: {explain(err, entity, row)}") from None
                counts[entity] = len(rows)
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--db", default=os.environ.get("QLSV_DB_URL", DEFAULT_URL))
    args = parser.parse_args()
    conn = connect(args.db)
    try:
        print(import_dir(School(conn), args.data_dir))
    except SchoolError as e:
        print(f"Lỗi: {e}. Không có dòng nào được ghi.", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
