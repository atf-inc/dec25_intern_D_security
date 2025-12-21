import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.BACKEND_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const days = searchParams.get("days") || "30";

    const response = await fetch(`${API_URL}/api/issues/patterns?days=${days}`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Issue patterns API error:", error);
    
    // Return mock data
    return NextResponse.json({
      period_days: 30,
      patterns: [
        { pattern: "HARDCODED_SECRET", count: 45 },
        { pattern: "AWS_KEY", count: 23 },
        { pattern: "PRIVATE_KEY", count: 18 },
        { pattern: "API_TOKEN", count: 15 },
        { pattern: "SQL_INJECTION", count: 12 },
        { pattern: "XSS_VULNERABILITY", count: 8 },
        { pattern: "WEAK_PASSWORD", count: 6 },
        { pattern: "INSECURE_RANDOM", count: 4 },
      ],
    });
  }
}

