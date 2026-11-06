"""CLI quản lý sinh viên trên MySQL. Cùng các lệnh với bài 02, thêm --db thay cho --data-dir.

    python qlsv.py add_class --id 1 --class_name "K66CC"
    python qlsv.py --db mysql://user:pass@host:3306/qlsv list_student --class_id 1
"""
import argparse
import os
import sys
import unicodedata

import pymysql

from school import DEFAULT_URL, ENTITIES, School, SchoolError, connect, normalize

FIELD_HELP = {
    "id": "ID (số nguyên dương)", "class_name": "tên lớp", "name": "họ tên",
    "birthday": "YYYY-MM-DD", "phone": "10 chữ số, bắt đầu bằng 0",
    "class_id": "ID lớp", "head_of_class": "ID lớp chủ nhiệm (bỏ trống nếu không có)",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qlsv.py", description="Quản lý lớp, sinh viên, giáo viên (MySQL)")
    parser.add_argument("--db", default=os.environ.get("QLSV_DB_URL", DEFAULT_URL),
                        help="URL kết nối, mặc định lấy từ biến môi trường QLSV_DB_URL")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    for name, entity in ENTITIES.items():
        p = sub.add_parser(f"list_{name}", help=f"liệt kê {name}")
        if name == "student":
            p.add_argument("--class_id", help="chỉ hiện sinh viên của lớp này")

        p = sub.add_parser(f"add_{name}", help=f"thêm {name}")
        for c in entity.columns:
            p.add_argument(f"--{c.key}", required=c.key != "head_of_class", help=FIELD_HELP[c.key])

        p = sub.add_parser(f"edit_{name}", help=f"sửa {name}, chỉ các trường được truyền")
        for c in entity.columns:
            p.add_argument(f"--{c.key}", required=c.key == "id", help=FIELD_HELP[c.key])

        p = sub.add_parser(f"remove_{name}", help=f"xoá {name}")
        p.add_argument("--id", required=True, help=FIELD_HELP["id"])
    return parser


def width(text: str) -> int:
    """Độ rộng hiển thị: bỏ qua dấu tổ hợp để tiếng Việt dạng NFD vẫn thẳng cột."""
    return sum(1 for ch in text if not unicodedata.combining(ch))


def print_table(header: list[str], rows: list[list[str]]) -> None:
    widths = [max([width(h), *(width(r[i]) for r in rows)]) for i, h in enumerate(header)]
    line = lambda cells: "  ".join(c + " " * (w - width(c)) for c, w in zip(cells, widths)).rstrip()
    print(line(header))
    print(line(["-" * w for w in widths]))
    for r in rows:
        print(line(r))
    print(f"({len(rows)} dòng)")


def show(value) -> str:
    return "" if value is None else str(value)


def run(school: School, args: argparse.Namespace) -> None:
    action, entity = args.command.split("_", 1)
    e = ENTITIES[entity]
    values = {k: v for k, v in vars(args).items() if k in e.keys}

    if action == "list":
        class_id = getattr(args, "class_id", None)
        if class_id:
            class_id = normalize(e.columns[-1], class_id, required=True)
        rows = school.rows(entity, class_id=class_id or None)
        print_table(e.header, [[show(r[k]) for k in e.keys] for r in rows])
    elif action == "add":
        print(f"Đã thêm {entity}: {school.add(entity, values)}")
    elif action == "edit":
        print(f"Đã sửa {entity}: {school.edit(entity, values.pop('id'), values)}")
    elif action == "remove":
        school.remove(entity, args.id)
        print(f"Đã xoá {entity} id={args.id}")


def main(argv: list[str] | None = None, conn=None) -> int:
    """`conn` cho phép test truyền sẵn một kết nối; bình thường mở kết nối từ --db."""
    args = build_parser().parse_args(argv)
    try:
        own = conn is None
        conn = conn or connect(args.db)
    except pymysql.err.OperationalError as e:
        print(f"Lỗi: không kết nối được MySQL ({e.args[-1]})", file=sys.stderr)
        return 2
    try:
        run(School(conn), args)
    except SchoolError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    finally:
        if own:
            conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
