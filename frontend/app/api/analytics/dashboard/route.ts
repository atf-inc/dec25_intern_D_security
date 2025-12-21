import { NextResponse } from "next/server";

const API_URL = process.env.BACKEND_API_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/analytics/dashboard`, {
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Dashboard API error:", error);
    
    // Return mock data for development/demo
    return NextResponse.json({
      summary: {
        total_scans: 1247,
        total_blocked: 23,
        total_warned: 156,
        total_passed: 1068,
        pass_rate: 85.6,
        total_issues: 312,
        critical_issues: 23,
        active_repos: 12,
      },
      recent: {
        scans_last_7_days: 89,
      },
      top_champions: [
        { id: "developer1", display_name: "Alice Chen", security_score: 98.5, clean_prs: 45, total_prs: 47 },
        { id: "developer2", display_name: "Bob Smith", security_score: 95.2, clean_prs: 38, total_prs: 41 },
        { id: "developer3", display_name: "Carol Davis", security_score: 92.8, clean_prs: 31, total_prs: 35 },
        { id: "developer4", display_name: "David Lee", security_score: 89.4, clean_prs: 28, total_prs: 33 },
        { id: "developer5", display_name: "Eve Wilson", security_score: 87.1, clean_prs: 25, total_prs: 30 },
      ],
    });
  }
}

