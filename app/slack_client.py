# app/slack_client.py

import requests
import logging
import os

# Try to load custom configuration
try:
    from app.config import config
except ImportError:
    config = None

logger = logging.getLogger(__name__)

# Load Slack webhook URL
# 1. Try environment variable first (for local testing)
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

# 2. If not in environment, try Secret Manager (for production)
if not SLACK_WEBHOOK_URL and config:
    try:
        SLACK_WEBHOOK_URL = config.get_secret('SLACK_WEBHOOK_URL')
    except Exception as e:
        logger.warning(f"Failed to load Slack webhook from Secret Manager: {e}")
        logger.info("💡 Tip: Set SLACK_WEBHOOK_URL environment variable for local testing")


def send_slack_alert(alert_data: dict) -> bool:
    """
    Send security alert to Slack using Block Kit format.
    
    Args:
        alert_data (dict): Alert information containing incident details.
    
    Returns:
        bool: True if alert sent successfully, False otherwise
    """
    if not SLACK_WEBHOOK_URL:
        logger.error("❌ Slack webhook URL not configured")
        return False
    
    # Extract and validate data
    pr_url = alert_data.get('pr_url', '#')
    severity = alert_data.get('severity', 'high').lower()
    action = alert_data.get('action', 'REVIEW').upper()
    issues_count = alert_data.get('issues_count', 0)
    
    # Severity configuration
    severity_config = {
        'critical': {
            'indicator': '🔴',
            'label': 'CRITICAL',
            'style': 'danger',
            'color': '#DC143C'
        },
        'high': {
            'indicator': '🟠',
            'label': 'HIGH',
            'style': 'danger',
            'color': '#FF8C00'
        },
        'medium': {
            'indicator': '🟡',
            'label': 'MEDIUM',
            'style': 'warning',
            'color': '#FFD700'
        },
        'low': {
            'indicator': '🟢',
            'label': 'LOW',
            'style': 'primary',
            'color': '#32CD32'
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
    
    # Build Slack Block Kit payload
    blocks = [
        # Header
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🛡️ ATF Sentinel Security Alert",
                "emoji": True
            }
        },
        # Severity and Status
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Severity*\n{sev['indicator']} {sev['label']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status*\n{action_status}"
                }
            ]
        },
        {"type": "divider"},
        # Incident Description
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🚨 Incident*\n{alert_data.get('incident', 'Security Policy Violation')}"
            }
        },
        # Repository Details
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Repository*\n`{alert_data.get('repo', 'N/A')}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Branch*\n`{alert_data.get('branch', 'N/A')}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Author*\n{alert_data.get('author', 'Unknown')}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Time*\n{alert_data.get('time', 'N/A')}"
                }
            ]
        }
    ]
    
    # Add issues count if available
    if issues_count > 0:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Issues Detected*\n:warning: {issues_count} security issue(s) found"
            }
        })
    
    blocks.append({"type": "divider"})
    
    # Impact Assessment
    blocks.extend([
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📊 Impact Assessment (JP)*\n{alert_data.get('summary_jp', 'N/A')}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📊 Impact Assessment (EN)*\n{alert_data.get('summary_en', 'N/A')}"
            }
        },
        {"type": "divider"}
    ])
    
    # Recommended Fix
    fix_text = alert_data.get('fix', 'N/A')
    if len(fix_text) > 500:
        fix_text = fix_text[:497] + "..."
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*🔧 Recommended Fix*\n```{fix_text}```"
        }
    })
    
    # Code Diff
    diff_text = alert_data.get('diff', 'N/A')
    if len(diff_text) > 1000:
        diff_text = diff_text[:997] + "..."
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*📝 Code Changes*\n```{diff_text}```"
        }
    })
    
    # Action Buttons
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🔗 View Pull Request",
                    "emoji": True
                },
                "url": pr_url,
                "style": sev['style']
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Security Guidelines",
                    "emoji": False
                },
                "url": "https://aitf.co.jp/security/"
            }
        ]
    })
    
    # Footer context
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "🤖 Automated by ATF Sentinel | Security Scanning System"
            }
        ]
    })
    
    # Send to Slack
    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json={"blocks": blocks},
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        logger.info(f"✅ Slack alert sent successfully (Status: {response.status_code})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send Slack alert: {str(e)}")
        return False


def send_simple_notification(message: str, severity: str = "info") -> bool:
    """
    Send a simple text notification to Slack.
    """
    if not SLACK_WEBHOOK_URL:
        return False
    
    emoji_map = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅"
    }
    emoji = emoji_map.get(severity, "📢")
    
    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} {message}"
                }
            }
        ]
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}")
        return False