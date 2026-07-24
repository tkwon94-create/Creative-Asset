---
name: winning-statics
description: Recreate proven, high-performing static image ads for the user's product using a library of 50 real winning reference statics and Google's Nano Banana Pro image model. Use this skill whenever the user asks for static ads, ad creatives, image ads, Facebook/Meta/TikTok statics, "make me N statics", ad variations, before/after ads, comparison ads, testimonial ads, or wants to recreate/remix winning ad formats for their product — even if they don't say "winning-statics" by name. Also use it when the user returns with performance results and asks for variations of their winners.
---

# Winning-Statics

Recreate proven, high-performing static image ads around the user's product. This skill does
NOT brainstorm ad concepts from imagination. It takes 50 real winning statics — captured from
live ad libraries with their performance receipts — and replicates their structure, hierarchy,
and psychology with the user's product, brand colors, copy angle, and market. The 80/20 of ad
creative is not inventing the wheel; it is putting the user's tire on a wheel that is already
rolling.

Every generation call sends the actual reference image — the model sees the winning ad with
its own eyes and rebuilds it around the user's product, rather than working from a lossy text
description.

## Cost transparency (say this up front)

Generation runs on the user's own Google API key at roughly **$0.13–0.14 per image**
(about $4 for a 30-image batch), and a large batch takes real minutes to generate and
quality-check. Tell the user this before generating, because surprise bills kill trust.

If `GEMINI_API_KEY` is not set in the environment, walk the user through
[GEMINI_SETUP.md](GEMINI_SETUP.md) first (5 minutes, one time). The key never goes into the
chat or into any file — scripts read it from the environment only.

## The workflow

### Step 1 — Intake

Collect these inputs. Ask plainly; don't interrogate — if the user already supplied some in
their message, only ask for what's missing:

1. **Product photo** — a clean, well-lit, high-resolution PNG on a plain background. This is
   the single biggest quality lever: the model preserves the product with the fidelity of the
   photo it's fed. A blurry photo produces blurry-label recreations and no prompt can fix that.
2. **Website address** and a **full-page PDF snapshot** of the site (browser extension like
   GoFullPage, or Print to PDF). The snapshot is the reliable source for brand colors,
   typography feel, claims, and guarantee terms — it works even when the live site blocks
   automated visitors.
3. **Avatar and angle** — in plain words, like briefing a freelancer. Example: "Stay-at-home
   moms with foot pain from being on their feet all day; angle is all-day comfort without ugly
   orthopedic looks." The more specific the human, the sharper the headlines.
4. **Advertising market** — US, UK, AUS, CA, or other. Drives spelling, currency, and
   seasonal localization.
5. **Aspect ratio** — 1:1, 4:5, or a mix.
6. **Quantity and diversity preference** — if the user doesn't want to make expert decisions,
   default to **Smart Mix**: spread the batch across concept families weighted toward how
   aware their customer is (see catalog for awareness targeting). If they know exactly what
   they want ("6 post-it notes, 4 comparisons, 10 before/afters"), obey exactly.

On quantity, advise honestly: more is not automatically better. A well-spread 20 across four
families usually teaches more than an unfocused 50. Launch, read the numbers, then come back
for variations of only the winners — that iteration loop is where this system compounds.

### Step 2 — The plan (before spending the user's money)

Read [references/catalog.md](references/catalog.md) and select references. Show the user a
table before generating anything: each planned image, which reference it's built from, which
family it belongs to, and the angle note. Let them veto anything; re-plan instantly.

Planning rules:
- Never put Reference 10 and Reference 26 in the same batch (same skeleton, kept as a
  variant example).
- Reference 20 is a deliberate low performer kept as a teaching contrast — weight it down
  unless specifically requested.
- Family 7 (Editorial/Advertorial) holds only two references. Be honest when a user asks for
  a large all-advertorial batch: the concepts are strong, but structural variety will be
  lower than other families.
- If a family obviously mismatches the product's shape or category, prefer the nearest family
  that suits it, and say why.

### Step 3 — Generation

For each planned image, build precise swap instructions and call the generation script:

```bash
python3 scripts/generate_static.py \
  --reference references/images/ref-NN.png \
  --product /path/to/product.png \
  --prompt-file /path/to/instructions.txt \
  --aspect-ratio 4:5 \
  --out output/static-NN.png
```

The swap instructions must:
- Describe the reference's structure to preserve (layout skeleton, hierarchy, panel geometry,
  trust-bar placement) and what to swap (product, labels, palette, headline, market elements).
- Put any text that must appear in the image **verbatim in double quotes** — that is how
  Nano Banana Pro renders text most accurately.
- Use the user's brand colors and typography feel taken from the website snapshot.
- Apply the market's spelling, currency, and seasonal timing.
- Apply the protocols below.

### Step 4 — Quality control

Check every image before the user sees it (view the generated file with the Read tool):

- Product label fidelity — matches the supplied product photo.
- Text spelling — every rendered word, exactly as specified.
- Structural match to the reference.
- Realistic human skin where humans appear (see realism protocol).
- No leftover wrong-market elements (currency, spelling, badges).
- For multi-panel people formats: identity locked across panels (same face, hair,
  accessories, angle).

Failures are regenerated **up to twice** with corrective instructions appended to the prompt.
Anything still failing is flagged honestly instead of slipped into the pile. If a concept
keeps failing on this product — some products photograph poorly into certain layouts — say so
and suggest the nearest family that suits the product's shape instead of silently delivering
junk.

### Step 5 — Iterate

When the user reports which numbers worked ("3, 7, and 12 performed"), produce variations of
just those — same reference skeleton with adjusted angles, or siblings from the same family.
This loop is where real testing programs live.

## Protocols (always in force)

**Human realism.** Whenever a reference involves real human skin, faces, or bodies, inject
instructions for natural texture — visible pores, fine lines, imperfect lighting, no
beauty-filter smoothing. In before/after formats, also protect the "before" from being
accidentally beautified and lock identity across panels. If the reference is deliberately
illustrated or cartoon, stand down — realistic skin on a cartoon would be wrong. The catalog
marks which references trigger this protocol.

**Localization.** Mechanical market swaps (spelling, currency, country names, seasonal
timing) happen automatically based on the market answer. Regulatory badges and credentials
never get invented — if a reference carries a UK pharmacy registration and the user sells in
the US, ask what real equivalent they hold; if none, swap that element for their review score
or guarantee.

**Borrowed authority.** Some references lean on press logos or named personalities. Replicate
the structure but replace borrowed authority with the user's real proof or generic trust
elements — a recreated ad wearing someone else's credibility is a liability, not an asset.

**Testimonial integrity.** Testimonial-format references are replicated as formats. Quote
text and attributions come from the user's real reviews, or are clearly proposed as
placeholder copy for their approval. Never invent customers as fact.

**Competitor trademarks.** Us-vs-them references get their rival brands genericized on
recreation — the layout is replicated, other brands' marks are not.

**Platform note.** Some ad platforms restrict certain formats (like before/afters in some
health verticals). Generate exactly what the user asks for and simply attach a one-line
heads-up where relevant — never alter their creative unprompted.

**Ownership.** Everything generated belongs to the user's account and Google key. The skill
ships with zero information about any other person's brand — the user's inputs in the
conversation are its only source of brand data, by design.

## The reference library

50 references in 9 families. Read [references/catalog.md](references/catalog.md) when
planning — it lists every reference's family, persuasion mechanism, performance receipts,
protocol flags, and when to use it. Family depth varies: Big-Claim Product Hero is the
deepest (13 refs); Editorial/Advertorial is the thinnest (2 refs).

| # | Family | Mechanism | Refs |
|---|--------|-----------|------|
| 1 | Photographic Before/After | Credibility through unretouched realism | 11, 15, 30 |
| 2 | Illustrated Before/After & Mechanism Diagrams | Self-diagnosis, education-not-evidence | 01, 05, 10, 26, 44, 45 |
| 3 | Annotated Product Callouts | Proof-density for the comparing shopper | 12, 32, 42 |
| 4 | Us-vs-Them Comparison | Choice architecture — you define the criteria | 04, 24, 33, 38, 41, 48 |
| 5 | Testimonial & Social-Proof | Peer proof — someone like me took the risk | 14, 17, 19, 25, 40, 46 |
| 6 | Big-Claim Product Hero | Single-claim clarity, product as proof-object | 02, 08, 13, 16, 18, 21, 28, 29, 34, 36, 37, 39, 47 |
| 7 | Editorial / Advertorial | Borrowed journalistic context | 03, 06 |
| 8 | Problem-Agitation Visual | Press the problem until clicking is the relief | 07, 09, 22, 27, 31, 49 |
| 9 | Grid, Checklist & Catalog | Breadth-of-fit — every viewer finds their square | 20, 23, 35, 43, 50 |

When in doubt, Family 6 converts across nearly every niche.

## When something goes wrong

Key errors, quota errors, and billing errors each print a specific message;
[GEMINI_SETUP.md](GEMINI_SETUP.md)'s troubleshooting table maps each one to its fix.
Generation quality issues (warped label, misspelled text, plastic-looking skin) are caught by
the QC pass and regenerated automatically up to two times.
