# backend/app/gemini_analyzer.py

import os
import json
import logging
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def extract_json(text: str):
    """
    Extract JSON from response, handling Markdown code blocks.
    """
    try:
        if not text:
            raise ValueError("Empty response")
        
        cleaned = text.strip()
        if "```" in cleaned:
            pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
            match = re.search(pattern, cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
            
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"JSON Parsing failed: {e}")
        raise ValueError("Could not extract valid JSON from response")

def analyze_code_with_gemini(diff_text, engineer_context=""):
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
        You are a Senior Security Engineer. Analyze the following code.
        
        {engineer_context}
        
        RETURN JSON ONLY using this schema:
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
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
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