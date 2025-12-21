/**
 * ATF Sentinel Type Definitions
 */

// ===========================================
// Enums
// ===========================================

export type ScanAction = "PASS" | "WARN" | "BLOCK";
export type Severity = "low" | "medium" | "high" | "critical";
export type ChampionBadge = "none" | "bronze" | "silver" | "gold" | "platinum";

// ===========================================
// Dashboard Types
// ===========================================

export interface DashboardSummary {
  total_scans: number;
  total_blocked: number;
  total_warned: number;
  total_passed: number;
  pass_rate: number;
  total_issues: number;
  critical_issues: number;
  active_repos: number;
}

export interface DashboardStats {
  summary: DashboardSummary;
  recent: {
    scans_last_7_days: number;
  };
  top_champions: ChampionPreview[];
}

export interface ChampionPreview {
  id: string;
  display_name: string;
  security_score: number;
  clean_prs: number;
  total_prs: number;
}

// ===========================================
// Repository Types
// ===========================================

export interface Repository {
  id: string;
  name: string;
  organization: string;
  total_scans: number;
  total_issues: number;
  blocked_prs: number;
  pass_rate: number;
  last_scan_at: string | null;
  is_active: boolean;
}

export interface RepoAnalyticsResponse {
  total: number;
  offset: number;
  limit: number;
  data: Repository[];
}

// ===========================================
// Engineer Types
// ===========================================

export interface Engineer {
  id: string;
  display_name: string;
  avatar_url: string | null;
  security_score: number;
  total_prs: number;
  clean_prs: number;
  warned_prs: number;
  blocked_prs: number;
  total_issues_introduced: number;
  issues_fixed: number;
  last_activity_at: string | null;
}

export interface EngineerAnalyticsResponse {
  total: number;
  offset: number;
  limit: number;
  data: Engineer[];
}

// ===========================================
// Champion Types
// ===========================================

export interface Champion {
  rank: number;
  id: string;
  display_name: string;
  avatar_url: string | null;
  security_score: number;
  total_prs: number;
  clean_prs: number;
  clean_rate: number;
  issues_fixed: number;
  badge: ChampionBadge;
}

export interface ChampionsResponse {
  champions: Champion[];
}

// ===========================================
// Scan Result Types
// ===========================================

export interface ScanResult {
  id: string;
  repo_id: string;
  pr_number: number;
  pr_title: string;
  pr_url: string;
  author_id: string;
  action: ScanAction;
  severity: Severity;
  issues_count: number;
  files_scanned: number;
  created_at: string;
}

export interface RecentScansResponse {
  data: ScanResult[];
}

// ===========================================
// Security Issue Types
// ===========================================

export interface SecurityIssue {
  id: string;
  scan_id: string;
  file_path: string;
  line_number: number | null;
  pattern_name: string;
  pattern_type: string;
  severity: Severity;
  is_false_positive: boolean;
  is_resolved: boolean;
}

export interface IssuePattern {
  pattern: string;
  count: number;
}

export interface IssuePatternsResponse {
  period_days: number;
  patterns: IssuePattern[];
}

// ===========================================
// Metrics Types
// ===========================================

export interface DailyMetric {
  date: string;
  total_scans: number;
  passed: number;
  warned: number;
  blocked: number;
  critical_issues: number;
  high_issues: number;
  medium_issues: number;
  low_issues: number;
  pass_rate: number;
  block_rate: number;
}

export interface MetricsResponse {
  period_days: number;
  repo_id: string | null;
  data: DailyMetric[];
}

// ===========================================
// Chat Types
// ===========================================

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  history: Array<{
    role: "user" | "assistant";
    content: string;
  }>;
}

export interface ChatResponse {
  response: string;
}

// ===========================================
// Test Generation Types
// ===========================================

export interface TestGenerationRequest {
  code: string;
  language: string;
}

export interface TestGenerationResponse {
  tests: string;
  language: string;
}

// ===========================================
// API Response Types
// ===========================================

export interface APIError {
  detail: string;
  status_code?: number;
}

export interface PaginatedResponse<T> {
  total: number;
  offset: number;
  limit: number;
  data: T[];
}

// ===========================================
// Health Check Types
// ===========================================

export interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy";
  github_client: boolean;
  secrets_loaded: boolean;
  allowed_repos: number;
  database: {
    status: string;
    database?: string;
    error?: string;
  };
  version: string;
}

