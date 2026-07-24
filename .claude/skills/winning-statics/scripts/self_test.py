#!/usr/bin/env python3
"""One-time self-test for the Winning-Statics setup.

Verifies, in order:
  1. GEMINI_API_KEY is set in the environment
  2. The google-genai and pillow packages are installed
  3. The key is accepted by the Gemini API (a tiny, sub-cent text call)

Run:  python3 self_test.py
"""

import os
import sys


def fail(msg: str) -> None:
    print(f"  FAIL — {msg}")
    sys.exit(1)


def main() -> None:
    print("Winning-Statics self-test")

    print("[1/3] Checking GEMINI_API_KEY ...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        fail("GEMINI_API_KEY is not set. Follow GEMINI_SETUP.md, then "
             'export GEMINI_API_KEY="your-key-here" and re-run.')
    print("  OK — key found in environment (never printed, never stored).")

    print("[2/3] Checking dependencies ...")
    try:
        from google import genai  # noqa: F401
        import PIL  # noqa: F401
    except ImportError as e:
        fail(f"missing package ({e}). Fix: pip install google-genai pillow")
    print("  OK — google-genai and pillow installed.")

    print("[3/3] Verifying the key with a tiny API call ...")
    from google import genai
    client = genai.Client(api_key=api_key)
    try:
        client.models.generate_content(model="gemini-2.0-flash", contents="ping")
    except Exception as e:
        msg = str(e)
        if "API key not valid" in msg or "API_KEY_INVALID" in msg:
            fail("the API rejected this key. Re-copy it from "
                 "https://aistudio.google.com (watch for extra spaces).")
        fail(f"unexpected API error: {msg}")
    print("  OK — key accepted by the Gemini API.")

    print("\nAll checks passed. You're ready to generate statics.")


if __name__ == "__main__":
    main()
