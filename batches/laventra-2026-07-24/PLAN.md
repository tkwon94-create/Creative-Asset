# LAVENTRA GROW:TURN — 10-Static Batch Plan (2026-07-24)

**Product:** LAVENTRA GROW:TURN Ampoule — scalp serum with built-in fine-bristle brush
applicator, 100 ml / 3.38 fl oz. Label ingredients: "(V)BioExo-Water(Heartleaf)", "SCALP
CLERA". K-beauty biotech scalp-care positioning.

**Avatar & angle:** Stay-at-home moms with thinning hair / postpartum & stress shedding
(widening part line, more hair in the brush). Angle: a 2-minute at-home Korean scalp
ritual for visibly thicker, fuller hair — no salon appointments.

**Market:** US (USD, US spelling). **Aspect ratio:** 4:5 (product photo 1:1).
**Brand palette:** matte white + burnt orange (#B75A2B) + near-black text, clean minimal
K-beauty aesthetic (taken from the product label; the website blocks automated visitors
from this environment, so send a full-page PDF snapshot to refine typography/claims).

## The batch (Smart Mix, weighted problem-aware)

| # | Ref | Family | Concept | Angle note |
|---|-----|--------|---------|-----------|
| 01 | ref-03 | 7 Editorial | Korean scalp-ritual long headline (#1 of 238, 72 days) | Near-native fit: K-beauty scalp ritual vs US shampoo habits |
| 02 | ref-15 | 1 Photo B/A | Split comparison, one head, part line "without / with" (#1 in a 167-ad account) | Realism protocol; before protected from beautifying |
| 03 | ref-10 | 2 Illustrated timeline | Hair-density silhouettes Before → 2 wks → 6 wks → 12 wks, oversized tube | Staged plausibility |
| 04 | ref-44 | 2 Line-art progress | Elegant single-line sketches Week 1/4/8, product inset | Premium aesthetic matches K-beauty |
| 05 | ref-09 | 8 Problem-agitation | 3D follicle render, healthy vs dormant — no product | "The real reason your part keeps getting wider" |
| 06 | ref-01 | 2 Blame reframe | "You're not losing hair — your scalp environment is" two-figure diagram | Reframes blame away from mom |
| 07 | ref-12 | 3 Callout X-pattern | Tube centered, 4 callouts (brush, Heartleaf exosome water, Scalp Clera, absorbs clean) | UK regulator badge swapped for guarantee/rating chip |
| 08 | ref-41 | 4 Complement table | "What your shampoo does / what LAVENTRA adds" | Positions WITH shampoo, genericized |
| 09 | ref-19 | 5 Testimonial portrait | Mom at kitchen table holding tube under serif quote | PLACEHOLDER QUOTE — needs real review before publishing |
| 10 | ref-36 | 6 Big claim | Type-scale contrast: "2 YEARS of postpartum shedding / TURNED AROUND AT HOME" | Simple brutal type contrast |

## Placeholders that need the user's sign-off before running ads

- **#09 quote + attribution** ("Emily K., 34, mom of two") is proposed placeholder copy,
  not a real customer — replace with a real review or don't run it.
- Any star-rating / review-count chip is rendered as a generic "★★★★★" visual with no
  count claimed; add real numbers if available.
- No guarantee is claimed anywhere (site guarantee terms unknown). If there's a real
  money-back guarantee, it should be added to #07's trust bar.
- Platform heads-up: #02 (photographic before/after on a real person) can trip Meta's
  personal-health ad policies in some accounts; #05 shows anatomy renders — both are
  standard in this niche but review before launch.

## How to run

Requires Higgsfield platform credits (the account currently has none — that is the only
blocker) and `HF_API_KEY`/`HF_API_SECRET` in the environment.

```bash
bash batches/laventra-2026-07-24/run.sh            # product photo + all 10
bash batches/laventra-2026-07-24/run.sh 3 7        # regenerate specific numbers
```

Step 0 synthesizes the clean LAVENTRA product photo (`product/laventra-grow-turn.png`)
from the label spec, since the original photo lives only in the chat thread; QC it
against the real tube before the statics run.

## QC status after 3 generation rounds (2026-07-24)

| # | Status | Notes |
|---|--------|-------|
| 01 | NEAR-MISS | Strong layout; "entarely" + one garbled body line remain |
| 02 | FLAGGED | Headline still drops "to"; round-3 visual has the comparison inverted |
| 03 | FLAGGED | Text now clean but rendered 6 panels instead of 4 |
| 04 | PASS | All text correct; letterbox bars should be cropped before launch |
| 05 | PASS | Letter-perfect, clean anatomy split |
| 06 | PASS | Letter-perfect ("starved roots" swap); thin bars, crop before launch |
| 07 | NEAR-MISS | Trust bar fixed; "right the root", doubled "even", stray paren |
| 08 | FLAGGED | Table format degrades every round; header garbled |
| 09 | NEAR-MISS | Portrait excellent; quote still renders "thas't it" |
| 10 | FLAGGED | "POSTPARTUM" misrenders every round in huge type |

Lesson captured: layered base-prompt + corrections created conflicting copy on 09/10;
any further round should rewrite the base prompt files to the final copy and delete
the correction layers. Big display type with unusual words (POSTPARTUM) and dense
multi-line copy are the model's consistent weak spots; short-copy formats pass.
