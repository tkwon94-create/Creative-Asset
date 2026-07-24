# One-Time Setup — Google API Key

Winning-Statics generates images with Google's Nano Banana Pro model using **your own
Google API key**. This walkthrough is written for someone who has never touched an API.
Five minutes, one time, done.

Your key never goes into the chat or into any file — the scripts read it from your
environment only.

## What it costs

You pay Google directly, only for what you generate: roughly **$0.13–0.14 per image**,
about **$4 for a 30-image batch**. Set a budget alert (step 4) so there are never surprises.

## Step-by-step

1. **Create a free account** at [aistudio.google.com](https://aistudio.google.com)
   (any Google account works — the same one you use for Gmail is fine).

2. **Click "Get API Key"** in the left sidebar, then **"Create API key"**.
   A long string of letters and numbers appears — that's your key. Copy it.

3. **Enable billing.** Nano Banana Pro is a paid model, so Google asks for a payment
   method. In AI Studio, follow the billing prompt (or go to your Google Cloud billing
   settings). You only pay for what you generate.

4. **Set a budget alert.** In Google Cloud billing, create a budget (for example $10/month)
   with an email alert. This is your safety net.

5. **Store the key in an environment variable** called `GEMINI_API_KEY`:

   **Mac / Linux** — add to `~/.zshrc` or `~/.bashrc`:
   ```bash
   export GEMINI_API_KEY="paste-your-key-here"
   ```
   Then open a new terminal (or run `source ~/.zshrc`).

   **Windows (PowerShell)**:
   ```powershell
   [Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "paste-your-key-here", "User")
   ```
   Then open a new terminal.

6. **Install the two Python packages** the scripts need:
   ```bash
   pip install google-genai pillow
   ```

7. **Ask Claude to run the self-test** (or run it yourself):
   ```bash
   python3 scripts/self_test.py
   ```
   Three green checks and you're done forever.

## Troubleshooting

| Message you see | What it means | Fix |
|---|---|---|
| `GEMINI_API_KEY is not set` | The environment variable isn't visible to the script | Redo step 5, then open a **new** terminal so the variable loads |
| `key invalid` / `API_KEY_INVALID` | The key was mistyped or revoked | Re-copy the key from AI Studio — watch for extra spaces at the ends |
| `quota exceeded` / `429` | You hit a rate or usage limit | Wait a minute and retry; for sustained volume, raise your quota in AI Studio |
| `billing issue` / `PERMISSION_DENIED` | Billing isn't enabled for the account | Redo step 3; confirm a payment method is attached |
| `missing package` | Python can't find google-genai or pillow | `pip install google-genai pillow` (use the same Python you run the script with) |
| The model returns no image | The request was refused or filtered | Read the printed model message; adjust the instructions and retry |

## Security notes

- Never paste your key into a chat, a file, or a screenshot. Environment variable only.
- If a key ever leaks, revoke it in AI Studio and create a new one — takes 30 seconds.
- Everything generated belongs to your account and your Google key.
