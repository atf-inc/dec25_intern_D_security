# app/email_client.py

import os
import logging
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timezone, timedelta

# Try to load custom configuration
try:
    from app.config import config
except ImportError:
    config = None

load_dotenv()
logger = logging.getLogger(__name__)

# Load SendGrid configuration
# 1. Try environment variables first (for local testing)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

# 2. If not in environment, try Secret Manager (for production)
if not SENDGRID_API_KEY and config:
    try:
        SENDGRID_API_KEY = config.get_secret('sendgrid-api-key')
    except Exception as e:
        logger.warning(f"Failed to load SendGrid API key from Secret Manager: {e}")
        logger.info("💡 Tip: Set SENDGRID_API_KEY environment variable for local testing")

if not FROM_EMAIL and config:
    try:
        FROM_EMAIL = config.get_secret('from-email')
    except Exception as e:
        logger.warning(f"Failed to load FROM_EMAIL from Secret Manager: {e}")
        logger.info("💡 Tip: Set FROM_EMAIL environment variable for local testing")


def send_security_email(recipient: str, alert_data: dict) -> bool:
    """
    Send security alert email with formatting matching Slack alerts.
    
    Args:
        recipient (str): Email address to send the alert to.
        alert_data (dict): Alert information containing incident details.
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        logger.error("❌ SendGrid not configured (missing API key or FROM_EMAIL)")
        return False

    # Extract and validate data
    pr_url = alert_data.get('pr_url', '#')
    severity = alert_data.get('severity', 'high').lower()
    action = alert_data.get('action', 'REVIEW').upper()
    issues_count = alert_data.get('issues_count', 0)
    repo = alert_data.get('repo', 'Unknown Repository')
    branch = alert_data.get('branch', 'Unknown Branch')
    author = alert_data.get('author', 'Unknown Author')
    incident = alert_data.get('incident', 'Security Policy Violation')
    
    # Get timestamp
    time_str = alert_data.get('time')
    if not time_str:
        now_utc = datetime.now(timezone.utc)
        now_ist = now_utc + timedelta(hours=5, minutes=30)
        time_str = f"{now_ist.strftime('%Y-%m-%d')} | {now_ist.strftime('%H:%M:%S IST')}"
    
    # Severity configuration
    severity_config = {
        'critical': {
            'indicator': '🔴',
            'label': 'CRITICAL',
            'color': '#DC143C',
            'bg_color': '#FFF0F0'
        },
        'high': {
            'indicator': '🟠',
            'label': 'HIGH',
            'color': '#FF8C00',
            'bg_color': '#FFF5E6'
        },
        'medium': {
            'indicator': '🟡',
            'label': 'MEDIUM',
            'color': '#FFD700',
            'bg_color': '#FFFEF0'
        },
        'low': {
            'indicator': '🟢',
            'label': 'LOW',
            'color': '#32CD32',
            'bg_color': '#F0FFF0'
        }
    }
    
    sev = severity_config.get(severity, severity_config['high'])
    
    # Action status mapping
    action_status_map = {
        'BLOCK': '🚫 Merge Blocked',
        'PASS': '✅ Passed',
        'REVIEW': '⚠️ Review Required'
    }
    action_status = action_status_map.get(action, '📋 Manual Review')
    
    # Email subject
    subject = f"🛡️ [ATF Sentinel] {action} — {severity.upper()} — {repo}"
    
    # Get summaries and details
    summary_jp = alert_data.get('summary_jp', 'N/A')
    summary_en = alert_data.get('summary_en', 'N/A')
    fix = alert_data.get('fix', 'Refer to security guidelines.')
    diff = alert_data.get('diff', 'N/A')
    issues_summary = alert_data.get('issues_summary', '')
    
    # Truncate long content for email
    if len(fix) > 1000:
        fix = fix[:997] + "..."
    if len(diff) > 1500:
        diff = diff[:1497] + "..."
    
    # ---------- TEXT VERSION ----------
    text_content = f"""
🛡️ ATF Sentinel Security Alert
{'=' * 60}

SEVERITY: {sev['indicator']} {sev['label']}
STATUS:   {action_status}

{'=' * 60}
🚨 INCIDENT
{incident}

{'=' * 60}
📋 REPOSITORY DETAILS

Repository : {repo}
Branch     : {branch}
Author     : {author}
Time       : {time_str}

{'=' * 60}
⚠️ ISSUES DETECTED

{issues_count} security issue(s) found

{issues_summary if issues_summary else 'See details below.'}

{'=' * 60}
📊 IMPACT ASSESSMENT (JP)

{summary_jp}

{'=' * 60}
📊 IMPACT ASSESSMENT (EN)

{summary_en}

{'=' * 60}
🔧 RECOMMENDED FIX

{fix}

{'=' * 60}
📝 CODE CHANGES

{diff}

{'=' * 60}
🔗 ACTIONS

View Pull Request: {pr_url}
Security Guidelines: https://aitf.co.jp/security/

{'=' * 60}
🤖 Automated by ATF Sentinel | Security Scanning System
"""

    # ---------- HTML VERSION ----------
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .severity-badge {{
            display: inline-block;
            background-color: {sev['bg_color']};
            color: {sev['color']};
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 16px;
            margin: 20px 0;
            border: 2px solid {sev['color']};
        }}
        .status-badge {{
            display: inline-block;
            background-color: #f0f0f0;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 16px;
            margin: 20px 0 20px 10px;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #444;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
        }}
        .info-item {{
            background-color: #f8f9fa;
            padding: 12px;
            border-radius: 4px;
        }}
        .info-label {{
            font-weight: 600;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .info-value {{
            color: #333;
            font-size: 14px;
            font-family: monospace;
        }}
        .code-block {{
            background-color: #f5f5f5;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .issues-count {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .button-container {{
            margin-top: 30px;
            text-align: center;
        }}
        .button {{
            display: inline-block;
            padding: 14px 28px;
            margin: 0 10px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            transition: transform 0.2s;
        }}
        .button:hover {{
            transform: translateY(-2px);
        }}
        .button-primary {{
            background-color: {sev['color']};
            color: white;
        }}
        .button-secondary {{
            background-color: #6c757d;
            color: white;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
        .divider {{
            height: 1px;
            background-color: #e0e0e0;
            margin: 25px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ ATF Sentinel Security Alert</h1>
        </div>
        
        <div class="content">
            <div style="text-align: center;">
                <span class="severity-badge">{sev['indicator']} {sev['label']} SEVERITY</span>
                <span class="status-badge">{action_status}</span>
            </div>
            
            <div class="divider"></div>
            
            <div class="section">
                <div class="section-title">🚨 Incident</div>
                <p>{incident}</p>
            </div>
            
            <div class="section">
                <div class="section-title">📋 Repository Details</div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Repository</div>
                        <div class="info-value">{repo}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Branch</div>
                        <div class="info-value">{branch}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Author</div>
                        <div class="info-value">{author}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Time</div>
                        <div class="info-value">{time_str}</div>
                    </div>
                </div>
            </div>
            
            {f'''
            <div class="section">
                <div class="issues-count">
                    ⚠️ <strong>{issues_count} security issue(s) found</strong>
                </div>
                {f'<div class="code-block">{issues_summary}</div>' if issues_summary else ''}
            </div>
            ''' if issues_count > 0 else ''}
            
            <div class="divider"></div>
            
            <div class="section">
                <div class="section-title">📊 Impact Assessment (JP)</div>
                <p>{summary_jp}</p>
            </div>
            
            <div class="section">
                <div class="section-title">📊 Impact Assessment (EN)</div>
                <p>{summary_en}</p>
            </div>
            
            <div class="divider"></div>
            
            <div class="section">
                <div class="section-title">🔧 Recommended Fix</div>
                <div class="code-block">{fix}</div>
            </div>
            
            <div class="section">
                <div class="section-title">📝 Code Changes</div>
                <div class="code-block">{diff}</div>
            </div>
            
            <div class="button-container">
                <a href="{pr_url}" class="button button-primary">🔗 View Pull Request</a>
                <a href="https://aitf.co.jp/security/" class="button button-secondary">📚 Security Guidelines</a>
            </div>
        </div>
        
        <div class="footer">
            🤖 Automated by ATF Sentinel | Security Scanning System
        </div>
    </div>
</body>
</html>
"""

    # Create and send email
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=recipient,
        subject=subject,
        plain_text_content=text_content,
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"✅ Security email sent to {recipient} (Status: {response.status_code})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send security email: {str(e)}")
        return False


def send_simple_email_notification(recipient: str, message: str, severity: str = "info") -> bool:
    """
    Send a simple text notification email.
    
    Args:
        recipient (str): Email address to send to
        message (str): Notification message
        severity (str): Severity level (info, warning, error, success)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        logger.error("❌ SendGrid not configured")
        return False
    
    emoji_map = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅"
    }
    emoji = emoji_map.get(severity, "📢")
    
    subject = f"{emoji} ATF Sentinel Notification"
    
    text_content = f"{emoji} {message}\n\n— ATF Sentinel"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="padding: 20px; background-color: #f5f5f5; border-radius: 8px;">
            <h3>{emoji} ATF Sentinel Notification</h3>
            <p>{message}</p>
            <hr>
            <p style="font-size: 12px; color: #777;">
                🤖 Automated by ATF Sentinel
            </p>
        </div>
    </body>
    </html>
    """
    
    mail = Mail(
        from_email=FROM_EMAIL,
        to_emails=recipient,
        subject=subject,
        plain_text_content=text_content,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mail)
        logger.info(f"✅ Email notification sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send email notification: {e}")
        return False