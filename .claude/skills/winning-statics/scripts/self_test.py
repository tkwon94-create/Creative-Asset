#!/usr/bin/env python3
"""One-time self-test for the Winning-Statics setup.

Checks which image provider is ready:
  gemini      GEMINI_API_KEY set, google-genai + pillow installed, key accepted
  higgsfield  `higgsfield` CLI on PATH and logged in

At least one provider passing means you're ready to generate.

Run:  python3 self_test.py
"""

import os
import shutil
import subprocess
import sys


def test_gemini() -> bool:
    print("--- Provider: gemini ---")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("  SKIP — GEMINI_API_KEY not set (see GEMINI_SETUP.md to use this provider).")
        return False

    try:
        from google import genai  # noqa: F401
        import PIL  # noqa: F401
    except ImportError as e:
        print(f"  FAIL — missing package ({e}). Fix: pip install google-genai pillow")
        return False

    from google import genai
    client = genai.Client(api_key=api_key)
    try:
        client.models.generate_content(model="gemini-2.0-flash", contents="ping")
    except Exception as e:
        msg = str(e)
        if "API key not valid" in msg or "API_KEY_INVALID" in msg:
            print("  FAIL — the API rejected this key. Re-copy it from "
                  "https://aistudio.google.com (watch for extra spaces).")
        else:
            print(f"  FAIL — unexpected API error: {msg}")
        return False
    print("  OK — key accepted by the Gemini API.")
    return True


def test_higgsfield_api() -> bool:
    print("--- Provider: higgsfield-api ---")
    has_key = bool(os.environ.get("HF_KEY")
                   or (os.environ.get("HF_API_KEY") and os.environ.get("HF_API_SECRET")))
    if not has_key:
        print("  SKIP — no HF_API_KEY/HF_API_SECRET (or HF_KEY) set "
              "(see HIGGSFIELD_SETUP.md Route B to use this provider).")
        return False
    try:
        import higgsfield_client  # noqa: F401
    except ImportError:
        print("  FAIL — SDK not installed. Fix: pip install higgsfield-client")
        return False
    print("  OK — API key present and SDK installed. (Credentials are verified "
          "server-side on first upload/generation.)")
    return True


def test_higgsfield() -> bool:
    print("--- Provider: higgsfield ---")
    if not shutil.which("higgsfield"):
        print("  SKIP — `higgsfield` CLI not found (see HIGGSFIELD_SETUP.md to use "
              "this provider).")
        return False

    try:
        proc = subprocess.run(["higgsfield", "model", "list"],
                              capture_output=True, text=True, timeout=60)
    except Exception as e:
        print(f"  FAIL — could not run the CLI: {e}")
        return False

    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        low = out.lower()
        if "login" in low or "auth" in low or "unauthorized" in low:
            print("  FAIL — not logged in (sessions are short-lived). "
                  "Fix: higgsfield auth login")
        else:
            print(f"  FAIL — CLI error:\n{out.strip()}")
        return False

    if "nano_banana" in out:
        print("  OK — CLI logged in; nano_banana model available.")
    else:
        print("  OK — CLI logged in. (Couldn't confirm nano_banana in the catalog "
              "output; generation will tell you if the model name changed.)")
    return True


def main() -> None:
    print("Winning-Statics self-test\n")
    results = [test_gemini(), test_higgsfield_api(), test_higgsfield()]
    print()
    if any(results):
        print("Ready: at least one provider passed. You're set to generate statics.")
    else:
        print("No provider is ready. Set up one of:\n"
              "  - GEMINI_SETUP.md      (Google API key)\n"
              "  - HIGGSFIELD_SETUP.md  (Higgsfield CLI login or platform API key)")
        sys.exit(1)


if __name__ == "__main__":
    main()
