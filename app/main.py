"""
ATF Sentinel - GitHub Webhook Server
Main FastAPI application that receives and processes GitHub PR events
Author: ANIRUDH S J
"""
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
import hmac
import hashlib
import logging
import json
from typing import Optional
from app.config import config
from app.github_client import GitHubClient
from app.scanner import run_security_scan
from app.reporter import report_security_issue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ATF Sentinel",
    description="Automated security scanning for GitHub Pull Requests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize GitHub client
try:
    github_client = GitHubClient(config.github_token)
    logger.info("✅ GitHub client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize GitHub client: {e}")
    github_client = None


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 ATF Sentinel starting up...")
   
    # Validate configuration
    if config.validate():
        logger.info("✅ All configuration validated")
    else:
        logger.warning("⚠️ Some configuration issues detected")
   
    logger.info(f"📋 Allowed repos: {config.allowed_repos}")
    logger.info("✅ Application ready to receive webhooks")

@app.get("/")
async def root():
    """Root endpoint - basic service info"""
    return {
        "service": "ATF Sentinel",
        "version": "1.0.0",
        "status": "operational",
        "description": "Automated security scanning for GitHub Pull Requests",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook/github",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
   
    health_status = {
        "status": "healthy",
        "github_client": github_client is not None,
        "secrets_loaded": bool(config.github_token),
        "allowed_repos": len(config.allowed_repos),
        "version": "1.0.0"
    }
   
    # Check if all critical components are working
    if not all([health_status["github_client"], health_status["secrets_loaded"]]):
        health_status["status"] = "degraded"
        return JSONResponse(status_code=503, content=health_status)
   
    return health_status


def verify_github_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC SHA256
    
    This is CRITICAL for security - prevents unauthorized webhook calls!
    
    Args:
        payload: Raw request body (bytes)
        signature: X-Hub-Signature-256 header value
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not signature:
        logger.warning("⚠️ No signature provided in webhook request")
        return False
    
    # GitHub sends signature as "sha256=<hash>"
    if not signature.startswith('sha256='):
        logger.warning("⚠️ Invalid signature format (must start with 'sha256=')")
        return False
    
    # Get webhook secret
    secret = config.webhook_secret
    if not secret:
        logger.error("❌ Webhook secret not configured!")
        return False
    
    # Calculate expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Extract provided signature (remove "sha256=" prefix)
    provided_signature = signature.split('=')[1]
    
    # Compare using constant-time comparison (prevents timing attacks)
    is_valid = hmac.compare_digest(expected_signature, provided_signature)
    
    if not is_valid:
        logger.warning("⚠️ Webhook signature verification FAILED!")
        logger.debug(f"Expected: {expected_signature[:10]}...")
        logger.debug(f"Provided: {provided_signature[:10]}...")
    
    return is_valid


def is_repo_allowed(repo_name: str) -> bool:
    """
    Check if repository is in the allowed list
    
    Supports wildcards:
    - "myorg/*" matches all repos in myorg
    - "myorg/specific-repo" matches exact repo
    
    Args:
        repo_name: Full repo name (e.g., 'octocat/Hello-World')
        
    Returns:
        True if allowed, False otherwise
    """
    allowed_repos = config.allowed_repos
    
    if not allowed_repos:
        logger.warning("⚠️ No allowed repos configured - blocking all")
        return False
    
    for pattern in allowed_repos:
        # Wildcard support (e.g., "myorg/*")
        if pattern.endswith('/*'):
            org = pattern[:-2]
            if repo_name.startswith(f"{org}/"):
                logger.info(f"✅ Repo {repo_name} matches wildcard pattern: {pattern}")
                return True
        
        # Exact match
        elif pattern == repo_name:
            logger.info(f"✅ Repo {repo_name} is explicitly allowed")
            return True
    
    logger.warning(f"⚠️ Repo {repo_name} not in allowed list")
    logger.debug(f"Allowed patterns: {allowed_repos}")
    return False


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint - receives PR events
    
    This is the MAIN endpoint that GitHub calls when PRs are created/updated!
    
    Headers:
        X-Hub-Signature-256: HMAC signature for verification
        X-GitHub-Event: Type of event (pull_request, push, etc.)
        X-GitHub-Delivery: Unique delivery ID
        
    Returns:
        JSON response with processing status
    """
    
    logger.info(f"📨 Received webhook - Event: {x_github_event}, Delivery: {x_github_delivery}")
    
    try:
        # Step 1: Read raw payload (needed for signature verification)
        payload_bytes = await request.body()
        
        # Step 2: Verify signature (SECURITY CHECK!)
        if not verify_github_signature(payload_bytes, x_hub_signature_256):
            logger.error("❌ Invalid webhook signature - rejecting request")
            raise HTTPException(
                status_code=401, 
                detail="Invalid signature - webhook authentication failed"
            )
        
        logger.info("✅ Webhook signature verified")
        
        # Step 3: Parse JSON payload
        try:
            payload = json.loads(payload_bytes.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Step 4: Only process pull_request events
        if x_github_event != "pull_request":
            logger.info(f"⏭️ Ignoring {x_github_event} event (only processing pull_request)")
            return {
                "status": "ignored",
                "reason": f"Event type '{x_github_event}' is not processed",
                "processed_events": ["pull_request"]
            }
        
        # Step 5: Extract PR information
        action = payload.get('action')
        repo_name = payload['repository']['full_name']
        pr_number = payload['number']
        pr_data = payload['pull_request']
        pr_author = pr_data['user']['login']
        pr_title = pr_data['title']
        pr_sha = pr_data['head']['sha']
        pr_url = pr_data['html_url']
        
        logger.info(f"📋 PR Details:")
        logger.info(f"   Repository: {repo_name}")
        logger.info(f"   PR #{pr_number}: {pr_title}")
        logger.info(f"   Author: @{pr_author}")
        logger.info(f"   Action: {action}")
        logger.info(f"   SHA: {pr_sha[:8]}...")
        
        # Step 6: Check if repo is allowed
        if not is_repo_allowed(repo_name):
            logger.warning(f"❌ Repository {repo_name} not authorized")
            raise HTTPException(
                status_code=403,
                detail=f"Repository '{repo_name}' is not in the allowed list"
            )
        
        # Step 7: Only scan on relevant actions
        if action not in ['opened', 'synchronize', 'reopened']:
            logger.info(f"⏭️ Ignoring action '{action}' (only scanning: opened, synchronize, reopened)")
            return {
                "status": "ignored",
                "reason": f"Action '{action}' does not trigger scanning",
                "scanned_actions": ["opened", "synchronize", "reopened"]
            }
        
        # Step 8: Set initial "pending" status
        logger.info("⏳ Setting pending status...")
        github_client.set_commit_status(
            repo_name,
            pr_sha,
            'pending',
            '🔍 Security scan in progress...'
        )
        
        # Step 9: Fetch PR files and diffs
        logger.info(f"📁 Fetching files from PR #{pr_number}...")
        try:
            pr_files = github_client.get_pr_files(repo_name, pr_number)
        except Exception as e:
            logger.error(f"❌ Failed to fetch PR files: {e}")
            github_client.set_commit_status(
                repo_name,
                pr_sha,
                'error',
                '⚠️ Failed to fetch PR files'
            )
            raise HTTPException(status_code=500, detail=f"Failed to fetch PR files: {str(e)}")
        
        if not pr_files:
            logger.warning(f"⚠️ No text files to scan in PR #{pr_number}")
            github_client.set_commit_status(
                repo_name,
                pr_sha,
                'success',
                '✅ No files to scan'
            )
            return {
                "status": "success",
                "message": "No text files to scan",
                "pr": pr_number,
                "repo": repo_name
            }
        
        logger.info(f"✅ Found {len(pr_files)} files to scan")
        
        # Step 10: Run security scan
        logger.info("🔍 Running security scan...")
        metadata = {
            "repo": repo_name,
            "branch": pr_data['head']['ref'],
            "author": pr_author,
            "pr_url": pr_url
        }
        
        try:
            scan_result = run_security_scan(pr_files, metadata)
        except Exception as e:
            logger.error(f"❌ Scanner failed: {e}")
            github_client.set_commit_status(
                repo_name,
                pr_sha,
                'error',
                '⚠️ Scanner error'
            )
            raise HTTPException(status_code=500, detail=f"Scanner error: {str(e)}")
        
        # Step 11: Process scan results
        action_taken = scan_result.get('action', 'PASS')
        severity = scan_result.get('severity', 'low')
        issues_count = len(scan_result.get('issues', []))
        
        logger.info(f"📊 Scan Results: {action_taken} | Severity: {severity} | Issues: {issues_count}")
        
        # Step 12: Set commit status based on results
        if action_taken == 'BLOCK':
            github_client.set_commit_status(
                repo_name,
                pr_sha,
                'failure',
                f'🚫 Security issues found ({issues_count} critical)'
            )
            status_code = 'failure'
        elif action_taken == 'WARN':
            github_client.set_commit_status(
                repo_name,
                pr_sha,
                'success',
                f'⚠️ Warnings found ({issues_count} issues)'
            )
            status_code = 'success'
        else:
            github_client.set_commit_status(
                repo_name,
                pr_sha,
                'success',
                '✅ Security scan passed'
            )
            status_code = 'success'
        
        # Step 13: Send Slack notification if issues found
        if action_taken in ['BLOCK', 'WARN'] and issues_count > 0:
            logger.info("📢 Sending Slack notification...")
            try:
                report_security_issue(scan_result, pr_url)
            except Exception as e:
                logger.error(f"⚠️ Failed to send Slack notification: {e}")
                # Don't fail the entire webhook if Slack fails
        
        logger.info(f"✅ Successfully processed PR #{pr_number}")
        
        return {
            "status": "success",
            "message": "Security scan completed",
            "repo": repo_name,
            "pr": pr_number,
            "author": pr_author,
            "scan_result": {
                "action": action_taken,
                "severity": severity,
                "issues_count": issues_count,
                "status": status_code
            },
            "files_scanned": len(pr_files)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"❌ Unexpected error processing webhook: {e}", exc_info=True)
        
        # Try to set error status if we have the info
        try:
            if 'repo_name' in locals() and 'pr_sha' in locals():
                github_client.set_commit_status(
                    repo_name,
                    pr_sha,
                    'error',
                    '⚠️ Internal error during scan'
                )
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


# For local testing
if __name__ == "__main__":
    import uvicorn
   
    print("\n" + "="*70)
    print("🚀 Starting ATF Sentinel locally...")
    print("="*70)
    print(f"\n📍 Server will run at: http://localhost:8000")
    print(f"📖 API docs at: http://localhost:8000/docs")
    print(f"💚 Health check: http://localhost:8000/health")
    print("\n" + "="*70 + "\n")
   
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )