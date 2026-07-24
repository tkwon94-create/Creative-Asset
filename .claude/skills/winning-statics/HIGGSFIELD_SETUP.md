# One-Time Setup — Higgsfield

Winning-Statics can generate images through [Higgsfield](https://higgsfield.ai), which
provides access to Google's Nano Banana Pro model (`nano_banana_2`) on your Higgsfield
plan — no Google API key needed. Setup is a CLI install plus a browser login.

## What it costs

Generation draws on your Higgsfield plan's credits (Nano Banana Pro is included in paid
plans). There's no per-image bill from Google — check your plan's credit allowance at
[higgsfield.ai](https://higgsfield.ai) before running large batches.

## Step-by-step

1. **Install the Higgsfield CLI** (any one of these):

   ```bash
   # macOS / Linux
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh

   # Homebrew
   brew install higgsfield-ai/tap/higgsfield

   # npm (cross-platform, including Windows)
   npm install -g @higgsfield/cli
   ```

2. **Log in** (opens your browser to authorize):

   ```bash
   higgsfield auth login
   ```

   Sessions are short-lived — if generation ever fails with an auth error, just run
   this again.

3. **Verify** it works:

   ```bash
   python3 scripts/self_test.py
   ```

   or manually: `higgsfield model list` should print the model catalog, including
   `nano_banana_2`.

That's it. The generation script auto-detects the CLI — no keys to store anywhere.

## Troubleshooting

| Message you see | What it means | Fix |
|---|---|---|
| `command not found: higgsfield` | CLI not installed or not on PATH | Redo step 1; open a new terminal |
| `not logged in` / `unauthorized` / login prompt | Session token expired (they're short-lived) | `higgsfield auth login` again |
| Credits / quota error | Plan allowance used up | Check your plan and credits at higgsfield.ai |
| Generation succeeds but download fails | Network hiccup fetching the result URL | The error prints the asset URL — download it manually or re-run |

## Notes

- The script calls: `higgsfield generate create nano_banana_2 --prompt "…"
  --aspect_ratio 4:5 --resolution 2k --image-references <reference> <product> --wait`.
  Local image paths are uploaded automatically by the CLI.
- Prefer the Gemini route instead? See [GEMINI_SETUP.md](GEMINI_SETUP.md). If both are
  set up, the script prefers Gemini; force one with `--provider higgsfield`.
