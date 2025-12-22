"""
ATF Sentinel - GitHub Webhook Server
Main FastAPI application that receives and processes GitHub PR events
Author: ANIRUDH S J
"""
from fastapi import FastAPI, Request, Header, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import sqlalchemy
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
    
    # Initialize allowed repositories in database
    db = None
    try:
        db = next(get_db())
        for repo_pattern in config.allowed_repos:
            # Handle wildcard patterns (e.g., "org/*")
            if repo_pattern.endswith('/*'):
                org = repo_pattern[:-2]
                # Check if any repo from this org exists
                existing = db.query(Repository).filter(Repository.organization == org).first()
                if not existing:
                    logger.info(f"📝 Note: Repository pattern '{repo_pattern}' will be created on first scan")
            else:
                # Exact repo name - create entry if it doesn't exist
                repo = db.query(Repository).filter(Repository.id == repo_pattern).first()
                if not repo:
                    try:
                        org, name = repo_pattern.split('/', 1)
                        new_repo = Repository(
                            id=repo_pattern,
                            name=name,
                            organization=org,
                            is_active=True,
                            total_scans=0,
                            total_issues=0,
                            blocked_prs=0,
                        )
                        db.add(new_repo)
                        logger.info(f"✅ Created repository entry: {repo_pattern}")
                    except ValueError:
                        logger.warning(f"⚠️ Invalid repo format '{repo_pattern}', skipping")
        db.commit()
        db.close()
    except Exception as e:
        logger.warning(f"⚠️ Could not initialize repositories: {e}")
        if db is not None:
            try:
                db.rollback()
                db.close()
            except:
                pass
    
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
            "webhook_diagnostics": "/api/webhook/diagnostics",
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
            desc(Engineer.security_score)  # type: ignore
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
        
        # Apply sorting - handle pass_rate specially as it's a property
        if sort_by == "pass_rate":
            # Sort by pass_rate calculated value (total_scans - blocked_prs) / total_scans
            # Calculate in Python after fetching since it's a property
            pass
        else:
            sort_column = getattr(Repository, sort_by)
            if order == "desc":
                query = query.order_by(desc(sort_column))  # type: ignore
            else:
                query = query.order_by(sort_column)  # type: ignore
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        repos = query.offset(offset).limit(limit).all()
        
        # Sort by pass_rate in Python if needed
        if sort_by == "pass_rate":
            repos = sorted(repos, key=lambda r: r.pass_rate, reverse=(order == "desc"))
        
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
                    "last_scan_at": r.last_scan_at.isoformat() if r.last_scan_at is not None else None,
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
                    "last_activity_at": e.last_activity_at.isoformat() if e.last_activity_at is not None else None,
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
            desc(Engineer.security_score)  # type: ignore
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
                    "clean_rate": round((int(e.clean_prs) / int(e.total_prs) * 100), 2) if (e.total_prs is not None and int(e.total_prs) > 0) else 100.0,  # type: ignore
                    "issues_fixed": e.issues_fixed,
                    "badge": get_champion_badge(float(e.security_score) if isinstance(e.security_score, (int, float)) else 0.0),
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

def verify_github_signature(payload: bytes, signature: Optional[str]) -> bool:
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
    
    # Update repository stats - SQLAlchemy handles these assignments correctly
    current_scans = repo.total_scans or 0
    current_issues = repo.total_issues or 0
    current_blocked = repo.blocked_prs or 0
    
    repo.total_scans = current_scans + 1  # type: ignore
    repo.total_issues = current_issues + len(scan_result.get('issues', []))  # type: ignore
    if action_str == 'BLOCK':
        repo.blocked_prs = current_blocked + 1  # type: ignore
    repo.last_scan_at = datetime.utcnow()  # type: ignore
    
    # Update engineer stats
    current_total_prs = engineer.total_prs or 0
    current_clean = engineer.clean_prs or 0
    current_warned = engineer.warned_prs or 0
    current_blocked_prs = engineer.blocked_prs or 0
    current_issues_intro = engineer.total_issues_introduced or 0
    
    engineer.total_prs = current_total_prs + 1  # type: ignore
    if action_str == 'PASS':
        engineer.clean_prs = current_clean + 1  # type: ignore
    elif action_str == 'WARN':
        engineer.warned_prs = current_warned + 1  # type: ignore
    elif action_str == 'BLOCK':
        engineer.blocked_prs = current_blocked_prs + 1  # type: ignore
    engineer.total_issues_introduced = current_issues_intro + len(scan_result.get('issues', []))  # type: ignore
    engineer.update_security_score()
    
    try:
        db.commit()
        logger.debug(f"✅ Committed scan result for PR #{pr_number} in {repo_name}")
    except Exception as e:
        logger.error(f"❌ Failed to commit scan result: {e}", exc_info=True)
        db.rollback()
        raise
    
    return scan


async def process_pr_scan_background(
    repo_name: str,
    pr_number: int,
    pr_title: str,
    pr_url: str,
    pr_sha: str,
    branch: str,
    pr_author: str
):
    """
    Background task to process PR scan without blocking webhook response.
    This prevents GitHub webhook timeout (10 seconds limit).
    """
    try:
        # Check if GitHub client is available
        if not github_client:
            logger.error("❌ [Background] GitHub client not initialized")
            return
        
        # Type assertion for linter - github_client is guaranteed to be non-None after check above
        assert github_client is not None, "GitHub client must be initialized"
        client = github_client
        
        # Get a new database session for background task
        from app.database import get_session_local
        SessionLocal = get_session_local()
        db = SessionLocal()
        
        try:
            logger.info(f"📁 [Background] Fetching files from PR #{pr_number}...")
            pr_files = client.get_pr_files(repo_name, pr_number)
            
            if not pr_files:
                logger.warning(f"⚠️ [Background] No text files to scan in PR #{pr_number}")
                if pr_sha and len(pr_sha) >= 7:
                    client.set_commit_status(
                        repo_name, pr_sha, 'success', '✅ No files to scan'
                    )
                return
            
            logger.info(f"✅ [Background] Found {len(pr_files)} files to scan")
            logger.info(f"📧 [Background] Fetching author email for PR #{pr_number}...")
            author_email = client.get_pr_author_email(repo_name, pr_number)
            
            logger.info("🔍 [Background] Running security scan...")
            metadata = {
                "repo": repo_name,
                "branch": branch,
                "author": pr_author,
                "author_email": author_email,
                "pr_url": pr_url
            }
            
            scan_result = run_security_scan(pr_files, metadata)
            
            action_taken = scan_result.get('action', 'PASS')
            severity = scan_result.get('severity', 'low')
            issues_count = len(scan_result.get('issues', []))
            
            logger.info(f"📊 [Background] Scan Results: {action_taken} | Severity: {severity} | Issues: {issues_count}")
            
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
                logger.info("✅ [Background] Scan result saved to database")
            except Exception as e:
                logger.error(f"⚠️ [Background] Failed to save scan result: {e}", exc_info=True)
            
            # Set final commit status
            if pr_sha and len(pr_sha) >= 7:
                if action_taken == 'BLOCK':
                    client.set_commit_status(
                        repo_name, pr_sha, 'failure',
                        f'🚫 Security issues found ({issues_count} critical)'
                    )
                elif action_taken == 'WARN':
                    client.set_commit_status(
                        repo_name, pr_sha, 'success',
                        f'⚠️ Warnings found ({issues_count} issues)'
                    )
                else:
                    client.set_commit_status(
                        repo_name, pr_sha, 'success', '✅ Security scan passed'
                    )
            
            # Send Slack notification if needed
            if action_taken in ['BLOCK', 'WARN'] and issues_count > 0:
                logger.info("📢 [Background] Sending Slack notification...")
                try:
                    report_security_issue(scan_result, pr_url)
                except Exception as e:
                    logger.error(f"⚠️ [Background] Failed to send Slack notification: {e}")
            
            logger.info(f"✅ [Background] Successfully processed PR #{pr_number}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ [Background] Error processing PR scan: {e}", exc_info=True)
        try:
            if github_client and pr_sha and len(pr_sha) >= 7:
                client = github_client  # Use local reference
                client.set_commit_status(
                    repo_name, pr_sha, 'error', '⚠️ Error during scan'
                )
        except Exception:
            pass


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    GitHub webhook endpoint - receives PR events
    """
    logger.info(f"📨 Received webhook - Event: {x_github_event}, Delivery: {x_github_delivery}")
    
    # Initialize variables for error handling
    repo_name: Optional[str] = None
    pr_sha: Optional[str] = None
    
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
        
        # Ensure these are strings (they should be from payload)
        if not isinstance(repo_name, str) or not isinstance(pr_sha, str):
            raise HTTPException(status_code=400, detail="Invalid payload: missing required fields")
        
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
        
        if not github_client:
            raise HTTPException(status_code=503, detail="GitHub client not initialized")
        
        # Set pending status immediately
        logger.info("⏳ Setting pending status...")
        if pr_sha and len(pr_sha) >= 7:
            github_client.set_commit_status(
                repo_name,
                pr_sha,
                'pending',
                '🔍 Security scan in progress...'
            )
        
        # Queue background task for processing (returns immediately)
        logger.info(f"📋 Queuing PR #{pr_number} for background processing...")
        background_tasks.add_task(
            process_pr_scan_background,
            repo_name=repo_name,
            pr_number=pr_number,
            pr_title=pr_title,
            pr_url=pr_url,
            pr_sha=pr_sha,
            branch=branch,
            pr_author=pr_author
        )
        
        # Return immediately to avoid GitHub timeout
        return {
            "status": "accepted",
            "message": "Webhook received and queued for processing",
            "repo": repo_name,
            "pr": pr_number,
            "author": pr_author,
            "note": "Scan is processing in the background. Check commit status for results."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error processing webhook: {e}", exc_info=True)
        
        try:
            if github_client and 'repo_name' in locals() and 'pr_sha' in locals() and repo_name and pr_sha:
                github_client.set_commit_status(
                    repo_name, pr_sha, 'error', '⚠️ Internal error during scan'
                )
        except Exception:
            pass
        
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/webhook/diagnostics")
async def webhook_diagnostics():
    """
    Diagnostic endpoint to verify webhook configuration.
    Returns webhook endpoint info and configuration status.
    """
    try:
        webhook_secret_configured = bool(config.webhook_secret)
        github_client_configured = github_client is not None
        allowed_repos = config.allowed_repos
        
        # Get base URL from request (if available)
        import os
        base_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
        
        return {
            "status": "ok",
            "webhook_endpoint": f"{base_url}/webhook/github",
            "configuration": {
                "webhook_secret_configured": webhook_secret_configured,
                "webhook_secret_length": len(config.webhook_secret) if config.webhook_secret else 0,
                "github_token_configured": bool(config.github_token),
                "github_client_initialized": github_client_configured,
                "allowed_repos": allowed_repos,
                "allowed_repos_count": len(allowed_repos),
            },
            "instructions": {
                "github_setup": "Go to your repository → Settings → Webhooks → Add webhook",
                "payload_url": f"{base_url}/webhook/github",
                "content_type": "application/json",
                "events": ["pull_request"],
                "secret_required": True,
            },
            "health": {
                "backend": "operational",
                "database": check_database_health(),
            }
        }
    except Exception as e:
        logger.error(f"Webhook diagnostics error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scans/test")
async def test_scan_endpoint(db: Session = Depends(get_db)):
    """
    Test endpoint to verify scan tracking is working.
    Returns current scan statistics.
    """
    try:
        total_scans = db.query(func.count(ScanResult.id)).scalar() or 0
        total_repos = db.query(func.count(Repository.id)).scalar() or 0
        total_engineers = db.query(func.count(Engineer.id)).scalar() or 0
        
        recent_scans = db.query(ScanResult).order_by(
            desc(ScanResult.created_at)
        ).limit(10).all()
        
        return {
            "status": "ok",
            "statistics": {
                "total_scans": total_scans,
                "total_repositories": total_repos,
                "total_engineers": total_engineers,
            },
            "recent_scans": [
                {
                    "id": s.id,
                    "repo": s.repo_id,
                    "pr_number": s.pr_number,
                    "action": s.action.value,
                    "issues_count": s.issues_count,
                    "created_at": s.created_at.isoformat() if hasattr(s, 'created_at') and s.created_at is not None else None,  # type: ignore
                }
                for s in recent_scans
            ],
            "repositories": [
                {
                    "id": r.id,
                    "total_scans": r.total_scans,
                    "total_issues": r.total_issues,
                    "last_scan_at": r.last_scan_at.isoformat() if r.last_scan_at is not None else None,
                }
                for r in db.query(Repository).all()
            ]
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
