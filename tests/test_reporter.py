# tests/test_reporter.py

import logging
import pytest
from app.reporter import report_security_issue

# Setup logging for test visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture
def mock_pr_url():
    return "https://github.com/atf-inc/dec25_intern_d_security/pull/1"

def test_report_critical_regex(mock_pr_url):
    """Test Case 1: Critical regex detection (Should alert Slack)"""
    test_data = {
        "repo": "atf-inc/test-repo",
        "branch": "feature/api-keys",
        "author": "dev@example.com",
        "incident": "Hardcoded Secrets / PII Detected",
        "summary_en": "Found 3 critical patterns across 2 files.",
        "summary_jp": "複数のファイルで3件の機密情報が検出されました。",
        "action": "BLOCK",
        "severity": "critical",
        "fix": "Remove hardcoded values.",
        "diff": "+ AWS_SECRET_KEY = 'AKIAIOSFODNN7EXAMPLE'\n+ API_KEY = 'sk-1234567890'",
        "issues": [
            {"file": "config.py", "pattern": "AWS Secret Key"},
            {"file": "settings.py", "pattern": "API Key"}
        ]
    }
    # report_security_issue returns True if it successfully triggers the slack_client
    result = report_security_issue(test_data, mock_pr_url)
    assert result is True

def test_report_ai_vulnerability(mock_pr_url):
    """Test Case 2: AI-detected vulnerability (Should alert Slack)"""
    test_data = {
        "repo": "atf-inc/web-app",
        "branch": "develop",
        "author": "security-team@atf.com",
        "incident": "SQL Injection Vulnerability Detected",
        "summary_en": "Direct user input used in SQL query without sanitization.",
        "summary_jp": "サニタイズされていないユーザー入力がSQLクエリで使用されています。",
        "action": "BLOCK",
        "severity": "high",
        "fix": "Use parameterized queries or ORM methods.",
        "diff": "+ query = f'SELECT * FROM users WHERE id = {user_id}'",
        "issues": [
            {"type": "sql_injection", "line": 42, "file": "database.py"}
        ]
    }
    result = report_security_issue(test_data, mock_pr_url)
    assert result is True

def test_report_clean_pass(mock_pr_url):
    """Test Case 3: Pass with no issues (Should skip Slack notification)"""
    test_data = {
        "repo": "atf-inc/docs",
        "branch": "main",
        "author": "writer@atf.com",
        "incident": "No changes to scan",
        "action": "PASS",
        "severity": "low",
        "issues": []
    }
    # reporter.py is configured to return True but skip Slack for clean passes
    result = report_security_issue(test_data, mock_pr_url)
    assert result is True

if __name__ == "__main__":
    # Allow running this specific test file directly
    pytest.main([__file__])