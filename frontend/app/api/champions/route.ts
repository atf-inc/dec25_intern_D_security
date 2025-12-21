import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.BACKEND_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const limit = searchParams.get("limit") || "10";

    const response = await fetch(`${API_URL}/api/champions?limit=${limit}`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Champions API error:", error);
    
    // Return mock data
    return NextResponse.json({
      champions: [
        { rank: 1, id: "alice-chen", display_name: "Alice Chen", avatar_url: null, security_score: 98.5, total_prs: 47, clean_prs: 45, clean_rate: 95.7, issues_fixed: 12, badge: "platinum" },
        { rank: 2, id: "bob-smith", display_name: "Bob Smith", avatar_url: null, security_score: 95.2, total_prs: 41, clean_prs: 38, clean_rate: 92.7, issues_fixed: 8, badge: "platinum" },
        { rank: 3, id: "carol-davis", display_name: "Carol Davis", avatar_url: null, security_score: 92.8, total_prs: 35, clean_prs: 31, clean_rate: 88.6, issues_fixed: 6, badge: "gold" },
        { rank: 4, id: "david-lee", display_name: "David Lee", avatar_url: null, security_score: 89.4, total_prs: 33, clean_prs: 28, clean_rate: 84.8, issues_fixed: 4, badge: "gold" },
        { rank: 5, id: "eve-wilson", display_name: "Eve Wilson", avatar_url: null, security_score: 87.1, total_prs: 30, clean_prs: 25, clean_rate: 83.3, issues_fixed: 5, badge: "gold" },
        { rank: 6, id: "frank-moore", display_name: "Frank Moore", avatar_url: null, security_score: 82.5, total_prs: 28, clean_prs: 22, clean_rate: 78.6, issues_fixed: 3, badge: "silver" },
        { rank: 7, id: "grace-taylor", display_name: "Grace Taylor", avatar_url: null, security_score: 78.9, total_prs: 25, clean_prs: 19, clean_rate: 76.0, issues_fixed: 2, badge: "silver" },
        { rank: 8, id: "henry-anderson", display_name: "Henry Anderson", avatar_url: null, security_score: 75.3, total_prs: 22, clean_prs: 16, clean_rate: 72.7, issues_fixed: 1, badge: "silver" },
      ],
    });
  }
}

