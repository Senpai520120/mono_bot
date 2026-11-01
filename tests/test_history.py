import json
import threading

from utils.history import get_history, save_history


def test_empty_when_file_missing(tmp_path):
    assert get_history(tmp_path / "history.json") == []


def test_keeps_last_10_newest_first(tmp_path):
    path = tmp_path / "history.json"
    for i in range(15):
        save_history({"n": i}, path)
    assert [e["n"] for e in get_history(path)] == list(range(14, 4, -1))


def test_corrupted_file_is_replaced(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("{not json", encoding="utf-8")
    assert get_history(path) == []
    save_history({"n": 1}, path)
    assert json.loads(path.read_text(encoding="utf-8")) == [{"n": 1}]


def test_concurrent_writes_do_not_corrupt_file(tmp_path):
    path = tmp_path / "history.json"
    threads = [threading.Thread(target=save_history, args=({"n": i}, path)) for i in range(30)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(get_history(path)) == 10
