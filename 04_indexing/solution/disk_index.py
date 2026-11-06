"""Index lưu trên đĩa: tìm một dòng trong file 1 triệu dòng mà không phải đọc cả file.

File `<bảng>.<cột>.idx` gồm các bản ghi 16 byte cố định (khoá int64, vị trí byte của dòng
trong file .txt), sắp xếp tăng dần theo khoá. Vì bản ghi dài cố định nên bản ghi thứ i nằm
ở byte i*16: tìm nhị phân chỉ cần khoảng log2(n) lần seek + read, không cần nạp gì vào RAM.
Đây là ý tưởng nền của B-tree trong MySQL/PostgreSQL (B-tree đọc theo trang thay vì từng bản ghi).
"""
import struct
from pathlib import Path

RECORD = struct.Struct("<qQ")  # khoá int64, offset uint64


def build(table_file: Path, column: str) -> Path:
    """Quét file bảng một lần, ghi index đã sắp xếp. Chỉ hỗ trợ cột kiểu int."""
    entries = []
    with table_file.open("rb") as f:
        header = f.readline().decode("utf-8").rstrip("\n").split("|")
        names = [h.partition(":")[0] for h in header]
        if f"{column}:int" not in header:
            raise ValueError(f"{table_file.name}: cần cột '{column}' kiểu int")
        pos = names.index(column)
        offset = f.tell()
        for line in f:
            cell = line.split(b"|")[pos]
            if cell.strip():
                entries.append((int(cell), offset))
            offset += len(line)
    entries.sort()
    index_file = table_file.with_suffix(f".{column}.idx")
    with index_file.open("wb") as f:
        for key, off in entries:
            f.write(RECORD.pack(key, off))
    return index_file


def lookup(table_file: Path, index_file: Path, key: int) -> tuple[str | None, int]:
    """Trả về (dòng dữ liệu hoặc None, số lần đọc index)."""
    reads = 0
    with index_file.open("rb") as idx:
        lo, hi = 0, idx.seek(0, 2) // RECORD.size
        while lo < hi:  # lower_bound giống trong minidb, nhưng đọc từ đĩa
            mid = (lo + hi) // 2
            idx.seek(mid * RECORD.size)
            mid_key, _ = RECORD.unpack(idx.read(RECORD.size))
            reads += 1
            if mid_key < key:
                lo = mid + 1
            else:
                hi = mid
        idx.seek(lo * RECORD.size)
        record = idx.read(RECORD.size)
    if len(record) < RECORD.size:
        return None, reads
    found_key, offset = RECORD.unpack(record)
    if found_key != key:
        return None, reads
    with table_file.open("rb") as f:
        f.seek(offset)
        return f.readline().decode("utf-8").rstrip("\n"), reads
