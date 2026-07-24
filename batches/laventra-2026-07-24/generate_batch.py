#!/usr/bin/env python3
"""Generate the batch's statics via the Higgsfield API and record result URLs.

The result CDN is unreachable from this environment, so instead of downloading,
each result URL is appended to results.json; fetch-manifest.json + CI bring the
files into the repo. Usage: generate_batch.py [NN ...] (default: all 10).
Retries with corrective text go through --suffix-file on individual reruns.
"""

import glob
import json
import os
import sys

BATCH_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BATCH_DIR, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, ".claude/skills/winning-statics/scripts"))

import generate_static  # noqa: E402  (for build_prompt)
import higgsfield_client  # noqa: E402

RAW_BASE = ("https://raw.githubusercontent.com/tkwon94-create/Creative-Asset/"
            "claude/winning-statics-product-rc8gjc/"
            ".claude/skills/winning-statics/references/images")
PRODUCT_URL = ("https://d3u0tzju9qaucj.cloudfront.net/"
               "1c0bbe60-da3c-4723-aae6-a16da75136ad/"
               "1b7ae509-3137-4a05-bf05-045b3f41a0e5.png")
REF = {"01": "ref-03", "02": "ref-15", "03": "ref-10", "04": "ref-44",
       "05": "ref-09", "06": "ref-01", "07": "ref-12", "08": "ref-41",
       "09": "ref-19", "10": "ref-36"}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    suffix = ""
    if "--suffix-file" in sys.argv:
        suffix_path = sys.argv[sys.argv.index("--suffix-file") + 1]
        suffix = "\n" + open(suffix_path, encoding="utf-8").read()
    nums = [f"{int(a):02d}" for a in args] or sorted(REF)

    results_path = os.path.join(BATCH_DIR, "results.json")
    results = json.load(open(results_path)) if os.path.exists(results_path) else {}

    for n in nums:
        prompt_file = [p for p in glob.glob(os.path.join(BATCH_DIR, "prompts", f"{n}-*.txt"))
                       if "corrections" not in p][0]
        instructions = open(prompt_file, encoding="utf-8").read().strip() + suffix
        corrections = os.path.join(BATCH_DIR, "prompts", f"{n}-corrections.txt")
        if os.path.exists(corrections):
            instructions += "\n" + open(corrections, encoding="utf-8").read()
        prompt = generate_static.build_prompt(instructions)
        print(f"== static {n} ({REF[n]})", flush=True)
        r = higgsfield_client.subscribe("nano-banana", {
            "prompt": prompt,
            "aspect_ratio": "4:5",
            "image_urls": [f"{RAW_BASE}/{REF[n]}.png", PRODUCT_URL],
        })
        url = r["images"][0]["url"]
        results[n] = url
        json.dump(results, open(results_path, "w"), indent=2)
        print(f"   {url}", flush=True)

    manifest = [{"url": u, "path": f"batches/laventra-2026-07-24/output/static-{n}.png"}
                for n, u in sorted(results.items())]
    json.dump(manifest, open(os.path.join(BATCH_DIR, "fetch-manifest.json"), "w"),
              indent=2)
    print("done: results.json and fetch-manifest.json updated", flush=True)


if __name__ == "__main__":
    main()
