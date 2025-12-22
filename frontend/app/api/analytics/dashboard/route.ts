import { NextResponse } from "next/server";

// Use BACKEND_API_URL for server-side calls (Docker internal network)
// Fallback to NEXT_PUBLIC_API_URL or localhost for local dev
const API_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
    return NextResponse.json(
      { error: "Failed to fetch dashboard data", detail: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

