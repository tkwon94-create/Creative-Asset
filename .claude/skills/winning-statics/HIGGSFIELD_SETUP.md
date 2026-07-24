# One-Time Setup — Higgsfield

Winning-Statics can generate images through [Higgsfield](https://higgsfield.ai), which
provides access to Google's Nano Banana Pro model on your Higgsfield plan — no Google
API key needed. There are two routes; either one works:

- **Route A — CLI + browser login** (simplest on your own machine): no key to manage.
- **Route B — platform API key** (works headless / in remote environments): uses
  `HF_API_KEY` + `HF_API_SECRET` from your Higgsfield platform dashboard.

## What it costs

Generation draws on your Higgsfield plan's credits (Nano Banana Pro is included in paid
plans). There's no per-image bill from Google — check your plan's credit allowance at
[higgsfield.ai](https://higgsfield.ai) before running large batches.

## Route A — CLI + browser login

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

## Route B — platform API key

1. **Get your key pair** from the Higgsfield platform dashboard
   ([platform.higgsfield.ai](https://platform.higgsfield.ai)): an API key and an API
   secret.

2. **Store them as environment variables** (never in a chat, file, or repo):

   ```bash
   export HF_API_KEY="your-key"
   export HF_API_SECRET="your-secret"
   ```

   (The combined form `HF_KEY="key:secret"` also works.) In a remote/cloud Claude Code
   environment, add these in the environment's settings rather than the terminal so they
   survive restarts and stay out of the transcript.

3. **Install the SDK**:

   ```bash
   pip install higgsfield-client
   ```

4. **Verify**: `python3 scripts/self_test.py`

**Note on the model path:** Higgsfield's platform API addresses models by hierarchical
paths (like `bytedance/seedream/v4/text-to-image`), and the path for Nano Banana Pro is
not publicly documented. The generation script tries a short list of likely paths and
prints the one that works so you can pin it:

```bash
export WINNING_STATICS_HF_MODEL_PATH="<the-path-that-worked>"
```

If none work, look up the exact path in your platform dashboard's model catalog and set
that variable — everything else stays the same.

## Troubleshooting

| Message you see | What it means | Fix |
|---|---|---|
| `command not found: higgsfield` | CLI not installed or not on PATH | Redo Route A step 1; open a new terminal |
| `not logged in` / `unauthorized` / login prompt | CLI session token expired (they're short-lived) | `higgsfield auth login` again |
| API rejected your credentials | Key/secret mistyped or revoked | Re-copy both values from the platform dashboard |
| `no known model path ... accepted` | Nano Banana Pro's platform path differs from the guesses | Set `WINNING_STATICS_HF_MODEL_PATH` (see Route B note) |
| Credits / quota error | Plan allowance used up | Check your plan and credits at higgsfield.ai |
| Generation succeeds but download fails | Network hiccup fetching the result URL | The error prints the asset URL — download it manually or re-run |
| Connection refused / 403 CONNECT (remote environments) | The environment's network policy blocks higgsfield.ai | Allow `*.higgsfield.ai` (and `clerk.higgsfield.ai` for Route A) in the environment's network settings |

## Notes

- The script calls: `higgsfield generate create nano_banana_2 --prompt "…"
  --aspect_ratio 4:5 --resolution 2k --image-references <reference> <product> --wait`.
  Local image paths are uploaded automatically by the CLI.
- Prefer the Gemini route instead? See [GEMINI_SETUP.md](GEMINI_SETUP.md). If both are
  set up, the script prefers Gemini; force one with `--provider higgsfield`.
