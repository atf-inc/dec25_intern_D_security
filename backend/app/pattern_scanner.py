# backend/app/pattern_scanner.py

import re
import logging
from app.patterns import SECRET_PATTERNS, PII_PATTERNS, COMMENT_IGNORE_MARKERS

logger = logging.getLogger(__name__)

def should_ignore_line(file_path: str, line_content: str) -> bool:
    """
    Checks if a line contains a valid 'sentinel-ignore' comment 
    appropriate for the file's language.
    """
    # 1. Determine Language from Extension
    ext = file_path.lower().split('.')[-1] if '.' in file_path else ''
    
    ext_to_lang = {
        'py': 'python', 'js': 'javascript', 'jsx': 'javascript', 
        'ts': 'typescript', 'tsx': 'typescript', 'java': 'java', 
        'go': 'go', 'rb': 'ruby', 'php': 'php', 'c': 'c', 
        'cpp': 'cpp', 'sh': 'bash', 'yaml': 'yaml', 'yml': 'yaml', 
        'dockerfile': 'dockerfile', 'sql': 'sql'
    }
    
    lang = ext_to_lang.get(ext, 'python') # Default to python
    
    # 2. Get the marker for that language
    marker = COMMENT_IGNORE_MARKERS.get(lang, '# sentinel-ignore:')
    
    # 3. Check if line contains the marker
    if marker in line_content:
        return True
        
    return False

def scan_diff_for_patterns(diff_text, filename="unknown"):
    """
    Scans the git diff for regex matches (Secrets & PII).
    Accepts filename to determine correct ignore-comment syntax.
    """
    found_issues = []
    
    if not diff_text:
        return []

    ALL_PATTERNS = {**SECRET_PATTERNS, **PII_PATTERNS}
    lines = diff_text.split('\n')

    for line_num, line in enumerate(lines):
        # 1. Skip Metadata and Binary file warnings
        if line.startswith('Binary files'):
            continue

        # 2. Only check added lines
        if not line.startswith('+') or line.startswith('+++'):
            continue

        # 3. CHECK WHITELIST: Use context-aware ignore logic
        if should_ignore_line(filename, line):
            continue

        # 4. Clean the line
        clean_line = line[1:]
        
        # 5. Run Regex
        for rule_name, pattern in ALL_PATTERNS.items():
            try:
                if re.search(pattern, clean_line):
                    severity = "CRITICAL" if rule_name in SECRET_PATTERNS else "HIGH"
                    
                    issue = {
                        "type": "Pattern Violation",
                        "severity": severity,
                        "rule": rule_name,
                        "line": line_num + 1,
                        "description": f"Detected potential {rule_name}",
                    }

                    if rule_name in SECRET_PATTERNS:
                        issue["fix_code"] = "Use Environment Variables (os.environ) instead of hardcoding."
                    
                    found_issues.append(issue)

            except re.error as e:
                logger.error(f"Regex error in rule {rule_name}: {e}")
                continue

    return found_issues