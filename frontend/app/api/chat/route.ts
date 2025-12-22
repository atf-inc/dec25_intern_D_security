import { NextRequest, NextResponse } from "next/server";
import { chatWithGemini } from "@/lib/gemini";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, history } = body;

    if (!message || typeof message !== "string") {
      return NextResponse.json(
        { error: "Message is required" },
        { status: 400 }
      );
    }

    // Convert history to the format expected by chatWithGemini
    const chatHistory = (history || []).map((msg: { role: string; content: string }) => ({
      role: msg.role as "user" | "assistant",
      content: msg.content,
    }));

    const response = await chatWithGemini(chatHistory, message);

    return NextResponse.json({ response });
  } catch (error: any) {
    console.error("Chat API error:", error);
    
    // Return more specific error messages
    const errorMessage = error?.message || "Failed to process chat request";
    
    return NextResponse.json(
      { 
        error: errorMessage,
        details: error?.message 
      },
      { status: 500 }
    );
  }
}

