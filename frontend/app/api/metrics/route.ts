import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.BACKEND_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const days = searchParams.get("days") || "30";

    const response = await fetch(`${API_URL}/api/metrics?days=${days}`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Metrics API error:", error);
    
    // Generate mock time series data
    const days = parseInt(request.nextUrl.searchParams.get("days") || "30");
    const data = [];
    const now = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      
      const totalScans = Math.floor(Math.random() * 30) + 10;
      const blocked = Math.floor(Math.random() * 3);
      const warned = Math.floor(Math.random() * 5);
      const passed = totalScans - blocked - warned;
      
      data.push({
        date: date.toISOString().split("T")[0],
        total_scans: totalScans,
        passed,
        warned,
        blocked,
        critical_issues: blocked,
        high_issues: Math.floor(Math.random() * 3),
        medium_issues: Math.floor(Math.random() * 5),
        low_issues: Math.floor(Math.random() * 8),
        pass_rate: (passed / totalScans) * 100,
        block_rate: (blocked / totalScans) * 100,
      });
    }
    
    return NextResponse.json({
      period_days: days,
      repo_id: null,
      data,
    });
  }
}

