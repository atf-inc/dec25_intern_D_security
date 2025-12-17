# app/pattern_scanner.py

import re
import logging
from app.patterns import SECRET_PATTERNS, PII_PATTERNS, IGNORE_MARKER

# Setup logging
logger = logging.getLogger(__name__)

def scan_diff_for_patterns(diff_text):
    """
    Scans the git diff for regex matches (Secrets & PII).
    
    Logic:
    - Only looks at added lines (lines starting with '+').
    - Ignores lines that contain the IGNORE_MARKER.
    - Skips metadata and binary file warnings.

    Returns:
        list of dict: A list of found issues with type, severity, rule, line, and description.
    """
    found_issues = []
    
    # Safety Check: If diff is empty or None, return empty list
    if not diff_text:
        return []

    # Combine both dictionaries to check everything at once
    ALL_PATTERNS = {**SECRET_PATTERNS, **PII_PATTERNS}

    # Split the diff into lines to check line-by-line
    lines = diff_text.split('\n')

    for line_num, line in enumerate(lines):
        # 1. Skip Metadata and Binary file warnings
        if line.startswith('Binary files'):
            continue

        # 2. Only check added lines (Git diffs start added lines with +)
        # We also skip lines starting with '+++' (File headers)
        if not line.startswith('+') or line.startswith('+++'):
            continue

        # 3. CHECK WHITELIST: If developer marked it as test data, skip it.
        if IGNORE_MARKER in line:
            continue

        # 4. Clean the line (remove the first '+') for accurate scanning
        clean_line = line[1:]
        
        # 5. Run Regex
        for rule_name, pattern in ALL_PATTERNS.items():
            try:
                if re.search(pattern, clean_line):
                    # Determine Severity
                    severity = "CRITICAL" if rule_name in SECRET_PATTERNS else "HIGH"
                    
                    # Create the issue object
                    issue = {
                        "type": "Pattern Violation",
                        "severity": severity,
                        "rule": rule_name,
                        "line": line_num + 1,
                        "description": f"Detected potential {rule_name}",
                    }

                    # Smart Fix Logic: Only suggest env vars for Secrets
                    if rule_name in SECRET_PATTERNS:
                        issue["fix_code"] = "Use Environment Variables (os.environ) instead of hardcoding."
                    
                    found_issues.append(issue)

            except re.error as e:
                # Log the error but continue scanning other patterns
                logger.error(f"Regex error in rule {rule_name}: {e}")
                continue

    return found_issues