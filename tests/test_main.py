import main


def test_missing_token_prints_clear_error(monkeypatch, capsys):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(main, "load_dotenv", lambda: None)
    assert main.main() == 1
    assert "TELEGRAM_BOT_TOKEN is not set" in capsys.readouterr().err
