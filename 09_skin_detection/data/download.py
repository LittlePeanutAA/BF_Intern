"""Tải bộ dữ liệu Pratheepan (78 ảnh + mask) về data/pratheepan/.

    python data/download.py

Nguồn chính thức: http://www.cs-chan.com/downloads_skin_dataset.html (file trên Google Drive của tác giả).
Bộ dữ liệu không được đưa vào repo vì ảnh lấy từ Internet, bản quyền thuộc người chụp.
"""
import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path

URL = "https://drive.usercontent.google.com/download?id=1nr3GCRWRG6RvgFH25Cquvl2tFbkQIWNB&export=download&confirm=t"
SHA256 = "d12482b09381630b4858e8f30ecb5e73e67dbd5f81b83e11e9449f81692501a3"
OUT = Path(__file__).resolve().parent / "pratheepan"


def main() -> None:
    if (OUT / "Ground_Truth").exists():
        print(f"Đã có dữ liệu ở {OUT}")
        return
    print("Đang tải khoảng 6 MB...")
    data = urllib.request.urlopen(URL, timeout=120).read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"Checksum không khớp ({digest}); file trên Drive có thể đã đổi.")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            # Bỏ rác của macOS có sẵn trong file zip gốc
            if name.startswith("__MACOSX") or name.endswith(".DS_Store") or name.endswith("/"):
                continue
            target = OUT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))
    print(f"Xong: {sum(1 for _ in OUT.rglob('*.*'))} file trong {OUT}")


if __name__ == "__main__":
    main()
