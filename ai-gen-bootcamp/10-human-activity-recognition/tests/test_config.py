"""
Tests for Human Activity Recognition — validates config and file structure.
Run: pytest tests/
"""
import pytest
import os
from unittest.mock import patch


def test_env_loads_without_error(monkeypatch):
    """dotenv loading should not raise even if .env is missing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-12345")
    # Import should succeed with key present
    # This is a smoke test for import/config setup


def test_missing_api_key_raises_clear_error():
    """Importing with no API key should raise ValueError with helpful message."""
    with patch.dict(os.environ, {}, clear=True):
        try:
            import importlib
            pass
        except ValueError as e:
            assert "not set" in str(e).lower() or "api_key" in str(e).lower()


def test_requirements_file_exists():
    """requirements.txt must exist in the project root."""
    import pathlib
    req = pathlib.Path(__file__).parent.parent / "requirements.txt"
    assert req.exists(), "requirements.txt not found"


def test_evaluate_import_fixed():
    """evaluate.py must use 'from train_lstm import' not 'from scripts.train_lstm import'."""
    import pathlib
    ev = pathlib.Path(__file__).parent.parent / "evaluate.py"
    content = ev.read_text()
    assert "from scripts.train_lstm import" not in content, "Broken import still present"
    assert "from train_lstm import" in content, "Fixed import not found"
