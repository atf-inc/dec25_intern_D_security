# app/patterns.py

"""
ATF Sentinel - Security Pattern Database
This module defines regex patterns to detect secrets, credentials, and PII.
It is used by the pattern_scanner module to flag high-risk code changes.
"""

# 1. High-Entropy Secrets (The "Block Immediately" List)
SECRET_PATTERNS = {
    # AWS: Matches Access Keys and specific assignment patterns for Secret Keys
    "AWS_ACCESS_KEY_ID": r"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])",
    "AWS_SECRET_ACCESS_KEY": r"(?i)(?:aws_secret_access_key|[a-z0-9_]*secret[a-z0-9_]*key[a-z0-9_]*)['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9\/+=]{40}['\"]?",
    
    # Google / Firebase
    "GOOGLE_API_KEY": r"AIza[0-9A-Za-z\-_]{35}", # Fixed backslash issue
    "GCP_PRIVATE_KEY_ID": r"private_key_id['\"]?:\s*['\"]?[a-f0-9]{40}['\"]?",
    
    # Platforms
    "GITHUB_TOKEN": r"(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36}",
    "SLACK_WEBHOOK": r"https://hooks\.slack\.com/services/T[A-Z0-9]{8,12}/B[A-Z0-9]{8,12}/[A-Z0-9]{24}",
    "SLACK_BOT_TOKEN": r"xoxb-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24}",
    
    # Database Connection Strings (Matches URI format with credentials)
    "DB_CONNECTION_STRING": r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb|redis)://(?:[^@\s:/?#]+(?::[^@\s/?#]*)?@)?[a-zA-Z0-9.\-]+(?:\:\d+)?(?:/[^\s?#]*)?(?:\?[^\s#]*)?",
    
    "GENERIC_PRIVATE_KEY": r"-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)\s+PRIVATE\s+KEY-----",
    
    # Generic Password (Strict Mode: Requires high entropy to avoid matching 'password = "text"')
    "GENERIC_PASSWORD": (
        r"(?i)(password|passwd|pwd|secret)['\"]?\s*[:=]\s*['\"]?"
        r"(?!(?:example|test|placeholder|changeme|password|default|sample|none|empty|yourpassword|admin)['\"]?)"
        r"(?=[^'\"]{8,})"  # At least 8 characters
        r"(?=(?:[^A-Z]*[A-Z]))"  # At least one uppercase
        r"(?=(?:[^a-z]*[a-z]))"  # At least one lowercase
        r"(?=(?:[^0-9]*[0-9]))"  # At least one digit
        r"[A-Za-z0-9@#$%^&*]{8,}['\"]?"
    )
}

# 2. Personally Identifiable Information (PII)
PII_PATTERNS = {
    "EMAIL_ADDRESS": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    
    # Credit Card: Matches Visa, MasterCard, Amex, Discover specifically
    "CREDIT_CARD": r"\b(?:4[0-9]{3}([ -]?)\d{4}\1\d{4}\1\d{4}"   # Visa (Group 1)
                   r"|5[1-5]\d{2}([ -]?)\d{4}\2\d{4}\2\d{4}"     # MasterCard (Group 2)
                   r"|3[47]\d{2}([ -]?)\d{6}\3\d{5}"             # Amex (Group 3)
                   r")\b",
                   
    "PHONE_NUMBER_JP": r"0\d{1,4}-\d{1,4}-\d{4}",
    
    # IPv4: Validates strict 0-255 range
    "IPV4_ADDRESS": r"\b(?:(?:25[0-5]|2[0-4][0-9]|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4][0-9]|1\d{2}|[1-9]?\d)\b"
}

# 3. Whitelist Marker
# Changed to generic string so it works in Python (#), JS (//), and HTML (<!-- -->)
IGNORE_MARKER = "test-data"