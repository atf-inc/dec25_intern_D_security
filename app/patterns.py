# app/patterns.py

# 1. High-Entropy Secrets (The "Block Immediately" List)
SECRET_PATTERNS = {
    # AWS
    "AWS_ACCESS_KEY_ID": r"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])",
    "AWS_SECRET_ACCESS_KEY": r"(?i)aws_secret_access_key['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9\/+=]{40}['\"]?",
    
    # Google / Firebase
    "GOOGLE_API_KEY": r"AIza[0-9A-Za-z\\-_]{35}",
    "GCP_PRIVATE_KEY_ID": r"private_key_id['\"]?:\s*['\"]?[a-f0-9]{40}['\"]?",
    
    # Platforms
    "GITHUB_TOKEN": r"(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36}",
    "SLACK_WEBHOOK": r"https://hooks\.slack\.com/services/T[A-Z0-9]{8,12}/B[A-Z0-9]{8,12}/[A-Z0-9]{24}",
    "SLACK_BOT_TOKEN": r"xoxb-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24}",
    
    # Database & Crypto
    "DB_CONNECTION_STRING": r"(?i)(postgres|mysql|mongodb|redis)://[a-zA-Z0-9_]+:[a-zA-Z0-9_]+@[a-zA-Z0-9.-]+",
    "GENERIC_PRIVATE_KEY": r"-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)\s+PRIVATE\s+KEY-----",
    
    # Generic "Password =" assignments (High risk of false positives, handled carefully)
    "GENERIC_PASSWORD": r"(?i)(password|passwd|pwd|secret)['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9@#$%^&*]{8,}['\"]?"
}

# 2. Personally Identifiable Information (PII)
PII_PATTERNS = {
    "EMAIL_ADDRESS": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
    "PHONE_NUMBER_JP": r"0\d{1,4}-\d{1,4}-\d{4}",
    "IPV4_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b" # Detects hardcoded IP addresses
}

# 3. Whitelist Marker
IGNORE_MARKER = "# test-data"