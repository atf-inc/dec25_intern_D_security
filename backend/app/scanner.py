# backend/app/scanner.py
import logging
from app.pattern_scanner import scan_diff_for_patterns
from app.gemini_analyzer import analyze_code_with_gemini
# RESTORED: Champion Logic
from app.champion import check_security_champion
from app.security_memory import get_engineer_profile, update_engineer_profile

logger = logging.getLogger(__name__)

def run_security_scan(files_list, metadata=None):
    """
    Orchestrates the scan for a LIST of files.
    """
    if metadata is None:
        metadata = {}

    # 1. Fetch Engineer Context (Security Memory)
    author = metadata.get('author', 'unknown_user')
    engineer_context = ""
    try:
        engineer_context = get_engineer_profile(author)
    except Exception as e:
        logger.warning(f"Failed to fetch engineer profile: {e}")

    all_regex_issues = []
    combined_diff_for_ai = ""

    # --- LOOP THROUGH EACH FILE ---
    for file_data in files_list:
        filename = file_data.get('filename', 'unknown')
        patch_text = file_data.get('patch', '')

        if not patch_text:
            continue

        # 2. Run Regex Scan
        file_issues = scan_diff_for_patterns(patch_text, filename=filename)
        
        for issue in file_issues:
            issue['file'] = filename
            all_regex_issues.append(issue)

        # 3. Collect text for AI
        if len(combined_diff_for_ai) < 10000: 
            combined_diff_for_ai += f"\n--- File: {filename} ---\n{patch_text}\n"

    # --- DECISION LOGIC ---

    # PHASE 1: REGEX BLOCKING
    if all_regex_issues:
        # Update Memory: Record bad behavior
        update_engineer_profile(author, all_regex_issues)

        return {
            **metadata,
            "incident": "Hardcoded Secrets / PII Detected",
            "summary_en": f"Found {len(all_regex_issues)} critical patterns across {len(files_list)} files.",
            "summary_jp": f"複数のファイルで{len(all_regex_issues)}件の機密情報が検出されました。",
            "action": "BLOCK",
            "severity": "critical",
            "fix": "Remove hardcoded values.",
            "diff": combined_diff_for_ai[:2000], 
            "issues": all_regex_issues
        }

    # PHASE 2: AI SCAN
    if combined_diff_for_ai:
        try:
            # Pass Engineer Context to AI
            ai_result = analyze_code_with_gemini(combined_diff_for_ai, engineer_context=engineer_context)
            
            # Update Memory: Record AI findings
            ai_issues = ai_result.get("vulnerabilities", [])
            update_engineer_profile(author, ai_issues)

            if not ai_result:
                logger.warning("AI analysis returned empty result")
                ai_result = {
                    "summary_en": "AI analysis unavailable",
                    "summary_jp": "AI分析が利用できません",
                    "action": "PASS",
                    "severity": "low"
                }

            # --- CHAMPION LOGIC RESTORED HERE ---
            # Only runs if the code is CLEAN (PASS)
            if ai_result.get("action") == "PASS":
                champion_data = check_security_champion(combined_diff_for_ai)
                
                if champion_data and champion_data.get('is_security_fix'):
                    badge = champion_data.get('badge', '🛡️')
                    praise = champion_data.get('praise_message', 'Great work!')
                    
                    # Append praise to the existing summary (Safe append)
                    current_summary = ai_result.get("summary_en", "")
                    current_summary_jp = ai_result.get("summary_jp", "")
                    
                    ai_result["summary_en"] = f"{current_summary}\n\n🏆 **Security Champion!**\n{badge} {praise}"
                    ai_result["summary_jp"] = f"{current_summary_jp}\n\n🏆 **セキュリティ・チャンピオン！**\n{badge} 素晴らしい修正です。"
            # ------------------------------------

            return {
                **metadata,
                "incident": ai_result.get("summary_en", "Security Audit"),
                "summary_en": ai_result.get("summary_en"),
                "summary_jp": ai_result.get("summary_jp"),
                "action": ai_result.get("action", "PASS"),
                "severity": ai_result.get("status", "low"),
                "fix": ai_result.get("fix", "N/A"),
                "diff": combined_diff_for_ai[:1000],
                "issues": ai_result.get("vulnerabilities", [])
            }

        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Fall through to PASS
    
    # PHASE 3: EMPTY / NO ISSUES
    return {
        **metadata,
        "incident": "No changes to scan",
        "action": "PASS",
        "severity": "low",
        "summary_en": "No logic changes detected.",
        "summary_jp": "変更はありません。",
        "issues": []
    }