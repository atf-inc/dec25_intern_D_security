import { GoogleGenerativeAI } from "@google/generative-ai";

// Initialize Gemini AI client
const apiKey = process.env.GEMINI_API_KEY || "";
if (!apiKey) {
  console.warn("⚠️ GEMINI_API_KEY not set - AI features will not work");
}

const genAI = new GoogleGenerativeAI(apiKey);

/**
 * Helper function to get a working model by trying multiple model names
 * Using latest models first (as of 2025)
 */
async function tryGenerateContent(prompt: string): Promise<string> {
  const modelsToTry = [
    "gemini-3-pro",              // Latest Gemini 3 Pro (Nov 2025)
    "gemini-3-flash",            // Latest Gemini 3 Flash (Dec 2025)
    "gemini-2.5-pro",            // Gemini 2.5 Pro with enhanced capabilities
    "gemini-2.5-flash",           // Gemini 2.5 Flash
    "gemini-1.5-pro-latest",     // Latest stable 1.5 pro model
    "gemini-1.5-flash-latest",   // Latest stable 1.5 flash model
    "gemini-1.5-pro",            // Stable 1.5 pro model
    "gemini-1.5-flash",          // Stable 1.5 flash model
  ];

  let lastError: any = null;

  for (const modelName of modelsToTry) {
    try {
      const currentModel = genAI.getGenerativeModel({ model: modelName });
      const result = await currentModel.generateContent(prompt);
      return result.response.text();
    } catch (error: any) {
      lastError = error;
      continue;
    }
  }

  throw lastError || new Error("Failed to generate content with any available model");
}

/**
 * Chat message type
 */
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

/**
 * Security chat context for AI
 */
const SECURITY_CONTEXT = `You are ATF Sentinel's AI security assistant. You help developers understand:
- Security vulnerabilities and how to fix them
- Best practices for secure coding
- Common security patterns and anti-patterns
- How to interpret scan results

Be concise, helpful, and provide actionable advice. When discussing code, provide examples.
Focus on practical security guidance rather than theoretical concepts.`;

/**
 * Chat with Gemini AI about security topics
 */
export async function chatWithGemini(
  messages: ChatMessage[],
  userMessage: string
): Promise<string> {
  // Check if API key is set
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is not configured. Please set it in your environment variables.");
  }

  // Try different models if one fails - using latest models first (as of 2025)
  const modelsToTry = [
    "gemini-3-pro",              // Latest Gemini 3 Pro (Nov 2025)
    "gemini-3-flash",            // Latest Gemini 3 Flash (Dec 2025)
    "gemini-2.5-pro",            // Gemini 2.5 Pro with enhanced capabilities
    "gemini-2.5-flash",          // Gemini 2.5 Flash
    "gemini-1.5-pro-latest",     // Latest stable 1.5 pro model
    "gemini-1.5-flash-latest",   // Latest stable 1.5 flash model
    "gemini-1.5-pro",            // Stable 1.5 pro model
    "gemini-1.5-flash",          // Stable 1.5 flash model
  ];

  let lastError: any = null;

  for (const modelName of modelsToTry) {
    try {
      const currentModel = genAI.getGenerativeModel({ model: modelName });
      
      // Build conversation history
      const history = messages.map((msg) => ({
        role: msg.role === "user" ? "user" : "model",
        parts: [{ text: msg.content }],
      }));

      // Start chat with history
      const chat = currentModel.startChat({
        history: [
          {
            role: "user",
            parts: [{ text: SECURITY_CONTEXT }],
          },
          {
            role: "model",
            parts: [
              {
                text: "I understand. I'm ATF Sentinel's AI security assistant, ready to help with security questions, vulnerability analysis, and secure coding practices.",
              },
            ],
          },
          ...history,
        ],
        generationConfig: {
          maxOutputTokens: 2048,
          temperature: 0.7,
        },
      });

      // Send message and get response
      const result = await chat.sendMessage(userMessage);
      const response = result.response;
      
      return response.text();
    } catch (error: any) {
      lastError = error;
      console.log(`Model ${modelName} failed, trying next...`);
      // Continue to next model
      continue;
    }
  }

  // If all models failed, throw error with details
  console.error("Gemini chat error - all models failed:", lastError);
  
  if (lastError?.message?.includes("API key") || lastError?.message?.includes("401")) {
    throw new Error("Invalid or missing Gemini API key. Please check your GEMINI_API_KEY environment variable.");
  }
  if (lastError?.message?.includes("quota") || lastError?.message?.includes("429")) {
    throw new Error("API quota exceeded. Please try again later.");
  }
  if (lastError?.message?.includes("not found") || lastError?.message?.includes("404")) {
    throw new Error("No compatible Gemini model found. Please verify your API key has access to Gemini models.");
  }
  
  throw new Error(`Failed to get AI response: ${lastError?.message || "Unknown error"}`);
}

/**
 * Generate security test cases for code
 */
export async function generateSecurityTests(
  code: string,
  language: string
): Promise<string> {
  const prompt = `Generate security test cases for the following ${language} code. 
Focus on:
1. Input validation tests
2. Authentication/authorization tests (if applicable)
3. SQL injection tests (if database operations present)
4. XSS prevention tests (if web-related)
5. Secret/credential exposure tests

Code:
\`\`\`${language}
${code}
\`\`\`

Provide test cases in a format appropriate for the language (e.g., pytest for Python, Jest for JavaScript).
Include both positive and negative test cases.`;

  try {
    return await tryGenerateContent(prompt);
  } catch (error: any) {
    console.error("Test generation error:", error);
    throw new Error(`Failed to generate security tests: ${error?.message || "Unknown error"}`);
  }
}

/**
 * Analyze code for security vulnerabilities
 */
export async function analyzeCodeSecurity(
  code: string,
  language: string
): Promise<{
  summary: string;
  vulnerabilities: Array<{
    type: string;
    severity: string;
    description: string;
    fix: string;
  }>;
  recommendations: string[];
}> {
  const prompt = `Analyze the following ${language} code for security vulnerabilities.

Code:
\`\`\`${language}
${code}
\`\`\`

Respond in JSON format with:
{
  "summary": "Brief security assessment",
  "vulnerabilities": [
    {
      "type": "vulnerability type",
      "severity": "critical|high|medium|low",
      "description": "what the issue is",
      "fix": "how to fix it"
    }
  ],
  "recommendations": ["list of security recommendations"]
}`;

  try {
    const text = await tryGenerateContent(prompt);
    
    // Extract JSON from response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error("Invalid response format");
    }
    
    return JSON.parse(jsonMatch[0]);
  } catch (error: any) {
    console.error("Code analysis error:", error);
    throw new Error(`Failed to analyze code: ${error?.message || "Unknown error"}`);
  }
}

/**
 * Explain a security pattern or vulnerability
 */
export async function explainSecurityConcept(concept: string): Promise<string> {
  const prompt = `Explain the following security concept in simple terms, with examples and mitigation strategies: "${concept}"

Structure your response as:
1. What it is
2. Why it's dangerous
3. Real-world example
4. How to prevent/fix it
5. Code example (if applicable)`;

  try {
    return await tryGenerateContent(prompt);
  } catch (error: any) {
    console.error("Explanation error:", error);
    throw new Error(`Failed to explain concept: ${error?.message || "Unknown error"}`);
  }
}

