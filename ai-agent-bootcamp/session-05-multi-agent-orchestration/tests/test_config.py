"""Tests for Session 05 Multi-Agent Orchestration — config and import validation."""
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


def test_stale_csv_not_present():
    """Unreferenced stale CSV must not be copied."""
    project_root = pathlib.Path(__file__).parent.parent
    stale = project_root / "ind_niftyCoreHousing_list 2.csv"
    assert not stale.exists(), "Stale unreferenced CSV was copied and should be excluded"


def test_hotel_log_no_module_level_crash():
    """hotel_review_log_analysis.py must not crash if CSV missing."""
    import ast
    project_root = pathlib.Path(__file__).parent.parent
    hotel_log = project_root / "6.hotel_review_log_analysis.py"
    assert hotel_log.exists(), "6.hotel_review_log_analysis.py not found"
    content = hotel_log.read_text()
    assert 'os.path.exists' in content, "Missing os.path.exists guard for CSV read"


def test_qna_chatbot_uses_correct_import():
    """1.qna_chatbot_UI.py must import ChatOpenAI from langchain_openai."""
    project_root = pathlib.Path(__file__).parent.parent
    qna = project_root / "1.qna_chatbot_UI.py"
    assert qna.exists(), "1.qna_chatbot_UI.py not found"
    content = qna.read_text()
    assert 'from langchain_openai import ChatOpenAI' in content, \
        "Still using deprecated langchain_community.chat_models.ChatOpenAI"
