"""Test trên dữ liệu tự tạo: không cần ảnh BF, không cần GPU, không cần ultralytics."""
import io
import json

import pytest
from PIL import Image, ImageDraw

from annotations import assign_split, dhash, rect_to_box
from crops import box_to_crop, crop_rect, xyxy_from_crop
from yolo_data import make_manifest, write_crop_dataset, write_full_dataset


def test_rect_to_box():
    assert rect_to_box({"top": 10, "left": 20, "bottom": 50, "right": 60}) == pytest.approx((0.4, 0.3, 0.4, 0.4))
    # trái/phải bị đảo, tràn ra ngoài ảnh
    assert rect_to_box({"top": -5, "left": 60, "bottom": 50, "right": 20}) == pytest.approx((0.4, 0.25, 0.4, 0.5))
    assert rect_to_box(None) is None
    assert rect_to_box({"top": 10, "left": 10, "bottom": 10, "right": 50}) is None
    assert rect_to_box({"top": "x", "left": 1, "bottom": 2, "right": 3}) is None


def test_split_is_stable_and_by_group():
    assert assign_split("abc") == assign_split("abc")
    counts = {s: 0 for s in ("train", "val", "test")}
    for i in range(3000):
        counts[assign_split(f"g{i}")] += 1
    assert 0.66 < counts["train"] / 3000 < 0.74 and 0.12 < counts["test"] / 3000 < 0.18
    with pytest.raises(ValueError):
        assign_split("abc", ratios=(0.5, 0.5, 0.5))


def make_image(path, color=(200, 30, 30), size=(200, 300)):
    """Nền chuyển màu và một khối màu. dHash so độ sáng các pixel kề nhau, nên nền phẳng một màu
    sẽ cho kết quả "bằng nhau" không ổn định khi ảnh bị nén lại."""
    w, h = size
    gradient = Image.linear_gradient("L").rotate(90 if w < h else -90).resize(size)  # sáng dần theo chiều ngang
    img = Image.merge("RGB", (gradient, gradient, gradient))
    ImageDraw.Draw(img).rectangle((w // 4, h // 3, 3 * w // 4, 5 * h // 6), fill=color)
    img.save(path, quality=95)


def test_dhash_groups_reencoded_copies(tmp_path):
    make_image(tmp_path / "a.jpg")
    Image.open(tmp_path / "a.jpg").resize((100, 150)).save(tmp_path / "a_small.jpg", quality=70)
    make_image(tmp_path / "b.jpg", size=(300, 200))
    assert dhash(tmp_path / "a.jpg") == dhash(tmp_path / "a_small.jpg")
    assert dhash(tmp_path / "a.jpg") != dhash(tmp_path / "b.jpg")


def test_crop_round_trip():
    label = (0.5, 0.5, 0.5, 0.5)                       # nhãn ở giữa ảnh 200x300
    rect = crop_rect(label, 200, 300)
    assert rect == (50, 75, 150, 225)
    vintage = (0.5, 0.7, 0.2, 0.05)
    inside = box_to_crop(vintage, rect, 200, 300)
    assert inside == pytest.approx((0.5, 0.9, 0.4, 0.1))
    # đổi ngược về pixel ảnh gốc
    cx, cy, w, h = inside
    xyxy = ((cx - w / 2) * 100, (cy - h / 2) * 150, (cx + w / 2) * 100, (cy + h / 2) * 150)
    assert xyxy_from_crop(xyxy, rect) == pytest.approx((80, 202.5, 120, 217.5))


def test_box_mostly_outside_crop_is_dropped_but_edge_box_kept():
    rect = (50, 75, 150, 225)
    assert box_to_crop((0.5, 0.25, 0.2, 0.05), rect, 200, 300) is None          # nằm ngoài nhãn
    assert box_to_crop((0.5, 0.745, 0.2, 0.02), rect, 200, 300) is not None     # chạm mép dưới, vẫn giữ


def test_build_datasets(tmp_path):
    images = tmp_path / "raw"
    images.mkdir()
    make_image(images / "a.jpg")
    make_image(images / "a_copy.jpg")                  # bản trùng: phải cùng split với a.jpg
    make_image(images / "b.jpg", color=(20, 20, 200), size=(300, 200))
    rect = {"top": 30, "left": 25, "bottom": 85, "right": 75}
    records = [
        {"image": "a.jpg", "label_rect": rect, "variety_rect": {"top": 60, "left": 35, "bottom": 65, "right": 65},
         "vintage_rect": None},
        {"image": "a_copy.jpg", "label_rect": rect, "variety_rect": None, "vintage_rect": None},
        {"image": "b.jpg", "label_rect": None, "variety_rect": None, "vintage_rect": None},
    ]
    rows = make_manifest(records, images)
    assert rows[0]["group"] == rows[1]["group"] and rows[0]["split"] == rows[1]["split"]
    json.dumps(rows)  # manifest phải ghi được ra JSON

    full = write_full_dataset(rows, images, tmp_path / "full").parent
    labels = sorted(p.name for p in full.glob("labels/*/*.txt"))
    assert labels == ["a.txt", "a_copy.txt"]           # b.jpg không có box nào nên bị bỏ
    split = rows[0]["split"]
    first = (full / "labels" / split / "a.txt").read_text().splitlines()
    assert [line.split()[0] for line in first] == ["0", "1"]   # label, variety

    crop = write_crop_dataset(rows, images, tmp_path / "crop").parent
    assert sorted(p.name for p in crop.glob("labels/*/*.txt")) == ["a.txt"]   # crop không có chữ thì bỏ
    assert (crop / "labels" / split / "a.txt").read_text().startswith("0 ")
    assert "names:\n  0: variety\n  1: vintage" in (crop / "data.yaml").read_text()


# ---------- API, với detector giả ----------

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from api import Detection, TwoStage, app, get_detector  # noqa: E402


def fake_stage1(image):
    return [Detection("label", 0.9, (50, 75, 150, 225)), Detection("variety", 0.3, (0, 0, 10, 10))]


def fake_stage2(crop):
    assert crop.size == (104, 156)                     # vùng nhãn nới thêm 2% mỗi phía
    return [Detection("vintage", 0.8, (10, 20, 30, 40))]


@pytest.fixture
def client():
    app.dependency_overrides[get_detector] = lambda: TwoStage(fake_stage1, fake_stage2)
    yield TestClient(app)
    app.dependency_overrides.clear()


def upload(img: Image.Image) -> dict:
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return {"image": ("x.jpg", buf.getvalue(), "image/jpeg")}


def test_predict_two_stage_maps_back_to_full_image(client):
    res = client.post("/predict", files=upload(Image.new("RGB", (200, 300))))
    assert res.status_code == 200
    body = res.json()
    assert [d["class"] for d in body["detections"]] == ["label", "vintage"]   # variety của bước 1 bị thay
    assert body["detections"][1]["bbox_xyxy"] == [58.0, 92.0, 78.0, 112.0]    # cộng gốc vùng cắt (48, 72)


def test_predict_rejects_non_image(client):
    res = client.post("/predict", files={"image": ("x.txt", b"not an image", "text/plain")})
    assert res.status_code == 400


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
