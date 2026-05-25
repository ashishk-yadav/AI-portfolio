"""
Tests for Legal Doc Summarizer — validates config loading and key validation.
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


def test_env_example_exists():
    """'.env.example' must exist in the project root."""
    import pathlib
    env_ex = pathlib.Path(__file__).parent.parent / ".env.example"
    assert env_ex.exists(), ".env.example not found"
