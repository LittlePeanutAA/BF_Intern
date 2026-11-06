"""CLI quản lý sinh viên. Ví dụ: python qlsv.py add_class --id 1 --class_name "K66CC"."""
import argparse
import os
import sys
import unicodedata
from pathlib import Path

from school import ENTITIES, School, SchoolError, normalize

FIELD_HELP = {
    "id": "ID (số nguyên dương)", "class_name": "tên lớp", "name": "họ tên",
    "birthday": "YYYY-MM-DD", "phone": "10 chữ số, bắt đầu bằng 0",
    "class_id": "ID lớp", "head_of_class": "ID lớp chủ nhiệm (bỏ trống nếu không có)",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qlsv.py", description="Quản lý lớp, sinh viên, giáo viên")
    parser.add_argument("--data-dir", default=os.environ.get("QLSV_DATA", "data"),
                        help="thư mục chứa Class.txt, Student.txt, Teacher.txt (mặc định ./data)")
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


def run(args: argparse.Namespace) -> None:
    school = School(Path(args.data_dir))
    action, entity = args.command.split("_", 1)
    values = {k: v for k, v in vars(args).items() if k in ENTITIES[entity].keys}

    if action == "list":
        rows = school.rows(entity)
        if getattr(args, "class_id", None):
            class_id = normalize(ENTITIES["student"].columns[-1], args.class_id, required=True)
            rows = [r for r in rows if r["class_id"] == class_id]
        print_table(ENTITIES[entity].header, [list(r.values()) for r in rows])
    elif action == "add":
        print(f"Đã thêm {entity}: {school.add(entity, values)}")
    elif action == "edit":
        print(f"Đã sửa {entity}: {school.edit(entity, values.pop('id'), values)}")
    elif action == "remove":
        school.remove(entity, args.id)
        print(f"Đã xoá {entity} id={args.id}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run(args)
    except (SchoolError, ValueError) as e:  # ValueError: file dữ liệu sai định dạng
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
