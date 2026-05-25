"""Tests for Session 03 RAG Fundamentals — config and import validation."""
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
