"""Tests for Session 08 AutoGen FinTech — config and import validation."""
import pytest
import os
import pathlib
from unittest.mock import patch


def test_requirements_file_exists():
    req = pathlib.Path(__file__).parent.parent / "requirements.txt"
    assert req.exists(), "requirements.txt not found"


def test_env_example_exists():
    env_ex = pathlib.Path(__file__).parent.parent / ".env.example"
    assert env_ex.exists(), ".env.example not found"


def test_no_hardcoded_api_keys():
    """Scan all .py files for hardcoded API key patterns."""
    import re
    project_root = pathlib.Path(__file__).parent.parent
    bad_pattern = re.compile(r'(sk-[a-zA-Z0-9]{20,}|gsk_[a-zA-Z0-9]{20,}|api_key\s*=\s*["\'][a-zA-Z0-9\-_]{10,}["\'])')
    violations = []
    for py_file in project_root.glob("*.py"):
        content = py_file.read_text(errors="ignore")
        if bad_pattern.search(content):
            violations.append(py_file.name)
    assert not violations, f"Hardcoded API keys found in: {violations}"


def test_python_files_have_no_syntax_errors():
    """All .py files must be valid Python."""
    import ast
    project_root = pathlib.Path(__file__).parent.parent
    errors = []
    for py_file in project_root.glob("*.py"):
        try:
            ast.parse(py_file.read_text(errors="ignore"))
        except SyntaxError as e:
            errors.append(f"{py_file.name}: {e}")
    assert not errors, f"Syntax errors found: {errors}"


def test_requirements_has_pyautogen_not_autogen():
    """requirements.txt must use pyautogen, not the wrong autogen package."""
    project_root = pathlib.Path(__file__).parent.parent
    content = (project_root / "requirements.txt").read_text()
    assert 'pyautogen' in content, "requirements.txt missing pyautogen"
    assert 'autogen~=0.9.9' not in content, "requirements.txt still has wrong autogen~=0.9.9"


def test_fintech_app_logs_errors():
    """3.fintech_app.py must log exceptions, not silently swallow them."""
    project_root = pathlib.Path(__file__).parent.parent
    fintech = project_root / "3.fintech_app.py"
    assert fintech.exists(), "3.fintech_app.py not found"
    content = fintech.read_text()
    assert 'print(f"[ERROR]' in content or "print(f'[ERROR]" in content, \
        "Error logging missing in 3.fintech_app.py except block"


def test_no_unsafe_env_assignment():
    """No file should do os.environ[key] = os.getenv(key) without None check."""
    import re
    project_root = pathlib.Path(__file__).parent.parent
    unsafe = re.compile(r"os\.environ\[.OPENAI_API_KEY.\]\s*=\s*os\.getenv\(.OPENAI_API_KEY.\)")
    violations = []
    for py_file in project_root.glob("*.py"):
        content = py_file.read_text(errors="ignore")
        if unsafe.search(content):
            violations.append(py_file.name)
    assert not violations, f"Unsafe env assignment (None not checked) in: {violations}"
