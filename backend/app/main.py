"""
ATF Sentinel - GitHub Webhook Server
Main FastAPI application that receives and processes GitHub PR events
Author: ANIRUDH S J
"""
from fastapi import FastAPI, Request, Header, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import hmac
import hashlib
import logging
import json
import uuid
from typing import Optional, List

from app.config import config
from app.github_client import GitHubClient
from app.scanner import run_security_scan
from app.reporter import report_security_issue
from app.database import get_db, init_engine, create_tables, check_database_health
from app.models import (
    ScanResult, SecurityIssue, Repository, Engineer, DailyMetrics,
    ScanAction, Severity
)

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
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        config.frontend_url,
        "http://localhost:3000",
        "https://*.run.app",  # Cloud Run URLs
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    
    # Initialize database
    try:
        init_engine()
        create_tables()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
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
        "version": "2.0.0",
        "status": "operational",
        "description": "Automated security scanning for GitHub Pull Requests",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook/github",
            "analytics": "/api/analytics/dashboard",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    
    db_health = check_database_health()
    
    health_status = {
        "status": "healthy",
        "github_client": github_client is not None,
        "secrets_loaded": bool(config.github_token),
        "allowed_repos": len(config.allowed_repos),
        "database": db_health,
        "version": "2.0.0"
    }
    
    # Check if all critical components are working
    if not all([health_status["github_client"], health_status["secrets_loaded"]]):
        health_status["status"] = "degraded"
        return JSONResponse(status_code=503, content=health_status)
    
    if db_health.get("status") != "healthy":
        health_status["status"] = "degraded"
    
    return health_status


# =============================================================================
# ANALYTICS API ENDPOINTS
# =============================================================================

@app.get("/api/analytics/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get dashboard summary statistics.
    Returns total scans, issues blocked, pass rate, and recent activity.
    """
    try:
        # Total counts
        total_scans = db.query(func.count(ScanResult.id)).scalar() or 0
        total_blocked = db.query(func.count(ScanResult.id)).filter(
            ScanResult.action == ScanAction.BLOCK
        ).scalar() or 0
        total_warned = db.query(func.count(ScanResult.id)).filter(
            ScanResult.action == ScanAction.WARN
        ).scalar() or 0
        total_passed = db.query(func.count(ScanResult.id)).filter(
            ScanResult.action == ScanAction.PASS
        ).scalar() or 0
        
        # Total issues found
        total_issues = db.query(func.count(SecurityIssue.id)).scalar() or 0
        critical_issues = db.query(func.count(SecurityIssue.id)).filter(
            SecurityIssue.severity == Severity.CRITICAL
        ).scalar() or 0
        
        # Pass rate
        pass_rate = (total_passed / total_scans * 100) if total_scans > 0 else 100.0
        
        # Last 7 days trend
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_scans = db.query(ScanResult).filter(
            ScanResult.created_at >= seven_days_ago
        ).count()
        
        # Active repositories
        active_repos = db.query(func.count(Repository.id)).filter(
            Repository.is_active == True
        ).scalar() or 0
        
        # Top engineers (security champions)
        top_engineers = db.query(Engineer).order_by(
            desc(Engineer.security_score)
        ).limit(5).all()
        
        return {
            "summary": {
                "total_scans": total_scans,
                "total_blocked": total_blocked,
                "total_warned": total_warned,
                "total_passed": total_passed,
                "pass_rate": round(pass_rate, 2),
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "active_repos": active_repos,
            },
            "recent": {
                "scans_last_7_days": recent_scans,
            },
            "top_champions": [
                {
                    "id": e.id,
                    "display_name": e.display_name or e.id,
                    "security_score": e.security_score,
                    "clean_prs": e.clean_prs,
                    "total_prs": e.total_prs,
                }
                for e in top_engineers
            ]
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/repos")
async def get_repo_analytics(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("total_scans", regex="^(total_scans|total_issues|blocked_prs|last_scan_at)$"),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    """
    Get per-repository analytics and metrics.
    """
    try:
        query = db.query(Repository)
        
        # Apply sorting
        sort_column = getattr(Repository, sort_by)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        repos = query.offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": [
                {
                    "id": r.id,
                    "name": r.name,
                    "organization": r.organization,
                    "total_scans": r.total_scans,
                    "total_issues": r.total_issues,
                    "blocked_prs": r.blocked_prs,
                    "pass_rate": r.pass_rate,
                    "last_scan_at": r.last_scan_at.isoformat() if r.last_scan_at else None,
                    "is_active": r.is_active,
                }
                for r in repos
            ]
        }
    except Exception as e:
        logger.error(f"Repo analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/engineers")
async def get_engineer_analytics(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("security_score", regex="^(security_score|total_prs|clean_prs|blocked_prs)$"),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    """
    Get engineer/developer leaderboard with security metrics.
    """
    try:
        query = db.query(Engineer)
        
        # Apply sorting
        sort_column = getattr(Engineer, sort_by)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        engineers = query.offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": [
                {
                    "id": e.id,
                    "display_name": e.display_name or e.id,
                    "avatar_url": e.avatar_url,
                    "security_score": e.security_score,
                    "total_prs": e.total_prs,
                    "clean_prs": e.clean_prs,
                    "warned_prs": e.warned_prs,
                    "blocked_prs": e.blocked_prs,
                    "total_issues_introduced": e.total_issues_introduced,
                    "issues_fixed": e.issues_fixed,
                    "last_activity_at": e.last_activity_at.isoformat() if e.last_activity_at else None,
                }
                for e in engineers
            ]
        }
    except Exception as e:
        logger.error(f"Engineer analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
async def get_time_series_metrics(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
    repo_id: Optional[str] = Query(None)
):
    """
    Get time-series metrics for charts.
    Returns daily scan counts, issues, and trends.
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(DailyMetrics).filter(
            DailyMetrics.date >= start_date
        )
        
        if repo_id:
            query = query.filter(DailyMetrics.repo_id == repo_id)
        else:
            query = query.filter(DailyMetrics.repo_id == None)  # Global metrics
        
        metrics = query.order_by(DailyMetrics.date).all()
        
        return {
            "period_days": days,
            "repo_id": repo_id,
            "data": [
                {
                    "date": m.date.strftime("%Y-%m-%d"),
                    "total_scans": m.total_scans,
                    "passed": m.passed_scans,
                    "warned": m.warned_scans,
                    "blocked": m.blocked_scans,
                    "critical_issues": m.critical_issues,
                    "high_issues": m.high_issues,
                    "medium_issues": m.medium_issues,
                    "low_issues": m.low_issues,
                    "pass_rate": m.pass_rate,
                    "block_rate": m.block_rate,
                }
                for m in metrics
            ]
        }
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/champions")
async def get_security_champions(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get top security champions - engineers with best security practices.
    """
    try:
        champions = db.query(Engineer).filter(
            Engineer.total_prs >= 5  # Minimum 5 PRs to qualify
        ).order_by(
            desc(Engineer.security_score)
        ).limit(limit).all()
        
        return {
            "champions": [
                {
                    "rank": idx + 1,
                    "id": e.id,
                    "display_name": e.display_name or e.id,
                    "avatar_url": e.avatar_url,
                    "security_score": e.security_score,
                    "total_prs": e.total_prs,
                    "clean_prs": e.clean_prs,
                    "clean_rate": round((e.clean_prs / e.total_prs * 100), 2) if e.total_prs > 0 else 100,
                    "issues_fixed": e.issues_fixed,
                    "badge": get_champion_badge(e.security_score),
                }
                for idx, e in enumerate(champions)
            ]
        }
    except Exception as e:
        logger.error(f"Champions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_champion_badge(score: float) -> str:
    """Get badge based on security score."""
    if score >= 95:
        return "platinum"
    elif score >= 85:
        return "gold"
    elif score >= 75:
        return "silver"
    elif score >= 60:
        return "bronze"
    return "none"


@app.get("/api/scans/recent")
async def get_recent_scans(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None, regex="^(PASS|WARN|BLOCK)$")
):
    """
    Get recent scan results.
    """
    try:
        query = db.query(ScanResult).order_by(desc(ScanResult.created_at))
        
        if action:
            query = query.filter(ScanResult.action == ScanAction[action])
        
        scans = query.limit(limit).all()
        
        return {
            "data": [
                {
                    "id": s.id,
                    "repo_id": s.repo_id,
                    "pr_number": s.pr_number,
                    "pr_title": s.pr_title,
                    "pr_url": s.pr_url,
                    "author_id": s.author_id,
                    "action": s.action.value,
                    "severity": s.severity.value,
                    "issues_count": s.issues_count,
                    "files_scanned": s.files_scanned,
                    "created_at": s.created_at.isoformat(),
                }
                for s in scans
            ]
        }
    except Exception as e:
        logger.error(f"Recent scans error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/issues/patterns")
async def get_issue_patterns(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """
    Get distribution of security issue patterns.
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pattern_counts = db.query(
            SecurityIssue.pattern_name,
            func.count(SecurityIssue.id).label('count')
        ).join(ScanResult).filter(
            ScanResult.created_at >= start_date
        ).group_by(
            SecurityIssue.pattern_name
        ).order_by(
            desc('count')
        ).limit(10).all()
        
        return {
            "period_days": days,
            "patterns": [
                {"pattern": p[0], "count": p[1]}
                for p in pattern_counts
            ]
        }
    except Exception as e:
        logger.error(f"Issue patterns error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# WEBHOOK HANDLERS
# =============================================================================

def verify_github_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC SHA256
    """
    if not signature:
        logger.warning("⚠️ No signature provided in webhook request")
        return False
    
    if not signature.startswith('sha256='):
        logger.warning("⚠️ Invalid signature format (must start with 'sha256=')")
        return False
    
    secret = config.webhook_secret
    if not secret:
        logger.error("❌ Webhook secret not configured!")
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    provided_signature = signature.split('=')[1]
    is_valid = hmac.compare_digest(expected_signature, provided_signature)
    
    if not is_valid:
        logger.warning("⚠️ Webhook signature verification FAILED!")
    
    return is_valid


def is_repo_allowed(repo_name: str) -> bool:
    """Check if repository is in the allowed list"""
    allowed_repos = config.allowed_repos
    
    if not allowed_repos:
        logger.warning("⚠️ No allowed repos configured - blocking all")
        return False
    
    for pattern in allowed_repos:
        if pattern.endswith('/*'):
            org = pattern[:-2]
            if repo_name.startswith(f"{org}/"):
                logger.info(f"✅ Repo {repo_name} matches wildcard pattern: {pattern}")
                return True
        elif pattern == repo_name:
            logger.info(f"✅ Repo {repo_name} is explicitly allowed")
            return True
    
    logger.warning(f"⚠️ Repo {repo_name} not in allowed list")
    return False


def save_scan_result(
    db: Session,
    repo_name: str,
    pr_number: int,
    pr_title: str,
    pr_url: str,
    commit_sha: str,
    branch: str,
    author: str,
    scan_result: dict,
    files_scanned: int
) -> ScanResult:
    """
    Save scan result to database and update related records.
    """
    scan_id = str(uuid.uuid4())
    
    # Ensure repository exists
    org, name = repo_name.split('/', 1)
    repo = db.query(Repository).filter(Repository.id == repo_name).first()
    if not repo:
        repo = Repository(
            id=repo_name,
            name=name,
            organization=org,
        )
        db.add(repo)
    
    # Ensure engineer exists
    engineer = db.query(Engineer).filter(Engineer.id == author).first()
    if not engineer:
        engineer = Engineer(id=author)
        db.add(engineer)
    
    # Create scan result
    action_str = scan_result.get('action', 'PASS')
    severity_str = scan_result.get('severity', 'low')
    
    scan = ScanResult(
        id=scan_id,
        repo_id=repo_name,
        pr_number=pr_number,
        pr_title=pr_title,
        pr_url=pr_url,
        commit_sha=commit_sha,
        branch=branch,
        author_id=author,
        action=ScanAction[action_str],
        severity=Severity[severity_str.upper()],
        issues_count=len(scan_result.get('issues', [])),
        files_scanned=files_scanned,
        summary_en=scan_result.get('summary_en'),
        summary_jp=scan_result.get('summary_jp'),
        fix_suggestion=scan_result.get('fix'),
        scan_metadata=scan_result,
    )
    db.add(scan)
    
    # Save individual issues
    for issue_data in scan_result.get('issues', []):
        issue = SecurityIssue(
            id=str(uuid.uuid4()),
            scan_id=scan_id,
            file_path=issue_data.get('file', 'unknown'),
            line_number=issue_data.get('line'),
            pattern_name=issue_data.get('pattern', 'unknown'),
            pattern_type=issue_data.get('type', 'regex'),
            severity=Severity[issue_data.get('severity', 'medium').upper()],
        )
        db.add(issue)
    
    # Update repository stats
    repo.total_scans += 1
    repo.total_issues += len(scan_result.get('issues', []))
    if action_str == 'BLOCK':
        repo.blocked_prs += 1
    repo.last_scan_at = datetime.utcnow()
    
    # Update engineer stats
    engineer.total_prs += 1
    if action_str == 'PASS':
        engineer.clean_prs += 1
    elif action_str == 'WARN':
        engineer.warned_prs += 1
    elif action_str == 'BLOCK':
        engineer.blocked_prs += 1
    engineer.total_issues_introduced += len(scan_result.get('issues', []))
    engineer.update_security_score()
    
    db.commit()
    return scan


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    GitHub webhook endpoint - receives PR events
    """
    logger.info(f"📨 Received webhook - Event: {x_github_event}, Delivery: {x_github_delivery}")
    
    try:
        payload_bytes = await request.body()
        
        if not verify_github_signature(payload_bytes, x_hub_signature_256):
            logger.error("❌ Invalid webhook signature - rejecting request")
            raise HTTPException(
                status_code=401, 
                detail="Invalid signature - webhook authentication failed"
            )
        
        logger.info("✅ Webhook signature verified")
        
        try:
            payload = json.loads(payload_bytes.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        if x_github_event != "pull_request":
            logger.info(f"⏭️ Ignoring {x_github_event} event (only processing pull_request)")
            return {
                "status": "ignored",
                "reason": f"Event type '{x_github_event}' is not processed",
                "processed_events": ["pull_request"]
            }
        
        action = payload.get('action')
        repo_name = payload['repository']['full_name']
        pr_number = payload['number']
        pr_data = payload['pull_request']
        pr_author = pr_data['user']['login']
        pr_title = pr_data['title']
        pr_sha = pr_data['head']['sha']
        pr_url = pr_data['html_url']
        branch = pr_data['head']['ref']
        
        logger.info(f"📋 PR Details: {repo_name} PR #{pr_number} by @{pr_author}")
        
        if not is_repo_allowed(repo_name):
            logger.warning(f"❌ Repository {repo_name} not authorized")
            raise HTTPException(
                status_code=403,
                detail=f"Repository '{repo_name}' is not in the allowed list"
            )
        
        if action not in ['opened', 'synchronize', 'reopened']:
            logger.info(f"⏭️ Ignoring action '{action}'")
            return {
                "status": "ignored",
                "reason": f"Action '{action}' does not trigger scanning",
            }
        
        logger.info("⏳ Setting pending status...")
        github_client.set_commit_status(
            repo_name,
            pr_sha,
            'pending',
            '🔍 Security scan in progress...'
        )
        
        logger.info(f"📁 Fetching files from PR #{pr_number}...")
        try:
            pr_files = github_client.get_pr_files(repo_name, pr_number)
        except Exception as e:
            logger.error(f"❌ Failed to fetch PR files: {e}")
            github_client.set_commit_status(
                repo_name, pr_sha, 'error', '⚠️ Failed to fetch PR files'
            )
            raise HTTPException(status_code=500, detail=f"Failed to fetch PR files: {str(e)}")
        
        if not pr_files:
            logger.warning(f"⚠️ No text files to scan in PR #{pr_number}")
            github_client.set_commit_status(
                repo_name, pr_sha, 'success', '✅ No files to scan'
            )
            return {
                "status": "success",
                "message": "No text files to scan",
                "pr": pr_number,
                "repo": repo_name
            }
        
        logger.info(f"✅ Found {len(pr_files)} files to scan")
        
        logger.info("🔍 Running security scan...")
        metadata = {
            "repo": repo_name,
            "branch": branch,
            "author": pr_author,
            "pr_url": pr_url
        }
        
        try:
            scan_result = run_security_scan(pr_files, metadata)
        except Exception as e:
            logger.error(f"❌ Scanner failed: {e}")
            github_client.set_commit_status(
                repo_name, pr_sha, 'error', '⚠️ Scanner error'
            )
            raise HTTPException(status_code=500, detail=f"Scanner error: {str(e)}")
        
        action_taken = scan_result.get('action', 'PASS')
        severity = scan_result.get('severity', 'low')
        issues_count = len(scan_result.get('issues', []))
        
        logger.info(f"📊 Scan Results: {action_taken} | Severity: {severity} | Issues: {issues_count}")
        
        # Save to database
        try:
            save_scan_result(
                db=db,
                repo_name=repo_name,
                pr_number=pr_number,
                pr_title=pr_title,
                pr_url=pr_url,
                commit_sha=pr_sha,
                branch=branch,
                author=pr_author,
                scan_result=scan_result,
                files_scanned=len(pr_files)
            )
            logger.info("✅ Scan result saved to database")
        except Exception as e:
            logger.error(f"⚠️ Failed to save scan result: {e}")
        
        if action_taken == 'BLOCK':
            github_client.set_commit_status(
                repo_name, pr_sha, 'failure',
                f'🚫 Security issues found ({issues_count} critical)'
            )
            status_code = 'failure'
        elif action_taken == 'WARN':
            github_client.set_commit_status(
                repo_name, pr_sha, 'success',
                f'⚠️ Warnings found ({issues_count} issues)'
            )
            status_code = 'success'
        else:
            github_client.set_commit_status(
                repo_name, pr_sha, 'success', '✅ Security scan passed'
            )
            status_code = 'success'
        
        if action_taken in ['BLOCK', 'WARN'] and issues_count > 0:
            logger.info("📢 Sending Slack notification...")
            try:
                report_security_issue(scan_result, pr_url)
            except Exception as e:
                logger.error(f"⚠️ Failed to send Slack notification: {e}")
        
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
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error processing webhook: {e}", exc_info=True)
        
        try:
            if 'repo_name' in locals() and 'pr_sha' in locals():
                github_client.set_commit_status(
                    repo_name, pr_sha, 'error', '⚠️ Internal error during scan'
                )
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# For local testing
if __name__ == "__main__":
    import uvicorn
   
    print("\n" + "="*70)
    print("🚀 Starting ATF Sentinel locally...")
    print("="*70)
    print(f"\n📍 Server will run at: http://localhost:8000")
    print(f"📖 API docs at: http://localhost:8000/docs")
    print(f"💚 Health check: http://localhost:8000/health")
    print(f"📊 Dashboard API: http://localhost:8000/api/analytics/dashboard")
    print("\n" + "="*70 + "\n")
   
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
