import pytest

from wordstat.cli import count_words, main


def test_counts_words():
    assert count_words("cat dog cat") == {"cat": 2, "dog": 1}


def test_top_n(capsys, tmp_path):
    file = tmp_path / "words.txt"
    file.write_text("apple banana apple orange banana apple", encoding="utf-8")
    assert main([str(file), "-n", "2"]) == 0
    assert capsys.readouterr().out == "apple: 3\nbanana: 2\n"


def test_empty_file(tmp_path, capsys):
    file = tmp_path / "empty.txt"
    file.write_text("", encoding="utf-8")
    assert main([str(file)]) == 0
    assert capsys.readouterr().out == ""


def test_unicode_words():
    assert count_words("café café привет") == {"café": 2, "привет": 1}


def test_very_long_line():
    assert count_words("hello " * 100000)["hello"] == 100000


def test_missing_file(capsys, tmp_path):
    assert main([str(tmp_path / "missing.txt")]) == 1
    assert "Cannot read file" in capsys.readouterr().err


def test_case_insensitive():
    assert count_words("Python python PYTHON") == {"python": 3}


def test_invalid_top_value():
    with pytest.raises(SystemExit) as error:
        main(["file.txt", "--top", "0"])
    assert error.value.code == 2
