#!/usr/bin/env bash
# Runs the LAVENTRA GROW:TURN 10-static batch through the winning-statics pipeline.
# Usage: run.sh            -> product photo (if missing) + all 10 statics
#        run.sh 3 7        -> only statics 03 and 07
set -euo pipefail

BATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$BATCH_DIR" rev-parse --show-toplevel)"
SKILL="$REPO_ROOT/.claude/skills/winning-statics"
REFS="$SKILL/references/images"
PRODUCT="$BATCH_DIR/product/laventra-grow-turn.png"
OUT="$BATCH_DIR/output"
mkdir -p "$BATCH_DIR/product" "$OUT"

# static number -> reference image
declare -A REF=(
  [01]=ref-03 [02]=ref-15 [03]=ref-10 [04]=ref-44 [05]=ref-09
  [06]=ref-01 [07]=ref-12 [08]=ref-41 [09]=ref-19 [10]=ref-36
)

if [[ ! -f "$PRODUCT" ]]; then
  echo "== Step 0: synthesizing clean product photo (QC it before trusting the batch)"
  PYTHONPATH="$SKILL/scripts" python3 - "$BATCH_DIR/prompts/00-product-photo.txt" "$PRODUCT" <<'PY'
import sys, urllib.request, higgsfield_client
prompt = open(sys.argv[1], encoding="utf-8").read().strip()
result = higgsfield_client.subscribe("nano-banana", {"prompt": prompt,
                                                     "aspect_ratio": "1:1",
                                                     "image_urls": []})
url = result["images"][0]["url"]
try:
    with urllib.request.urlopen(url, timeout=120) as r, open(sys.argv[2], "wb") as f:
        f.write(r.read())
    print(f"OK: saved {sys.argv[2]}")
except Exception as e:
    print(f"generated OK but download blocked ({e}); asset URL: {url}")
    sys.exit(1)
PY
fi

NUMS=("$@")
[[ ${#NUMS[@]} -eq 0 ]] && NUMS=(01 02 03 04 05 06 07 08 09 10)

for raw in "${NUMS[@]}"; do
  n=$(printf "%02d" "$((10#$raw))")
  prompt_file=$(ls "$BATCH_DIR/prompts/$n"-*.txt)
  echo "== Static $n (${REF[$n]})"
  PYTHONPATH="$SKILL/scripts" python3 "$SKILL/scripts/generate_static.py" \
    --provider higgsfield-api \
    --reference "$REFS/${REF[$n]}.png" \
    --product "$PRODUCT" \
    --prompt-file "$prompt_file" \
    --aspect-ratio 4:5 \
    --out "$OUT/static-$n.png"
done
echo "Done. QC every image in $OUT before shipping."
