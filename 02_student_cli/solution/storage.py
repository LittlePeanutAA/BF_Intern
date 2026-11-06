"""Đọc/ghi bảng dạng text: dòng đầu là tên cột, các cột ngăn cách bằng '|'."""
import os
import tempfile
from pathlib import Path

SEP = "|"


def read_table(path: Path, header: list[str]) -> list[list[str]]:
    """Trả về các dòng dữ liệu (đã bỏ dòng tiêu đề). File chưa có thì coi là bảng rỗng."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []
    found = [c.strip() for c in lines[0].split(SEP)]
    if found != header:
        raise ValueError(f"{path.name}: tiêu đề {found} khác với {header}")
    rows = []
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cells = [c.strip() for c in line.split(SEP)]
        if len(cells) != len(header):
            raise ValueError(f"{path.name}:{lineno}: có {len(cells)} cột, cần {len(header)}")
        rows.append(cells)
    return rows


def write_table(path: Path, header: list[str], rows: list[list[str]]) -> None:
    """Ghi ra file tạm rồi đổi tên, để file cũ không bao giờ bị ghi dở."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(SEP.join(r) for r in [header, *rows]) + "\n"
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)  # thao tác nguyên tử trên cùng một ổ đĩa
    except BaseException:
        os.unlink(tmp)
        raise
