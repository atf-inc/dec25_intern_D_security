import re
from dataclasses import dataclass
from typing import List, Pattern
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"


class Category(Enum):
    CLOUD_CREDENTIAL = "cloud_credential"
    TOKEN = "token"
    CRYPTOGRAPHIC_MATERIAL = "cryptographic_material"


@dataclass(frozen=True)
class DetectionPattern:
    id: str
    name: str
    pattern: Pattern
    severity: Severity
    category: Category
    description: str


# ===============================
# Cloud Provider Credentials
# ===============================

AWS_ACCESS_KEY_ID = DetectionPattern(
    id="aws_access_key_id",
    name="AWS Access Key ID",
    pattern=re.compile(r"AKIA[0-9A-Z]{16}"),
    severity=Severity.CRITICAL,
    category=Category.CLOUD_CREDENTIAL,
    description="AWS Access Key ID with fixed prefix"
)

GCP_API_KEY = DetectionPattern(
    id="gcp_api_key",
    name="GCP API Key",
    pattern=re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    severity=Severity.CRITICAL,
    category=Category.CLOUD_CREDENTIAL,
    description="Google Cloud API key"
)

AZURE_CLIENT_SECRET = DetectionPattern(
    id="azure_client_secret",
    name="Azure Client Secret",
    pattern=re.compile(r"client_secret\s*[=:]\s*['\"]?[A-Za-z0-9~._-]{34,40}['\"]?", re.IGNORECASE),
    severity=Severity.CRITICAL,
    category=Category.CLOUD_CREDENTIAL,
    description="Azure AD client secret (context-sensitive)"
)


# ===============================
# Developer Platform Tokens
# ===============================

GITHUB_PAT = DetectionPattern(
    id="github_pat",
    name="GitHub Personal Access Token",
    pattern=re.compile(r"ghp_[0-9A-Za-z]{36}"),
    severity=Severity.CRITICAL,
    category=Category.TOKEN,
    description="GitHub Personal Access Token"
)

GITHUB_OAUTH = DetectionPattern(
    id="github_oauth",
    name="GitHub OAuth Token",
    pattern=re.compile(r"gho_[0-9A-Za-z]{36}"),
    severity=Severity.CRITICAL,
    category=Category.TOKEN,
    description="GitHub OAuth Access Token"
)


# ===============================
# Cryptographic Material
# ===============================

PRIVATE_KEY_HEADER = DetectionPattern(
    id="private_key_header",
    name="Private Key Header",
    pattern=re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    severity=Severity.CRITICAL,
    category=Category.CRYPTOGRAPHIC_MATERIAL,
    description="Private key file header"
)


ALL_PATTERNS: List[DetectionPattern] = [
    AWS_ACCESS_KEY_ID,
    GCP_API_KEY,
    AZURE_CLIENT_SECRET,
    GITHUB_PAT,
    GITHUB_OAUTH,
    PRIVATE_KEY_HEADER,
]
