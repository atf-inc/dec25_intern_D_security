"""
SQLAlchemy Models for ATF Sentinel
Defines database schema for security scan results and analytics
Author: ANIRUDH S J
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, DateTime, Text, ForeignKey, 
    Boolean, Float, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum
from app.database import Base


class ScanAction(enum.Enum):
    """Possible scan result actions"""
    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"


class Severity(enum.Enum):
    """Issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Repository(Base):
    """
    Tracked repositories
    """
    __tablename__ = "repositories"
    
    id = Column(String(50), primary_key=True)  # e.g., "org/repo-name"
    name = Column(String(255), nullable=False)
    organization = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    total_scans = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    blocked_prs = Column(Integer, default=0)
    last_scan_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scan_results = relationship("ScanResult", back_populates="repository")
    
    # Indexes
    __table_args__ = (
        Index("idx_repo_org", "organization"),
        Index("idx_repo_active", "is_active"),
    )
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage"""
        if self.total_scans == 0:
            return 100.0
        return round(((self.total_scans - self.blocked_prs) / self.total_scans) * 100, 2)


class Engineer(Base):
    """
    Developer/Engineer metrics for security champions
    """
    __tablename__ = "engineers"
    
    id = Column(String(100), primary_key=True)  # GitHub username
    display_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Metrics
    total_prs = Column(Integer, default=0)
    clean_prs = Column(Integer, default=0)  # PRs with no issues
    warned_prs = Column(Integer, default=0)
    blocked_prs = Column(Integer, default=0)
    total_issues_introduced = Column(Integer, default=0)
    issues_fixed = Column(Integer, default=0)
    
    # Security score (calculated)
    security_score = Column(Float, default=100.0)
    
    # Timestamps
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scan_results = relationship("ScanResult", back_populates="engineer")
    
    # Indexes
    __table_args__ = (
        Index("idx_engineer_score", "security_score"),
    )
    
    def update_security_score(self):
        """
        Calculate security score based on PR history.
        Higher score = better security practices.
        """
        if self.total_prs == 0:
            self.security_score = 100.0
            return
        
        # Base score starts at 100
        score = 100.0
        
        # Deduct for blocked PRs (major penalty)
        score -= (self.blocked_prs / self.total_prs) * 40
        
        # Deduct for warned PRs (minor penalty)
        score -= (self.warned_prs / self.total_prs) * 15
        
        # Bonus for fixing issues
        if self.total_issues_introduced > 0:
            fix_rate = self.issues_fixed / self.total_issues_introduced
            score += fix_rate * 10
        
        # Clean PR bonus
        clean_rate = self.clean_prs / self.total_prs
        score += clean_rate * 5
        
        self.security_score = max(0.0, min(100.0, round(score, 2)))


class ScanResult(Base):
    """
    Individual PR scan results
    """
    __tablename__ = "scan_results"
    
    id = Column(String(50), primary_key=True)  # UUID
    
    # PR Information
    repo_id = Column(String(50), ForeignKey("repositories.id"), nullable=False)
    pr_number = Column(Integer, nullable=False)
    pr_title = Column(String(500), nullable=True)
    pr_url = Column(String(500), nullable=True)
    commit_sha = Column(String(40), nullable=False)
    branch = Column(String(255), nullable=True)
    
    # Author
    author_id = Column(String(100), ForeignKey("engineers.id"), nullable=False)
    
    # Scan Results
    action = Column(SQLEnum(ScanAction), default=ScanAction.PASS)
    severity = Column(SQLEnum(Severity), default=Severity.LOW)
    issues_count = Column(Integer, default=0)
    files_scanned = Column(Integer, default=0)
    
    # AI Analysis
    summary_en = Column(Text, nullable=True)
    summary_jp = Column(Text, nullable=True)
    fix_suggestion = Column(Text, nullable=True)
    
    # Raw data
    scan_metadata = Column(JSONB, nullable=True)  # Store full scan result
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    scan_duration_ms = Column(Integer, nullable=True)
    
    # Relationships
    repository = relationship("Repository", back_populates="scan_results")
    engineer = relationship("Engineer", back_populates="scan_results")
    issues = relationship("SecurityIssue", back_populates="scan_result", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_scan_repo", "repo_id"),
        Index("idx_scan_author", "author_id"),
        Index("idx_scan_action", "action"),
        Index("idx_scan_created", "created_at"),
        Index("idx_scan_repo_pr", "repo_id", "pr_number"),
    )


class SecurityIssue(Base):
    """
    Individual security issues found in scans
    """
    __tablename__ = "security_issues"
    
    id = Column(String(50), primary_key=True)  # UUID
    scan_id = Column(String(50), ForeignKey("scan_results.id"), nullable=False)
    
    # Issue details
    file_path = Column(String(500), nullable=False)
    line_number = Column(Integer, nullable=True)
    pattern_name = Column(String(100), nullable=False)  # e.g., "AWS_KEY", "PRIVATE_KEY"
    pattern_type = Column(String(50), nullable=True)  # regex, ai_detected
    
    # Content (sanitized)
    matched_content = Column(Text, nullable=True)  # Masked/sanitized
    context = Column(Text, nullable=True)  # Surrounding code context
    
    # Classification
    severity = Column(SQLEnum(Severity), default=Severity.MEDIUM)
    is_false_positive = Column(Boolean, default=False)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scan_result = relationship("ScanResult", back_populates="issues")
    
    # Indexes
    __table_args__ = (
        Index("idx_issue_scan", "scan_id"),
        Index("idx_issue_pattern", "pattern_name"),
        Index("idx_issue_severity", "severity"),
        Index("idx_issue_resolved", "is_resolved"),
    )


class DailyMetrics(Base):
    """
    Aggregated daily metrics for analytics
    """
    __tablename__ = "daily_metrics"
    
    id = Column(String(50), primary_key=True)  # date-repo or date-all
    date = Column(DateTime, nullable=False)
    repo_id = Column(String(50), ForeignKey("repositories.id"), nullable=True)  # NULL = global
    
    # Counts
    total_scans = Column(Integer, default=0)
    passed_scans = Column(Integer, default=0)
    warned_scans = Column(Integer, default=0)
    blocked_scans = Column(Integer, default=0)
    
    # Issues by severity
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    
    # Top patterns (JSON array)
    top_patterns = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_metrics_date", "date"),
        Index("idx_metrics_repo", "repo_id"),
        Index("idx_metrics_date_repo", "date", "repo_id"),
    )
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage"""
        if self.total_scans == 0:
            return 100.0
        return round((self.passed_scans / self.total_scans) * 100, 2)
    
    @property
    def block_rate(self) -> float:
        """Calculate block rate percentage"""
        if self.total_scans == 0:
            return 0.0
        return round((self.blocked_scans / self.total_scans) * 100, 2)

