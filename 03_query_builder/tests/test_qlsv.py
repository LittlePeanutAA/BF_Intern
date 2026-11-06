import shutil
from pathlib import Path

import pytest

from qlsv import main

SAMPLE = Path(__file__).parents[1] / "sample_data"


@pytest.fixture
def run(tmp_path, capsys):
    """Chạy CLI trên một bản sao của sample_data, trả về (mã thoát, stdout, stderr)."""
    data = tmp_path / "data"
    shutil.copytree(SAMPLE, data)

    def _run(*argv):
        code = main(["--data-dir", str(data), *argv])
        out, err = capsys.readouterr()
        return code, out, err

    _run.data = data
    return _run


def test_list_student_by_class(run):
    code, out, _ = run("list_student", "--class_id", "1")
    assert code == 0
    assert "Nguyễn Văn An" in out and "Trần Thị Bình" in out and "Lê Hoàng Cường" not in out
    assert "(2 dòng)" in out


def test_add_edit_remove_class(run):
    assert run("add_class", "--id", "4", "--class_name", "K67CA")[0] == 0
    assert "4|K67CA" in (run.data / "class.txt").read_text(encoding="utf-8")
    assert run("edit_class", "--id", "4", "--class_name", "K67CB")[0] == 0
    assert "4|K67CB" in (run.data / "class.txt").read_text(encoding="utf-8")
    assert run("remove_class", "--id", "4")[0] == 0
    assert "K67CB" not in (run.data / "class.txt").read_text(encoding="utf-8")


def test_file_format(run):
    run("add_student", "--id", "5", "--name", "Ngô Gia Huy", "--birthday", "2004-02-29",
        "--phone", "0912000005", "--class_id", "2")
    lines = (run.data / "student.txt").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "id:int|name:str|birthday:str|phone:str|class_id:int"
    assert lines[-1] == "5|Ngô Gia Huy|2004-02-29|0912000005|2"


def test_edit_only_changes_given_fields(run):
    run("edit_student", "--id", "1", "--phone", "0999999999")
    row = (run.data / "student.txt").read_text(encoding="utf-8").splitlines()[1]
    assert row == "1|Nguyễn Văn An|2004-03-12|0999999999|1"


def test_missing_files_mean_empty_tables(tmp_path, capsys):
    data = tmp_path / "empty"
    assert main(["--data-dir", str(data), "list_class"]) == 0
    assert main(["--data-dir", str(data), "add_class", "--id", "1", "--class_name", "A"]) == 0
    assert (data / "class.txt").read_text(encoding="utf-8") == "id:int|class_name:str\n1|A\n"


@pytest.mark.parametrize("argv, message", [
    (["add_class", "--id", "1", "--class_name", "X"], "đã tồn tại"),
    (["edit_class", "--id", "99", "--class_name", "X"], "không có class"),
    (["list_student", "--class_id", "x"], "không phải int"),
    (["remove_student", "--id", "99"], "không có student"),
    (["add_class", "--id", "abc", "--class_name", "X"], "không phải int"),
    (["add_class", "--id", "9", "--class_name", "A|B"], "'|'"),
    (["add_student", "--id", "9", "--name", "X", "--birthday", "2004-13-01", "--phone", "0912000009", "--class_id", "1"], "YYYY-MM-DD"),
    (["add_student", "--id", "9", "--name", "X", "--birthday", "2004-01-01", "--phone", "12345", "--class_id", "1"], "10 chữ số"),
    (["add_student", "--id", "9", "--name", "X", "--birthday", "2004-01-01", "--phone", "0912000009", "--class_id", "42"], "không tồn tại"),
    (["add_teacher", "--id", "9", "--name", "X", "--birthday", "1990-01-01", "--phone", "0903000009", "--head_of_class", "1"], "đã có chủ nhiệm"),
    (["edit_teacher", "--id", "3", "--head_of_class", "2"], "đã có chủ nhiệm"),
    (["remove_class", "--id", "1"], "còn sinh viên"),
    (["edit_student", "--id", "1"], "không có trường nào"),
])
def test_errors(run, argv, message):
    before = {p.name: p.read_text(encoding="utf-8") for p in run.data.iterdir()}
    code, _, err = run(*argv)
    assert code == 1
    assert message in err
    after = {p.name: p.read_text(encoding="utf-8") for p in run.data.iterdir()}
    assert after == before  # lỗi thì không được đổi dữ liệu


def test_teacher_can_drop_head_of_class(run):
    assert run("edit_teacher", "--id", "1", "--head_of_class", "")[0] == 0
    assert run("edit_teacher", "--id", "3", "--head_of_class", "1")[0] == 0


def test_corrupted_file_is_reported(run):
    (run.data / "class.txt").write_text("id:int|class_name:str\n1|A|extra\n", encoding="utf-8")
    code, _, err = run("list_class")
    assert code == 1 and "cần 2" in err


def test_unknown_command_shows_usage(run):
    with pytest.raises(SystemExit) as exc:
        run("fly_away")
    assert exc.value.code == 2
