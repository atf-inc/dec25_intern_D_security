# app/reporter.py

import os
import logging
from datetime import datetime, timezone, timedelta
from app.slack_client import send_slack_alert
from app.email_client import send_security_email

logger = logging.getLogger(__name__)

# Security admin email - receives all security alerts
# Set SECURITY_ADMIN_EMAIL env var to receive email notifications
SECURITY_ADMIN_EMAIL = os.getenv("SECURITY_ADMIN_EMAIL")

def report_security_issue(scan_result: dict, pr_url: str | None = None):
    """
    Formats scan results and sends a Slack alert.
    
    Args:
        scan_result (dict): Result from app.scanner.run_security_scan containing:
            - incident, summary_en, summary_jp
            - action, severity, fix, diff
            - repo, branch, author (from metadata)
            - issues: list of detected vulnerabilities
        pr_url (str, optional): Pull Request URL
    
    Returns:
        bool: True if alert sent successfully, False otherwise
    """
    # Skip reporting if action is PASS and no critical issues
    action = scan_result.get("action", "PASS")
    severity = scan_result.get("severity", "low")
    
    if action == "PASS" and severity in ["low", "info"]:
        logger.info("✅ Scan passed with no issues. Skipping Slack notification.")
        return True
    
    # Use PR URL from metadata if not provided
    final_pr_url = pr_url or scan_result.get("pr_url", "https://github.com/atf-inc/dec25_intern_D_security/pulls")
    
    # Get current time in IST and JST
    now_utc = datetime.now(timezone.utc)
    ist_offset = timedelta(hours=5, minutes=30)
    jst_offset = timedelta(hours=9)
    
    now_ist = now_utc + ist_offset
    now_jst = now_utc + jst_offset
    
    # Format timestamps - single date with both times
    date_str = now_ist.strftime("%Y-%m-%d")
    time_ist = now_ist.strftime("%H:%M:%S IST")
    time_jst = now_jst.strftime("%H:%M:%S JST")
    time_display = f"{date_str} | {time_ist} / {time_jst}"
    
    # Build alert payload
    alert_data = {
        "repo": scan_result.get("repo", "Unknown Repository"),
        "branch": scan_result.get("branch", "Unknown Branch"),
        "time": time_display,
        "author": scan_result.get("author", "Unknown Author"),
        "incident": scan_result.get("incident", "Security Policy Violation"),
        "summary_en": scan_result.get("summary_en", "Security concerns detected in code changes."),
        "summary_jp": scan_result.get("summary_jp", "コード変更にセキュリティ上の懸念が検出されました。"),
        "action": action,
        "fix": scan_result.get("fix", "Please review security guidelines and remediate vulnerabilities."),
        "diff": scan_result.get("diff", "No code diff available.")[:1000],  # Limit diff size
        "severity": severity,
        "pr_url": final_pr_url,
        "issues_count": len(scan_result.get("issues", [])),
        "issues_summary": format_issues_summary(scan_result.get("issues", [])),
    }
    
    try:
        logger.info(f"🚨 Reporting security issue: {alert_data['incident']}")
        logger.info(f"   Severity: {severity.upper()} | Action: {action}")

        success = send_slack_alert(alert_data)

        # Send email alerts for BLOCK and WARN actions
        if action in ["BLOCK", "WARN"]:
            # Always send to security admin
            if SECURITY_ADMIN_EMAIL:
                logger.info(f"📧 Sending email alert to security admin: {SECURITY_ADMIN_EMAIL}")
                send_security_email(SECURITY_ADMIN_EMAIL, scan_result)
            
            # Also send to PR author if they have a valid email (not GitHub noreply)
            author_email = scan_result.get("author_email")
            if author_email and "noreply" not in author_email.lower():
                if author_email != SECURITY_ADMIN_EMAIL:  # Avoid duplicate
                    logger.info(f"📧 Sending email alert to author: {author_email}")
                    send_security_email(author_email, scan_result)

        return success

        
    except Exception as e:
        logger.error(f"❌ Failed to send Slack alert: {str(e)}")
        return False


def format_issues_summary(issues: list) -> str:
    """
    Format issues list into readable summary.
    
    Args:
        issues (list): List of issue dictionaries
    
    Returns:
        str: Formatted summary string
    """
    if not issues:
        return "No specific issues detected."
    
    summary_lines = []
    for idx, issue in enumerate(issues, 1):
        file = issue.get('file', 'unknown')
        pattern = issue.get('pattern', 'unknown')
        summary_lines.append(f"{idx}. {file}: {pattern}")
    
    return "\n".join(summary_lines)
