import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.BACKEND_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const limit = searchParams.get("limit") || "20";
    const offset = searchParams.get("offset") || "0";

    const response = await fetch(
      `${API_URL}/api/analytics/repos?limit=${limit}&offset=${offset}`,
      {
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
      }
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Repos API error:", error);
    
    // Return mock data
    return NextResponse.json({
      total: 5,
      offset: 0,
      limit: 20,
      data: [
        { id: "atf-inc/main-app", name: "main-app", organization: "atf-inc", total_scans: 234, total_issues: 12, blocked_prs: 3, pass_rate: 92.5, last_scan_at: new Date().toISOString(), is_active: true },
        { id: "atf-inc/api-service", name: "api-service", organization: "atf-inc", total_scans: 189, total_issues: 8, blocked_prs: 2, pass_rate: 95.1, last_scan_at: new Date().toISOString(), is_active: true },
        { id: "atf-inc/frontend", name: "frontend", organization: "atf-inc", total_scans: 156, total_issues: 5, blocked_prs: 1, pass_rate: 97.2, last_scan_at: new Date().toISOString(), is_active: true },
        { id: "atf-inc/data-pipeline", name: "data-pipeline", organization: "atf-inc", total_scans: 98, total_issues: 15, blocked_prs: 5, pass_rate: 84.3, last_scan_at: new Date().toISOString(), is_active: true },
        { id: "atf-inc/mobile-app", name: "mobile-app", organization: "atf-inc", total_scans: 67, total_issues: 3, blocked_prs: 0, pass_rate: 98.5, last_scan_at: new Date().toISOString(), is_active: true },
      ],
    });
  }
}

