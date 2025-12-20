# backend/app/patterns.py

"""
ATF Sentinel - Security Pattern Database
This module defines regex patterns to detect secrets, credentials, and PII.
It is used by the pattern_scanner module to flag high-risk code changes.
"""

# 1. High-Entropy Secrets (The "Block Immediately" List)
SECRET_PATTERNS = {
    # AWS
    "AWS_ACCESS_KEY_ID": r"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])",
    "AWS_SECRET_ACCESS_KEY": r"(?i)(?:aws_secret_access_key|[a-z0-9_]*secret[a-z0-9_]*key[a-z0-9_]*)['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9\/+=]{40}['\"]?",
    
    # Google / Firebase
    "GOOGLE_API_KEY": r"AIza[0-9A-Za-z\-_]{35}",
    "GCP_PRIVATE_KEY_ID": r"private_key_id['\"]?:\s*['\"]?[a-f0-9]{40}['\"]?",
    
    # Platforms
    "GITHUB_TOKEN": r"(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36}",
    "SLACK_WEBHOOK": r"https://hooks\.slack\.com/services/T[A-Z0-9]{8,12}/B[A-Z0-9]{8,12}/[A-Z0-9]{24}",
    "SLACK_BOT_TOKEN": r"xoxb-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24}",
    
    # Database
    "DB_CONNECTION_STRING": r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb|redis)://(?:[^@\s:/?#]+(?::[^@\s/?#]*)?@)?[a-zA-Z0-9.\-]+(?:\:\d+)?(?:/[^\s?#]*)?(?:\?[^\s#]*)?",
    "GENERIC_PRIVATE_KEY": r"-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)\s+PRIVATE\s+KEY-----",
    
    # Generic Password
    "GENERIC_PASSWORD": (
        r"(?i)(password|passwd|pwd|secret)['\"]?\s*[:=]\s*['\"]?"
        r"(?!(?:example|test|placeholder|changeme|password|default|sample|none|empty|yourpassword|admin)['\"]?)"
        r"(?=[^'\"]{8,})"
        r"(?=(?:[^A-Z]*[A-Z]))"
        r"(?=(?:[^a-z]*[a-z]))"
        r"(?=(?:[^0-9]*[0-9]))"
        r"[A-Za-z0-9@#$%^&*]{8,}['\"]?"
    )
}

# 2. Personally Identifiable Information (PII)
PII_PATTERNS = {
    "EMAIL_ADDRESS": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "CREDIT_CARD": r"\b(?:4[0-9]{3}([ -]?)\d{4}\1\d{4}\1\d{4}"
                   r"|5[1-5]\d{2}([ -]?)\d{4}\2\d{4}\2\d{4}"
                   r"|3[47]\d{2}([ -]?)\d{6}\3\d{5}"
                   r")\b",
    "PHONE_NUMBER_JP": r"0\d{1,4}-\d{1,4}-\d{4}",
    "IPV4_ADDRESS": r"\b(?:(?:25[0-5]|2[0-4][0-9]|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4][0-9]|1\d{2}|[1-9]?\d)\b"
}

# 3. Ignore Logic (Context Aware)
# Maps programming languages to their comment syntax for suppression
COMMENT_IGNORE_MARKERS = {
    'python': '# sentinel-ignore:',
    'javascript': '// sentinel-ignore:',
    'typescript': '// sentinel-ignore:',
    'java': '// sentinel-ignore:',
    'go': '// sentinel-ignore:',
    'ruby': '# sentinel-ignore:',
    'php': '// sentinel-ignore:',
    'c': '// sentinel-ignore:',
    'cpp': '// sentinel-ignore:',
    'bash': '# sentinel-ignore:',
    'yaml': '# sentinel-ignore:',
    'dockerfile': '# sentinel-ignore:',
    'sql': '-- sentinel-ignore:',
}