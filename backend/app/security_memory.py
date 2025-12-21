# backend/app/security_memory.py
import json
import os
import logging
from collections import Counter

logger = logging.getLogger(__name__)
MEMORY_FILE = "security_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_memory(data):
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save security memory: {e}")

def get_engineer_profile(author_name):
    """
    Returns the CONTEXT STRING for the AI (e.g. 'History of SQLi...').
    """
    if not author_name:
        return ""
        
    data = load_memory()
    profile = data.get(author_name, {
        "risk_score": 0,
        "common_issues": [],
        "scan_count": 0
    })
    
    if profile["scan_count"] > 0:
        issues_str = ", ".join(profile["common_issues"])
        return f"ENGINEER CONTEXT: This author has a history of {issues_str} issues. Risk Score: {profile['risk_score']}/100. Be extra vigilant."
    
    return "ENGINEER CONTEXT: New contributor. Perform standard audit."

# --- NEW FUNCTION FOR DASHBOARD/TESTS ---
def get_profile_data(author_name):
    """
    Returns the RAW DICTIONARY (e.g. {'risk_score': 10}) for analytics.
    """
    data = load_memory()
    return data.get(author_name, {
        "risk_score": 0,
        "common_issues": [],
        "scan_count": 0
    })

def update_engineer_profile(author_name, issues_found):
    """
    Updates the risk profile based on scan results.
    """
    if not author_name:
        return

    data = load_memory()
    profile = data.get(author_name, {
        "risk_score": 0,
        "common_issues": [],
        "issue_history": [],
        "scan_count": 0
    })

    profile["scan_count"] += 1
    
    if issues_found:
        profile["risk_score"] = min(100, profile["risk_score"] + (len(issues_found) * 10))
        current_issues = [issue.get('type', 'Unknown') for issue in issues_found]
        profile["issue_history"].extend(current_issues)
        counts = Counter(profile["issue_history"])
        profile["common_issues"] = [item[0] for item in counts.most_common(3)]
    else:
        profile["risk_score"] = max(0, profile["risk_score"] - 5)

    data[author_name] = profile
    save_memory(data)