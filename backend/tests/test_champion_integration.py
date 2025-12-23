# backend/tests/test_champion_integration.py
import sys
import os
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# 2. Setup Path to find 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.scanner import run_security_scan

def run_test():
    print("\n🏆 TESTING SECURITY CHAMPION INTEGRATION...")
    print("="*60)

    # --- SCENARIO: A "Good" PR (Fixing SQL Injection) ---
    # This looks like a fix: removing f-string, adding parameterized query
    good_diff = """
    def login(user, pw):
    -   cursor.execute(f"SELECT * FROM users WHERE user = '{user}'")
    +   cursor.execute("SELECT * FROM users WHERE user = %s", (user,))
        return cursor.fetchone()
    """

    files_list = [
        {
            "filename": "backend/app/auth.py",
            "patch": good_diff
        }
    ]

    print("1️⃣  Simulating a Security Fix (SQL Injection remediation)...")
    print("2️⃣  Running Scanner...")

    # Run the scan
    result = run_security_scan(files_list)

    print("\n3️⃣  Analyzing Result:")
    print(f"   Action:  {result.get('action')}")
    print(f"   Summary: {result.get('summary_en')}")

    # VERIFICATION LOGIC
    if result.get('action') == "PASS" and "🏆" in result.get('summary_en', ''):
        print("\n✅ SUCCESS: Champion Logic Triggered!")
        print("   - Scan Passed")
        print("   - Trophy Emoji found")
        print("   - Praise message generated")
    else:
        print("\n❌ FAILED: Champion Logic did not trigger.")
        print("   (Note: This might happen if AI decides the fix isn't significant enough)")

    print("="*60 + "\n")

if __name__ == "__main__":
    run_test()