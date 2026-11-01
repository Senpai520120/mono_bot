import json
import logging
import os
import tempfile
import threading

import config

logger = logging.getLogger(__name__)

# The bot handles updates in several threads, so reads and writes are serialized.
_lock = threading.Lock()


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as exc:
        logger.warning("History file %s is unreadable (%s), starting with an empty history", path, exc)
        return []
    return data if isinstance(data, list) else []


def _write_atomic(path, data):
    """Write to a temp file and rename it, so a crash never leaves half-written JSON."""
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp_path, path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def save_history(entry, path=None):
    path = path or config.HISTORY_FILE
    with _lock:
        history = [entry, *_read(path)][: config.HISTORY_LIMIT]
        _write_atomic(path, history)


def get_history(path=None):
    path = path or config.HISTORY_FILE
    with _lock:
        return _read(path)
