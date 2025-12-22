# backend/app/champion.py

import os
import logging
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def extract_json(text: str):
    """
    Robust JSON extraction (Matches your gemini_analyzer logic).
    """
    try:
        if not text: return {}
        cleaned = text.strip()
        # Handle Markdown fences
        if "```" in cleaned:
            pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
            match = re.search(pattern, cleaned, re.DOTALL)
            if match: return json.loads(match.group(1))
        
        # Fallback regex
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match: return json.loads(match.group(0))
        
        return json.loads(cleaned)
    except:
        return {}

def check_security_champion(diff_text):
    """
    Analyzes code to see if it fixes a security issue.
    Returns praise data if true, None otherwise.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key: return None

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are a Security Culture Expert. Analyze this code diff.
        Does this code FIX a security issue, ADD input validation, or IMPROVE security posture?
        
        RETURN JSON ONLY:
        {{
            "is_security_fix": true, 
            "badge": "🛡️ Security Champion",
            "praise_message": "Write a short 1-sentence encouraging message about the fix."
        }}
        
        If no security improvement, return "is_security_fix": false.

        CODE: {diff_text[:5000]} 
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        return extract_json(response.text)

    except Exception as e:
        logger.error(f"Champion Logic Error: {e}")
        return None