#!/usr/bin/env python3
"""Generate a static ad by recreating a winning reference around the user's product.

Sends the actual reference image + the user's product photo + precise swap
instructions to Google's Nano Banana Pro image model (Gemini API). The API key is
read from the GEMINI_API_KEY environment variable only — never from a file or
argument, so it can't leak into chat logs or version control.

Usage:
    python3 generate_static.py \
        --reference references/images/ref-12.png \
        --product product.png \
        --prompt-file instructions.txt \
        --aspect-ratio 4:5 \
        --out output/static-01.png

Requires:  pip install google-genai pillow
Cost:      roughly $0.13-0.14 per generated image on the user's Google key.
"""

import argparse
import os
import sys

MODEL = os.environ.get("WINNING_STATICS_MODEL", "gemini-3-pro-image-preview")

KEY_HELP = """\
ERROR: GEMINI_API_KEY is not set.

Fix: follow GEMINI_SETUP.md in the skill folder (5 minutes, one time):
  1. Create a free account at https://aistudio.google.com
  2. Click "Get API Key" and create a key
  3. Enable billing (you only pay for what you generate — set a budget alert)
  4. export GEMINI_API_KEY="your-key-here"
"""


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference", required=True, help="Path to the winning reference static (PNG)")
    ap.add_argument("--product", required=True, help="Path to the user's clean product photo (PNG)")
    ap.add_argument("--prompt-file", required=True, help="Text file with the swap instructions")
    ap.add_argument("--aspect-ratio", default="1:1", choices=["1:1", "4:5", "3:4", "9:16", "16:9"],
                    help="Output aspect ratio (default 1:1)")
    ap.add_argument("--out", required=True, help="Output PNG path")
    args = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        die(KEY_HELP)

    for path in (args.reference, args.product, args.prompt_file):
        if not os.path.isfile(path):
            die(f"ERROR: file not found: {path}")

    try:
        from google import genai
        from google.genai import types
        from PIL import Image
    except ImportError as e:
        die(f"ERROR: missing dependency ({e}).\nFix: pip install google-genai pillow")

    with open(args.prompt_file, encoding="utf-8") as f:
        instructions = f.read().strip()

    prompt = (
        "You are recreating a proven, high-performing static image ad.\n"
        "IMAGE 1 is the winning reference ad: replicate its layout skeleton, visual "
        "hierarchy, panel geometry, and persuasion structure exactly.\n"
        "IMAGE 2 is the product that must appear in the recreation: preserve its "
        "packaging, label text, and proportions with photographic fidelity.\n"
        "Follow these swap instructions precisely. Any text in double quotes must be "
        "rendered verbatim, correctly spelled:\n\n"
        f"{instructions}"
    )

    client = genai.Client(api_key=api_key)
    reference = Image.open(args.reference)
    product = Image.open(args.product)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[prompt, reference, product],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=args.aspect_ratio),
            ),
        )
    except Exception as e:  # surface API errors with the mapped fix
        msg = str(e)
        if "API key not valid" in msg or "API_KEY_INVALID" in msg:
            die("ERROR: key invalid — your GEMINI_API_KEY was rejected.\n"
                "Fix: re-copy the key from https://aistudio.google.com (no extra spaces).")
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            die("ERROR: quota exceeded — you hit a rate or usage limit.\n"
                "Fix: wait a minute and retry; for sustained use raise your quota in "
                "Google AI Studio.")
        if "billing" in msg.lower() or "PERMISSION_DENIED" in msg:
            die("ERROR: billing issue — this model requires billing enabled on your "
                "Google account.\nFix: enable billing at https://aistudio.google.com "
                "(set a budget alert so there are no surprises).")
        die(f"ERROR: generation failed: {msg}")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    saved = False
    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            with open(args.out, "wb") as f:
                f.write(part.inline_data.data)
            saved = True
            break

    if not saved:
        text = getattr(response, "text", None) or "(no detail returned)"
        die(f"ERROR: the model returned no image. Model said:\n{text}")

    print(f"OK: saved {args.out}")


if __name__ == "__main__":
    main()
