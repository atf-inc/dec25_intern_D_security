import os
import json
import logging
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

def extract_json(text: str):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")
    return json.loads(match.group())

def analyze_code_with_gemini(diff_text):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "status": "clean",
            "summary_en": "Simulation: No API key provided.",
            "summary_jp": "シミュレーション：APIキーが設定されていません。",
            "action": "PASS",
            "fix": "N/A",
            "vulnerabilities": []
        }

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are a Senior Security Engineer.

Analyze the following code and RETURN ONLY VALID JSON.
NO markdown. NO explanation. NO text outside JSON.

Schema:
{{
  "status": "clean" | "warning" | "critical",
  "summary_en": "...",
  "summary_jp": "...",
  "action": "PASS" | "WARN" | "BLOCK",
  "fix": "...",
  "vulnerabilities": []
}}

CODE:
{diff_text}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return extract_json(response.text)

    except Exception as e:
        logger.error(f"GenAI Error: {e}")
        return {
            "status": "error",
            "summary_en": "AI Analysis Failed",
            "summary_jp": "AI分析中にエラーが発生しました。",
            "action": "WARN",
            "fix": "Check logs",
            "vulnerabilities": []
        }
