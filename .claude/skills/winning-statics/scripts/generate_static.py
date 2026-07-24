#!/usr/bin/env python3
"""Generate a static ad by recreating a winning reference around the user's product.

Sends the actual reference image + the user's product photo + precise swap
instructions to Google's Nano Banana Pro image model, through one of two providers:

  gemini      Google Gemini API directly. Needs GEMINI_API_KEY in the environment
              and `pip install google-genai pillow`. See GEMINI_SETUP.md.
  higgsfield  The Higgsfield CLI (model nano_banana_2). Needs the `higgsfield` CLI
              installed and logged in via `higgsfield auth login`. No API key to
              manage. See HIGGSFIELD_SETUP.md.

If --provider is omitted, the script auto-detects: GEMINI_API_KEY set -> gemini,
otherwise a `higgsfield` CLI on PATH -> higgsfield.

Credentials are never read from files or arguments — environment / CLI session
only, so they can't leak into chat logs or version control.

Usage:
    python3 generate_static.py \
        --reference references/images/ref-12.png \
        --product product.png \
        --prompt-file instructions.txt \
        --aspect-ratio 4:5 \
        --out output/static-01.png
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.request

GEMINI_MODEL = os.environ.get("WINNING_STATICS_MODEL", "gemini-3-pro-image-preview")
HIGGSFIELD_MODEL = os.environ.get("WINNING_STATICS_HF_MODEL", "nano_banana_2")

NO_PROVIDER_HELP = """\
ERROR: no image provider available.

Set up one of:
  gemini      export GEMINI_API_KEY=...        (see GEMINI_SETUP.md)
  higgsfield  install the CLI + `higgsfield auth login`  (see HIGGSFIELD_SETUP.md)
"""


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def build_prompt(instructions: str) -> str:
    return (
        "You are recreating a proven, high-performing static image ad.\n"
        "The FIRST attached image is the winning reference ad: replicate its layout "
        "skeleton, visual hierarchy, panel geometry, and persuasion structure exactly.\n"
        "The SECOND attached image is the product that must appear in the recreation: "
        "preserve its packaging, label text, and proportions with photographic fidelity.\n"
        "Follow these swap instructions precisely. Any text in double quotes must be "
        "rendered verbatim, correctly spelled:\n\n"
        f"{instructions}"
    )


# ---------------------------------------------------------------- gemini

def generate_gemini(args: argparse.Namespace, prompt: str) -> None:
    try:
        from google import genai
        from google.genai import types
        from PIL import Image
    except ImportError as e:
        die(f"ERROR: missing dependency ({e}).\nFix: pip install google-genai pillow")

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt, Image.open(args.reference), Image.open(args.product)],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=args.aspect_ratio),
            ),
        )
    except Exception as e:
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
                "Google account.\nFix: enable billing at https://aistudio.google.com.")
        die(f"ERROR: generation failed: {msg}")

    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            with open(args.out, "wb") as f:
                f.write(part.inline_data.data)
            return
    text = getattr(response, "text", None) or "(no detail returned)"
    die(f"ERROR: the model returned no image. Model said:\n{text}")


# ------------------------------------------------------------ higgsfield

def _run_higgsfield(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=900)


def generate_higgsfield(args: argparse.Namespace, prompt: str) -> None:
    base = [
        "higgsfield", "generate", "create", HIGGSFIELD_MODEL,
        "--prompt", prompt,
        "--aspect_ratio", args.aspect_ratio,
        "--resolution", args.resolution,
        "--wait",
    ]
    # Repeated-flag form first; some CLI versions take one flag with two values.
    variants = [
        base + ["--image-references", args.reference, "--image-references", args.product],
        base + ["--image-references", args.reference, args.product],
    ]

    proc = None
    for cmd in variants:
        proc = _run_higgsfield(cmd)
        if proc.returncode == 0:
            break
        # Only retry the alternate flag shape on a usage/flag-parsing error.
        if "image-references" not in (proc.stderr + proc.stdout):
            break

    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        low = out.lower()
        if "not authenticated" in low or "login" in low or "unauthorized" in low:
            die("ERROR: Higgsfield session expired or not logged in.\n"
                "Fix: run `higgsfield auth login` (tokens are short-lived), then retry.")
        if "credit" in low or "quota" in low or "insufficient" in low:
            die("ERROR: Higgsfield credits/quota issue.\n"
                "Fix: check your plan and remaining credits at https://higgsfield.ai, "
                "then retry.")
        die(f"ERROR: higgsfield generation failed:\n{out.strip()}")

    urls = re.findall(r"https://\S+", out)
    if not urls:
        die(f"ERROR: could not find a result URL in higgsfield output:\n{out.strip()}")

    # The last printed URL is the finished asset.
    url = urls[-1].rstrip(").,'\"")
    try:
        with urllib.request.urlopen(url, timeout=120) as resp, open(args.out, "wb") as f:
            shutil.copyfileobj(resp, f)
    except Exception as e:
        die(f"ERROR: generated OK but download failed ({e}).\nAsset URL: {url}")


# ----------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference", required=True, help="Path to the winning reference static (PNG)")
    ap.add_argument("--product", required=True, help="Path to the user's clean product photo (PNG)")
    ap.add_argument("--prompt-file", required=True, help="Text file with the swap instructions")
    ap.add_argument("--aspect-ratio", default="1:1",
                    choices=["1:1", "4:5", "3:4", "2:3", "3:2", "4:3", "5:4", "9:16", "16:9"],
                    help="Output aspect ratio (default 1:1)")
    ap.add_argument("--resolution", default="2k", choices=["1k", "2k", "4k"],
                    help="Output resolution, higgsfield provider only (default 2k)")
    ap.add_argument("--provider", choices=["gemini", "higgsfield"],
                    help="Force a provider; omit to auto-detect")
    ap.add_argument("--out", required=True, help="Output PNG path")
    args = ap.parse_args()

    for path in (args.reference, args.product, args.prompt_file):
        if not os.path.isfile(path):
            die(f"ERROR: file not found: {path}")

    provider = args.provider
    if not provider:
        if os.environ.get("GEMINI_API_KEY"):
            provider = "gemini"
        elif shutil.which("higgsfield"):
            provider = "higgsfield"
        else:
            die(NO_PROVIDER_HELP)
    elif provider == "gemini" and not os.environ.get("GEMINI_API_KEY"):
        die("ERROR: --provider gemini but GEMINI_API_KEY is not set. See GEMINI_SETUP.md.")
    elif provider == "higgsfield" and not shutil.which("higgsfield"):
        die("ERROR: --provider higgsfield but the `higgsfield` CLI is not on PATH.\n"
            "See HIGGSFIELD_SETUP.md.")

    with open(args.prompt_file, encoding="utf-8") as f:
        prompt = build_prompt(f.read().strip())

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    if provider == "gemini":
        generate_gemini(args, prompt)
    else:
        generate_higgsfield(args, prompt)
    print(f"OK: saved {args.out} (provider: {provider})")


if __name__ == "__main__":
    main()
