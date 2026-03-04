# SaleAnto — Re-Prompting & Master Prompt Evolution System
## How to Fix Bad Images, Learn From Failures, and Keep the Master Prompt Accurate

**Version:** 1.0  
**Date:** March 2026  
**Companion to:** SaleAnto Image Generation Instructions v1.0

---

## Table of Contents

1. [The Core Problem This Solves](#1-the-core-problem)
2. [The Full Feedback Loop (Overview)](#2-the-full-feedback-loop)
3. [Step 1 — Diagnose: What Exactly Is Wrong?](#3-diagnose)
4. [Step 2 — Classify: Is This a One-Off Fix or a Systemic Issue?](#4-classify)
5. [Step 3 — Re-Prompt: Targeted Fix for This Image](#5-re-prompt)
6. [Step 4 — Decide: Should the Master Prompt Change?](#6-decide)
7. [Step 5 — Update the Master Prompt (Safely)](#7-update-master-prompt)
8. [Step 6 — Regression Test (Prove It's Better)](#8-regression-test)
9. [Step 7 — Publish & Document](#9-publish)
10. [The Master Prompt Anatomy (What Lives Where)](#10-master-prompt-anatomy)
11. [Prompt Inheritance & Override Rules](#11-inheritance-rules)
12. [The Prompt Evolution Log (Living Document)](#12-evolution-log)
13. [Re-Prompt Patterns (Copy-Paste Fix Library)](#13-reprompt-patterns)
14. [Worked Example: Full Cycle Start to Finish](#14-worked-example)
15. [Anti-Patterns: What NOT to Do](#15-anti-patterns)

---

## 1. The Core Problem

Right now, when an image comes out wrong, one of two things happens:

**Bad Path A:** Someone edits the prompt randomly, regenerates, and if it looks okay, moves on. The original prompt is unchanged. Next time the same problem reappears.

**Bad Path B:** Someone edits the master prompt directly to fix one image. This fixes that case but breaks three other cases that were working fine.

**What should happen:** Diagnose → fix this image → decide if the master prompt needs to change → if yes, change it safely with regression testing → document what changed and why.

---

## 2. The Full Feedback Loop

```
   ┌──────────────────────────────────────────────────────────────────┐
   │                                                                  │
   │  GENERATE IMAGE                                                  │
   │       │                                                          │
   │       ▼                                                          │
   │  IMAGE OK? ───── YES ──→ SHIP IT ──→ TRACK ENGAGEMENT           │
   │       │                                      │                   │
   │       NO                                     │                   │
   │       │                                      │                   │
   │       ▼                                      │                   │
   │  ┌─────────────┐                             │                   │
   │  │ STEP 1      │                             │                   │
   │  │ DIAGNOSE    │  What exactly is wrong?     │                   │
   │  │ (tag the    │  Use the failure taxonomy   │                   │
   │  │  problem)   │                             │                   │
   │  └──────┬──────┘                             │                   │
   │         │                                    │                   │
   │         ▼                                    │                   │
   │  ┌─────────────┐                             │                   │
   │  │ STEP 2      │                             │                   │
   │  │ CLASSIFY    │  One-off or systemic?       │                   │
   │  └──────┬──────┘                             │                   │
   │         │                                    │                   │
   │    ┌────┴────┐                               │                   │
   │    │         │                               │                   │
   │  ONE-OFF   SYSTEMIC                          │                   │
   │    │         │                               │                   │
   │    ▼         ▼                               │                   │
   │  ┌────────┐ ┌────────────┐                   │                   │
   │  │ STEP 3 │ │ STEP 3     │                   │                   │
   │  │ FIX    │ │ FIX this   │                   │                   │
   │  │ this   │ │ image      │                   │                   │
   │  │ image  │ │    +       │                   │                   │
   │  │ only   │ │ STEP 4-7   │                   │                   │
   │  │        │ │ UPDATE     │                   │                   │
   │  │        │ │ MASTER     │                   │                   │
   │  └───┬────┘ └─────┬──────┘                   │                   │
   │      │            │                          │                   │
   │      └─────┬──────┘                          │                   │
   │            │                                 │                   │
   │            ▼                                 │                   │
   │     LOG THE FIX                              │                   │
   │     (what failed, what fixed it)             │                   │
   │            │                                 │                   │
   │            └────────────────┬────────────────┘                   │
   │                             │                                    │
   │                             ▼                                    │
   │                    WEEKLY REVIEW                                 │
   │                    (look at all failure logs,                    │
   │                     spot patterns,                               │
   │                     batch-update master prompts)                 │
   │                                                                  │
   └──────────────────────────────────────────────────────────────────┘
```

---

## 3. Step 1 — Diagnose: What Exactly Is Wrong?

**Never say "the image is bad." Always say exactly WHY it's bad.** Use this failure taxonomy:

### 3.1 Failure Taxonomy (Tag Every Bad Image)

| Code | Category | Description | Example |
|------|----------|-------------|---------|
| `C1` | **COLOR_WRONG** | Dominant colors don't match brand palette | Image is blue when brand is green/orange |
| `C2` | **COLOR_DULL** | Colors are washed out, desaturated, or muddy | Everything looks gray and lifeless |
| `C3` | **COLOR_OVER** | Colors are over-saturated or neon | Looks like a children's toy, not the brand |
| `S1` | **STYLE_MISMATCH** | Art style doesn't match brand identity | Got photorealistic when brand is illustration |
| `S2` | **STYLE_GENERIC** | Looks like generic stock photography | No brand personality, could be anyone's post |
| `L1` | **LAYOUT_CLUTTERED** | Too many elements, no visual hierarchy | Background has random objects everywhere |
| `L2` | **LAYOUT_NO_SAFE_ZONE** | No clean space for text overlay | Busy pattern or objects where text should go |
| `L3` | **LAYOUT_SUBJECT_SMALL** | Main subject is tiny or lost | Product is a small dot in the corner |
| `L4` | **LAYOUT_WRONG_ANGLE** | Camera angle is wrong for the purpose | Flat top-down when it should be 3/4 angle |
| `A1` | **ARTIFACT_DISTORTION** | Melted shapes, extra limbs, warped objects | Product has weird bent edges |
| `A2` | **ARTIFACT_TEXT** | AI generated unwanted text/letters in image | Random words or symbols appeared |
| `A3` | **ARTIFACT_EXTRA_OBJECTS** | Unexpected objects in the scene | Asked for one bottle, got three |
| `M1` | **MOOD_WRONG** | Emotional tone doesn't match intent | Got dark/moody when should be bright/cheerful |
| `M2` | **MOOD_FLAT** | No visual impact, no emotion, boring | Technically correct but nobody would stop scrolling |
| `B1` | **BACKGROUND_BUSY** | Background competes with subject | Detailed environment when should be simple gradient |
| `B2` | **BACKGROUND_WRONG** | Setting/environment is wrong | Got outdoor forest when should be studio |
| `T1` | **TEXTURE_PLASTIC** | Surfaces look fake, plasticky, or CG | Skin looks like silicone, fabric looks rendered |
| `T2` | **TEXTURE_WRONG** | Materials don't match description | Asked for matte, got glossy |
| `P1` | **PROMPT_IGNORED** | Model clearly ignored a key instruction | Asked for red, got blue. Asked for minimal, got busy |
| `P2` | **PROMPT_REWRITTEN** | OpenAI's revised_prompt changed critical intent | Your careful instructions got simplified away |

### 3.2 How to Diagnose

```
FOR every bad image:
  1. Look at the image for 5 seconds — what's the first thing that feels wrong?
  2. Tag it with 1-3 codes from the taxonomy above
  3. Compare the ORIGINAL prompt to the REVISED_PROMPT (from API response)
     - Did OpenAI rewrite something important?
     - Did a key instruction get dropped?
  4. Write a ONE-SENTENCE diagnosis:
     "L1 + C1: Image is cluttered with extra objects, and the colors are 
      blue/purple instead of the brand's green/cream palette."
```

---

## 4. Step 2 — Classify: One-Off or Systemic?

This is the critical decision that determines whether you just fix this image or update the master prompt.

### Decision Matrix

| Signal | Classification | Action |
|--------|---------------|--------|
| This is the **first time** you've seen this specific failure | **One-off** | Fix this image only (Step 3), log it |
| You've seen this **same failure 3+ times** across different posts | **Systemic** | Fix this image + update master prompt (Steps 3-7) |
| The failure is caused by a **missing instruction** that should apply to ALL images | **Systemic** | Update master prompt |
| The failure is caused by a **vague instruction** that the model interprets randomly | **Systemic** | Tighten the instruction in master prompt |
| The failure is **specific to one unusual post type** and wouldn't affect others | **One-off** | Fix this image only, maybe add a new Layout Preset |
| The `revised_prompt` shows OpenAI **consistently rewrites** a specific instruction | **Systemic** | Rephrase that instruction in master prompt |
| The failure only happens with a **specific product or subject** | **One-off** | Fix the Creative Brief for that subject |

### Tracking Pattern (Simple Counter)

Keep a running tally:

```
FAILURE_LOG:
  C1 (COLOR_WRONG): ||||| (5 times) ← SYSTEMIC — update master
  L1 (LAYOUT_CLUTTERED): ||| (3 times) ← SYSTEMIC — update master  
  A2 (ARTIFACT_TEXT): || (2 times) ← Watch — one more and it's systemic
  L3 (LAYOUT_SUBJECT_SMALL): | (1 time) ← One-off for now
```

**Rule of thumb: If you see the same failure code 3 times, it's systemic. Update the master prompt.**

---

## 5. Step 3 — Re-Prompt: Targeted Fix for This Image

### THE GOLDEN RULE: Never rewrite the entire prompt. Patch it.

When an image is wrong, you add a **targeted correction** to the existing prompt. This is faster, more controlled, and easier to learn from.

### 5.1 The Re-Prompt Formula

```
REPROMPT = ORIGINAL_PROMPT + CORRECTION_PATCH
```

The correction patch addresses ONLY the specific failure. It goes at the END of the prompt (because image models pay most attention to the beginning and end).

### 5.2 Correction Patches by Failure Code

| Code | Failure | Correction Patch (append to prompt) |
|------|---------|-------------------------------------|
| `C1` | Wrong colors | `"IMPORTANT: The dominant colors in this image MUST be {correct_hex_1} and {correct_hex_2}. Do NOT use {wrong_color}. The brand palette must be clearly visible."` |
| `C2` | Dull colors | `"IMPORTANT: Increase color vibrancy and saturation. Colors should feel fresh, vivid, and energetic — not washed out or muted."` |
| `C3` | Over-saturated | `"IMPORTANT: Reduce saturation. Colors should feel natural and refined, not neon or electric. Tone down all colors by approximately 30%."` |
| `S1` | Wrong art style | `"IMPORTANT: This must be {correct_style — e.g., clean editorial photography}. Do NOT render as {wrong_style — e.g., illustration, 3D, cartoon}."` |
| `S2` | Generic looking | `"IMPORTANT: This should NOT look like generic stock photography. Add brand personality through {specific detail — e.g., unique color grading, creative prop arrangement, distinctive angle}."` |
| `L1` | Cluttered | `"IMPORTANT: Simplify significantly. Remove ALL secondary objects and background details. Keep ONLY the main subject against a clean, simple background. Maximum 2-3 elements in the entire frame."` |
| `L2` | No safe zone | `"IMPORTANT: The {top/bottom/left/right} {30%} of the image MUST be completely empty — no objects, no patterns, no details. Just a smooth, uniform gradient or solid color suitable for text overlay."` |
| `L3` | Subject too small | `"IMPORTANT: Make the main subject MUCH larger. It should fill at least 50-60% of the frame. Bring the camera closer."` |
| `L4` | Wrong angle | `"IMPORTANT: Camera angle must be {correct_angle — e.g., straight-on at eye level / 45-degree overhead / flat lay top-down}. Do NOT use {wrong_angle}."` |
| `A1` | Distortion | `"IMPORTANT: All objects must be physically realistic with clean, precise edges. No warping, no melting, no impossible geometry. Every shape must be structurally correct."` |
| `A2` | Unwanted text | `"CRITICAL: Do NOT generate ANY text, letters, numbers, words, characters, or symbols anywhere in the image. The image must be completely text-free."` |
| `A3` | Extra objects | `"IMPORTANT: Include ONLY the objects explicitly described. Do NOT add any additional items, props, or decorative elements. If I described one bottle, show exactly one bottle."` |
| `M1` | Wrong mood | `"IMPORTANT: The emotional mood must be {correct_mood — e.g., bright, cheerful, energetic}. Adjust lighting to be {warmer/cooler/brighter/softer}. This should feel {mood}, NOT {wrong_mood}."` |
| `M2` | Flat/boring | `"IMPORTANT: Increase visual drama. Add stronger contrast between light and shadow. Create a clear focal point that draws the eye. This image needs to stop someone from scrolling."` |
| `B1` | Busy background | `"IMPORTANT: Background must be extremely simple — a smooth gradient, a solid color, or a very subtly textured surface. NO detailed environments, NO complex patterns, NO secondary scenes."` |
| `B2` | Wrong setting | `"IMPORTANT: The setting must be {correct_setting — e.g., a clean studio environment}. Do NOT place the subject in {wrong_setting — e.g., outdoor, nature, urban}."` |
| `T1` | Plastic look | `"IMPORTANT: All surfaces should have realistic, natural textures. Avoid any CG or rendered appearance. Materials should look tangible — you should almost feel the texture."` |
| `P1` | Instruction ignored | `"CRITICAL — HIGHEST PRIORITY: {repeat the ignored instruction, rephrased more forcefully and placed prominently}."` |

### 5.3 Re-Prompt Limits

```
Attempt 1: Original prompt → generates image → fails
Attempt 2: Original prompt + correction patch 1 → regenerate
Attempt 3: Original prompt + correction patch 1 + correction patch 2 → regenerate
STOP AFTER 3 ATTEMPTS.

If 3 attempts all fail:
  → The prompt structure is fundamentally wrong for this brief
  → Go back to the Creative Brief or Layout Preset and redesign
  → Do NOT keep appending patches — the prompt gets too long and contradictory
```

### 5.4 What Gets Logged After Re-Prompting

```json
{
  "original_run_id": "uuid-of-first-attempt",
  "reprompt_run_id": "uuid-of-this-attempt",
  "attempt_number": 2,
  "failure_codes": ["C1", "L1"],
  "diagnosis": "Colors were blue instead of brand green, and background had random objects",
  "correction_patches_applied": [
    "IMPORTANT: The dominant colors MUST be #4CAF50 and #FFF8E1...",
    "IMPORTANT: Simplify significantly. Remove ALL secondary objects..."
  ],
  "result": "pass | fail",
  "score": 5,
  "notes": "Colors fixed, composition much cleaner. Shipping this one.",
  "recommendation": "one-off | update_master"
}
```

---

## 6. Step 4 — Decide: Should the Master Prompt Change?

After fixing the image, ask yourself:

### The Decision Checklist

```
□ Have I seen this same failure 3+ times? → YES = update master
□ Is the fix something that should apply to ALL future images for this brand?
  → YES = update master
  → NO (it's specific to this one subject/brief) = don't update
□ Would adding this fix to the master prompt make it too long? (>250 words)
  → YES = consider adding it to the Layout Preset or Brand Style Pack instead
  → NO = safe to add to master
□ Could this fix break images that are currently working well?
  → YES = be very careful, test thoroughly (Step 6)
  → NO = lower risk, still test
□ Is the fix a TIGHTER version of an existing instruction?
  (e.g., changing "use brand colors" to "dominant colors MUST be #hex1 and #hex2")
  → YES = this is a refinement, usually safe
□ Is the fix a NEW instruction that didn't exist before?
  (e.g., adding "never use cool blue tones" when that wasn't specified)
  → YES = be careful, this could restrict future creative flexibility
```

### The Three Possible Outcomes

| Outcome | When | Action |
|---------|------|--------|
| **Don't update master** | One-off failure, specific to this subject or brief | Log the fix, move on |
| **Update Brand Style Pack** | The fix is about brand-level rules (colors, style, mood, must-avoid) | Update the Brand Style Pack, which flows into ALL prompts |
| **Update Layout Preset** | The fix is about composition, angles, spacing for a specific content type | Update the relevant Layout Preset only |

---

## 7. Step 5 — Update the Master Prompt (Safely)

### 7.1 The Three Master Prompt Components (Reminder)

```
MASTER PROMPT = Brand Style Pack + Layout Presets + Creative Brief Template

Each is updated independently:

Brand Style Pack    → affects ALL images for this brand
Layout Preset       → affects all images of that TYPE (e.g., all "Product Hero" images)
Creative Brief Template → affects how briefs are structured (rarely changes)
```

### 7.2 Update Procedure

```
STEP A: Draft the change (don't apply yet)

  1. Open the current active version of the component you're changing
  2. Make the edit in a DRAFT copy
  3. Write a clear change description:
     - WHAT changed (exact before/after text)
     - WHY it changed (which failure codes triggered this)
     - WHICH images were failing (link to run_ids)

STEP B: Test the draft (regression check — Section 8)

  4. Run the draft version against your Golden Brief Set
  5. Compare scores to the current active version
  6. Confirm: new version is BETTER overall, not just for the one case

STEP C: Publish (if tests pass)

  7. Mark the draft as the new active version
  8. Archive the previous version (don't delete it — you may need to rollback)
  9. Record the change in the Prompt Evolution Log (Section 12)

STEP D: Monitor

  10. Watch the next 10-20 images generated with the new version
  11. If new failures appear that weren't there before → ROLLBACK immediately
```

### 7.3 What a Master Prompt Update Looks Like (Concrete Example)

**Before (Brand Style Pack v1.2):**
```
Color palette: use {primary_hex}, {secondary_hex}, and {accent_hex}.
```

**Failure pattern observed:** 5 out of 12 recent images had wrong colors (C1). The model kept introducing blues and purples not in the palette.

**After (Brand Style Pack v1.3):**
```
Color palette: the DOMINANT colors in the image must be {primary_hex} and 
{secondary_hex}, with {accent_hex} as a small highlight. Do NOT introduce 
any colors outside this palette — specifically avoid blue, purple, and neon 
tones. The brand palette must be immediately recognizable.
```

**What changed:** Made color instruction more forceful, added explicit exclusions for colors that kept appearing, emphasized dominance.

### 7.4 Types of Master Prompt Updates

| Type | Description | Risk Level | Example |
|------|-------------|------------|---------|
| **Tighten** | Make an existing vague instruction more specific | Low | "clean background" → "smooth single-color gradient, no patterns or details" |
| **Add exclusion** | Add a new item to the must-avoid list | Low | Adding "no cool blue tones" after blues kept appearing |
| **Add instruction** | Add an entirely new instruction | Medium | Adding "all surfaces must show realistic texture" |
| **Rephrase** | Reword an instruction because the model kept misinterpreting it | Medium | Changing wording that OpenAI's rewriter kept altering |
| **Restructure** | Change the order or grouping of instructions | High | Moving color instructions to the front of the prompt |
| **Remove instruction** | Delete an instruction that's causing problems | High | Removing "creative and unique" because it made outputs too unpredictable |
| **Change default** | Change a default value (color, style, mood) | High | Changing default mood from "minimal" to "vibrant" |

**Rule: Low-risk changes need testing against 3 golden briefs. High-risk changes need ALL golden briefs.**

---

## 8. Step 6 — Regression Test

### 8.1 The Test

```
INPUTS:
  - Current active prompt versions (the "baseline")
  - Draft prompt versions (the "candidate")
  - Golden Brief Set (5-10 standard briefs)

PROCESS:
  For each golden brief:
    1. Generate 2 images with the BASELINE prompts
    2. Generate 2 images with the CANDIDATE prompts
    3. Score all 4 images using the 6-question evaluation
    4. Record scores

COMPARE:
  - Baseline average score across all briefs
  - Candidate average score across all briefs

DECISION:
  - Candidate average > Baseline average → PUBLISH candidate
  - Candidate average = Baseline average → Check if the specific failure is fixed
    - If yes → PUBLISH (no regression, target problem solved)
    - If no → REJECT candidate, try a different approach
  - Candidate average < Baseline average → REJECT candidate
    - Investigate which briefs got worse and why
    - The fix for one problem created a new problem → rethink the approach
```

### 8.2 Quick Test (Dev Mode — For Low-Risk Changes)

If the change is a minor tightening or exclusion addition, you don't need to test all briefs:

```
QUICK TEST:
  1. Generate 2 images with the brief that was FAILING (confirm it's fixed)
  2. Generate 2 images with the 2 briefs most DIFFERENT from the failing one (confirm no regression)
  3. If all pass → publish
  4. If any regress → full test needed
```

### 8.3 Comparison Format

```
REGRESSION TEST REPORT
Date: 2026-03-01
Change: Brand Style Pack v1.2 → v1.3 (stronger color instruction)
Reason: C1 failures in 5/12 recent images

| Brief # | Brief Type        | Baseline Score | Candidate Score | Delta |
|---------|-------------------|---------------|-----------------|-------|
| 1       | Product Showcase  | 4/6           | 5/6             | +1    |
| 2       | Offer / Promo     | 3/6           | 5/6             | +2    |
| 3       | Tips / Carousel   | 5/6           | 5/6             | 0     |
| 4       | Lifestyle         | 4/6           | 4/6             | 0     |
| 5       | Testimonial       | 5/6           | 5/6             | 0     |

Baseline Average: 4.2/6
Candidate Average: 4.8/6
Delta: +0.6

Result: PUBLISH ✅
Notes: Color accuracy improved significantly in briefs 1 and 2. 
No regression in other briefs. Target problem (C1) resolved.
```

---

## 9. Step 7 — Publish & Document

### 9.1 Publish the Change

```
UPDATE prompt_versions SET status = 'archived' 
  WHERE prompt_id = 'customoo_brand_style' AND status = 'active';

UPDATE prompt_versions SET status = 'active' 
  WHERE prompt_id = 'customoo_brand_style' AND version = 'v1.3';
```

### 9.2 Document in the Evolution Log (Section 12)

Every published change gets an entry in the Prompt Evolution Log. This is your institutional knowledge — without it, you'll forget why decisions were made.

---

## 10. The Master Prompt Anatomy — What Lives Where

Understanding where each instruction lives prevents "edit the wrong thing" mistakes.

```
┌─────────────────────────────────────────────────────────────────┐
│                    BRAND STYLE PACK (per brand)                 │
│                                                                 │
│  Lives here:                                                    │
│    • Brand name and identity                                    │
│    • Color palette (hex codes + explicit exclusions)             │
│    • Art style (e.g., "editorial product photography")          │
│    • Mood / tone defaults                                       │
│    • Typography direction                                       │
│    • Visual motifs and signatures                               │
│    • Global must-avoid list                                     │
│    • Brand Style Anchor sentence                                │
│                                                                 │
│  Who edits: Admin only                                          │
│  How often: Rarely (when brand evolves or systemic fixes)       │
│  Affects: EVERY image for this brand                            │
│                                                                 │
│  ⚠️ CHANGES HERE AFFECT EVERYTHING — always regression test     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    LAYOUT PRESETS (per content type)             │
│                                                                 │
│  Lives here:                                                    │
│    • Composition rules (subject placement, framing)             │
│    • Camera angle                                               │
│    • Background treatment                                       │
│    • Safe zone for text overlay (where + how much)              │
│    • Depth of field                                             │
│    • Lighting direction and quality                             │
│    • Spacing and balance rules                                  │
│                                                                 │
│  Who edits: Admin only                                          │
│  How often: When adding new formats or fixing composition issues│
│  Affects: All images using that specific preset                 │
│                                                                 │
│  ⚠️ Test against all golden briefs that use this preset         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CREATIVE BRIEF (per post)                    │
│                                                                 │
│  Lives here:                                                    │
│    • Specific subject / product description                     │
│    • Platform                                                   │
│    • Post goal                                                  │
│    • Key message                                                │
│    • Campaign theme                                             │
│    • Mood override (only if different from brand default)        │
│    • Must-include elements (post-specific props, settings)      │
│    • Must-exclude elements (post-specific)                      │
│                                                                 │
│  Who edits: Creator / AI / anyone                               │
│  How often: Every single post                                   │
│  Affects: Only this one image                                   │
│                                                                 │
│  ✅ Low risk — changes don't affect other images                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    NEGATIVE CONSTRAINTS (layered)               │
│                                                                 │
│  Level 1 — Global (applies to ALL brands):                      │
│    "No text, no letters, no watermarks, no logos in image"      │
│    "No distorted shapes or artifacts"                           │
│    "No sensitive or offensive content"                          │
│                                                                 │
│  Level 2 — Brand (from Brand Style Pack):                       │
│    "No cool blue tones" (for Customoo)                          │
│    "No dark moody lighting" (for Customoo)                      │
│    etc.                                                         │
│                                                                 │
│  Level 3 — Post (from Creative Brief):                          │
│    "No human faces in this specific image"                      │
│    "No outdoor settings for this specific shot"                 │
│    etc.                                                         │
│                                                                 │
│  All three levels merge into the final prompt's DO NOT section  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Prompt Inheritance & Override Rules

When the Creative Brief conflicts with the Brand Style Pack or Layout Preset, you need clear rules:

### 11.1 Priority Order (highest to lowest)

```
1. Global Constraints      (never overridden — safety, no-text, no-artifacts)
2. Brand Style Pack        (defines the brand — rarely overridden)
3. Layout Preset           (defines the composition — can be overridden per post)
4. Creative Brief          (defines this specific post — most flexible)
```

### 11.2 Override Rules

| Scenario | Rule | Example |
|----------|------|---------|
| Brief mood conflicts with brand mood | Brief overrides, but log a warning | Brand is "calm" but this post is a sale → "energetic" is OK |
| Brief colors conflict with brand palette | Brand wins (DO NOT override) | Brief asks for blue but brand palette has no blue → reject |
| Brief asks for text in image | Global constraint wins (NO text in image, ever) | Always strip text-in-image requests |
| Brief specifies a camera angle | Brief overrides Layout Preset angle | Layout says 20° overhead, brief says flat-lay → flat-lay wins |
| Brief adds extra must-include elements | Allowed, but validate they don't conflict with brand | Adding props is fine; adding off-brand colors is not |
| Brief wants a style not in brand pack | Flag it, don't block it, log it | Brief asks for "watercolor" but brand is "photography" → warn creator, allow with logging |

### 11.3 The Prompt Compiler Must Check

```
BEFORE compiling the final prompt:
  □ Are brief colors within brand palette? (if not → warn or reject)
  □ Is brief mood compatible with brand? (if weird → warn, allow)
  □ Does brief ask for text in image? (if yes → strip it, add to overlay queue)
  □ Does brief contradict a brand must-avoid? (if yes → reject with explanation)
  □ Is the combined prompt too long? (if >300 words → trim Creative Brief details)
```

---

## 12. The Prompt Evolution Log

This is a living document that records every master prompt change. Without this, you'll lose track of why prompts look the way they do.

### 12.1 Log Entry Format

```
═══════════════════════════════════════════════════
PROMPT EVOLUTION LOG — Customoo
═══════════════════════════════════════════════════

ENTRY #001
Date: 2026-03-01
Component: Brand Style Pack
Version: v1.0 → v1.1
Changed by: [name]
Type: Tighten (existing instruction made more specific)

WHAT CHANGED:
  Before: "Color palette: {primary_hex}, {secondary_hex}, {accent_hex}."
  After:  "The DOMINANT colors in the image must be {primary_hex} and 
           {secondary_hex}, with {accent_hex} as a small highlight. 
           Do NOT introduce colors outside this palette — specifically 
           avoid blue, purple, and neon tones."

WHY:
  - Failure code: C1 (COLOR_WRONG)
  - Seen 5 times in 12 recent generations
  - Model kept introducing blue/purple tones not in palette
  - Making instruction more forceful + adding explicit exclusions

EVIDENCE:
  - Run IDs: [uuid-1, uuid-2, uuid-3, uuid-4, uuid-5]
  - All showed unwanted blue/purple despite palette being green/cream

REGRESSION TEST:
  - Baseline avg: 4.2/6
  - Candidate avg: 4.8/6
  - No regressions detected
  - Result: PASS ✅

═══════════════════════════════════════════════════

ENTRY #002
Date: 2026-03-05
Component: Layout Preset — Product Hero
Version: v1.0 → v1.1
Changed by: [name]
Type: Add instruction

WHAT CHANGED:
  Before: "The upper third of the image is empty for text overlay."
  After:  "The upper third of the image must be COMPLETELY empty — 
           no objects, no patterns, no gradients with visible shapes. 
           Just a smooth, uniform color transition suitable for white 
           or dark text overlay with full readability."

WHY:
  - Failure code: L2 (NO_SAFE_ZONE)
  - Seen 3 times specifically in Product Hero images
  - Model interpreted "empty" as "less busy" rather than truly empty
  - Added emphasis + specified what "empty" actually means

...
═══════════════════════════════════════════════════
```

---

## 13. Re-Prompt Patterns (Copy-Paste Fix Library)

These are tested patterns that work. When you encounter a failure, find the matching pattern and paste the fix.

### 13.1 Color Fixes

```
FIX: Colors completely wrong
APPEND: "CRITICAL COLOR INSTRUCTION: This image must primarily use 
{hex1} and {hex2}. These two colors should make up at least 70% of the 
visible color area. {hex3} appears only as a small accent. No other 
colors should be dominant. Specifically exclude {wrong_colors}."

FIX: Colors right but too dull
APPEND: "Increase the vibrancy and richness of all colors by 
approximately 20-30%. Colors should feel fresh and alive, with clear 
distinction between the palette colors. Avoid any muddy, gray, or 
washed-out tones."

FIX: Colors right but too neon/saturated
APPEND: "Reduce saturation to a natural, refined level. Colors should 
feel sophisticated and authentic, not electric or artificial. Think 
high-end brand photography, not digital art."
```

### 13.2 Composition Fixes

```
FIX: Image too cluttered
APPEND: "SIMPLIFY THIS IMAGE. Maximum 2-3 elements in the entire frame. 
Remove all decorative objects, secondary items, and background details. 
The background should be a simple gradient or solid color. Negative 
space is essential."

FIX: Subject too small
APPEND: "SCALE UP the main subject. It should fill at least 50-60% of 
the frame area. Bring the virtual camera significantly closer. The 
subject should be the obvious, dominant element."

FIX: No room for text overlay
APPEND: "RESERVED TEXT ZONE: The {top/bottom} {30-40}% of the image 
must be completely clear — absolutely no objects, no strong patterns, 
no visual elements. This area must have a smooth, uniform color suitable 
for overlaying {light/dark} text with full readability."

FIX: Wrong camera angle
APPEND: "CAMERA ANGLE: Shoot from {correct_angle}. Specifically, the 
camera should be positioned {description — e.g., at eye level looking 
straight at the subject / 45 degrees above looking down / directly 
overhead for a flat-lay arrangement}."
```

### 13.3 Style Fixes

```
FIX: Looks like generic stock
APPEND: "This should NOT look like generic stock photography. Add 
intentional brand personality: {specific suggestion — e.g., unique 
color grading matching the brand palette, an unexpected camera angle, 
artful negative space, or a distinctive prop arrangement that feels 
curated, not random}."

FIX: Wrong art style entirely
APPEND: "ART STYLE OVERRIDE: This MUST be rendered as {correct_style}. 
It should look like {reference — e.g., a high-end product photo from 
a fashion magazine / a clean vector illustration / a warm lifestyle 
shot from a design blog}. Do NOT render as {wrong_style}."

FIX: Looks too AI-generated
APPEND: "This should look like a real photograph taken by a professional. 
Add natural imperfections: realistic lighting falloff, subtle color 
temperature variation, authentic material textures. Avoid the 
AI-generated look of perfect symmetry, over-smoothed surfaces, 
and unnaturally even lighting."
```

### 13.4 Artifact Fixes

```
FIX: Distorted objects
APPEND: "PHYSICAL ACCURACY: Every object must be geometrically correct 
with clean, precise edges. No warping, bending, melting, or impossible 
shapes. If the object is a {product}, it must look exactly like a real 
{product} would — structurally sound and physically plausible."

FIX: Unwanted text appeared
APPEND: "ZERO TEXT RULE: This image must contain absolutely NO text, 
letters, numbers, words, characters, symbols, signs, labels, or any 
form of writing. Not even partially visible or blurred text. The image 
must be completely free of any alphanumeric content."

FIX: Extra objects appeared
APPEND: "STRICT OBJECT COUNT: Include ONLY the following objects: 
{list exactly what should appear}. Do NOT add ANY other items, props, 
elements, or decorative details beyond what is listed. Less is more."
```

### 13.5 Mood & Atmosphere Fixes

```
FIX: Too dark/moody when should be bright
APPEND: "LIGHTING OVERRIDE: This image must be bright, well-lit, and 
cheerful. Use soft, abundant light from multiple directions. No dramatic 
shadows, no dark areas, no moody atmosphere. Overall brightness should 
be high — think a bright, sunny room."

FIX: Too flat/boring
APPEND: "VISUAL IMPACT: This image needs to stop someone mid-scroll. 
Add dramatic contrast between the subject and background. Use a bold 
color pop or a striking composition asymmetry. The focal point should 
be immediately obvious and compelling."
```

---

## 14. Worked Example: Full Cycle Start to Finish

### Scenario

You're generating a **Product Showcase** image for Customoo on **Instagram Feed (4:5)**.

### Attempt 1: Generate

**Compiled Prompt (simplified for this example):**
```
Create a clean, modern product photography image for Instagram in 
portrait orientation (4:5). The scene shows a custom-designed phone 
case with a colorful geometric pattern, placed upright on a smooth 
matte white surface. The product is centered in the lower two-thirds. 
Background is a clean gradient from #4CAF50 to a lighter tint. Upper 
third is empty for text overlay. Soft diffused lighting from upper 
left. [Customoo Brand Style: modern creative photography, green-cream 
palette, approachable and vibrant.] Do NOT include any text, letters, 
logos, or watermarks. Avoid clutter.
```

**Result:** Image comes back with the phone case, but the background is **blue-purple gradient** instead of green, and there's a **random coffee cup** next to the product.

### Step 1 — Diagnose

```
Failure codes: C1 (COLOR_WRONG), A3 (ARTIFACT_EXTRA_OBJECTS)
Diagnosis: "Background is blue-purple instead of green (#4CAF50). 
An unrequested coffee cup appeared next to the product."
Check revised_prompt: OpenAI rewrote "green gradient" to 
"colorful gradient" — that's why the color changed.
```

### Step 2 — Classify

```
C1: Has this happened before? Checking failure log...
  → C1 count: 4 previous occurrences → SYSTEMIC ← mark for master update
A3: Has this happened before?
  → A3 count: 1 previous occurrence → ONE-OFF for now
```

### Step 3 — Re-Prompt (fix this image)

Append correction patches:
```
CRITICAL COLOR INSTRUCTION: The background gradient MUST use #4CAF50 
(green) transitioning to a lighter green tint. Do NOT use blue, purple, 
or any cool tones. Green must be the dominant background color.

STRICT OBJECT COUNT: Include ONLY the phone case. Do NOT add any 
additional items — no cups, no pens, no props. Just the single phone 
case on the surface.
```

**Attempt 2 Result:** Green gradient, just the phone case. Score: 5/6. Ship it.

### Step 4 — Decide on Master Prompt Update

```
C1 is systemic (5 occurrences now). The color instruction in the 
Brand Style Pack is too weak — the model keeps overriding it.
→ UPDATE BRAND STYLE PACK

A3 is still one-off (2 occurrences). Watch it.
→ DON'T UPDATE yet, but log it
```

### Step 5 — Draft Master Prompt Update

**Brand Style Pack change:**
```
Before (v1.2):
  "Color palette: {primary_hex}, {secondary_hex}, {accent_hex}."

After (v1.3 DRAFT):
  "The DOMINANT colors must be {primary_hex} and {secondary_hex}, with 
  {accent_hex} as a small highlight only. These colors should make up 
  at least 70% of the visible area. Do NOT introduce any colors outside 
  this palette — specifically avoid blue, purple, cool gray, and neon 
  tones. The brand palette must be immediately recognizable."
```

### Step 6 — Regression Test

```
Run 5 golden briefs with baseline (v1.2) and candidate (v1.3):

| Brief | Baseline | Candidate | Delta |
|-------|----------|-----------|-------|
| 1     | 4/6      | 5/6       | +1    |
| 2     | 3/6      | 5/6       | +2    |
| 3     | 5/6      | 5/6       | 0     |
| 4     | 4/6      | 5/6       | +1    |
| 5     | 5/6      | 5/6       | 0     |

Baseline avg: 4.2  →  Candidate avg: 5.0
No regressions. PASS ✅
```

### Step 7 — Publish

```
- Brand Style Pack v1.3 → active
- Brand Style Pack v1.2 → archived
- Evolution Log entry #003 written
- Team notified: "Color instruction strengthened. Watch for any 
  new issues over next 20 generations."
```

### The Outcome

The specific image is fixed. AND future images across all post types will have better color accuracy because the master prompt was updated with a tested improvement.

---

## 15. Anti-Patterns: What NOT to Do

| Anti-Pattern | Why It's Bad | Do This Instead |
|--------------|-------------|-----------------|
| **"Just make it better"** — vague re-prompts | Model doesn't know what "better" means. You get random changes. | Diagnose the specific failure, apply a targeted fix. |
| **Rewriting the entire prompt from scratch** | You lose all the refinements built up over time. The new prompt will have new problems. | Patch the existing prompt. Only replace if fundamentally broken. |
| **Editing the master prompt directly without testing** | One fix breaks three other things. | Always draft → test → publish. |
| **Not logging what you changed** | Next week you won't remember why the prompt says what it says. Someone else edits it and re-introduces the old problem. | Log every change in the Evolution Log. |
| **Stacking 5+ correction patches on one prompt** | The prompt becomes contradictory and too long. Model ignores parts. | Max 2 patches per re-prompt. If it still fails, rethink the approach. |
| **Copying a "good prompt" from the internet** | It wasn't designed for your brand, your product, or your platform. | Use it as inspiration, but always adapt through your template system. |
| **Blaming the model when prompts are vague** | Image models do exactly what you describe (or their best interpretation of it). Garbage in, garbage out. | If the output is wrong, the prompt is wrong. Improve the prompt. |
| **Changing model settings AND prompt at the same time** | You can't tell which change fixed (or broke) things. | Change one variable at a time. |
| **Skipping the revised_prompt check** | OpenAI may rewrite your prompt. You're debugging the wrong thing. | Always compare your prompt to revised_prompt in the API response. |
| **Making the prompt longer and longer** | After ~250 words, models start ignoring instructions (especially middle ones). | Keep prompts focused. Move secondary instructions to Layout Presets or Brand Style Pack. |

---

## Quick Reference: The Complete Re-Prompt Decision Tree

```
IMAGE IS WRONG
     │
     ├─→ DIAGNOSE (tag with failure codes from Section 3)
     │
     ├─→ CHECK revised_prompt (did OpenAI rewrite something critical?)
     │        │
     │        ├─ YES → the prompt needs rephrasing to survive the rewrite
     │        └─ NO  → the prompt itself needs to be stronger
     │
     ├─→ APPLY CORRECTION PATCH (from Section 13)
     │        │
     │        ├─ Fixed? → Ship it
     │        └─ Not fixed? → Try one more patch (max 3 attempts)
     │             │
     │             ├─ Fixed? → Ship it
     │             └─ Still broken? → Rethink the brief or layout preset
     │
     ├─→ CHECK FAILURE COUNT for this failure code
     │        │
     │        ├─ 1-2 occurrences → Log as one-off, move on
     │        └─ 3+ occurrences → SYSTEMIC → update master prompt
     │
     └─→ IF UPDATING MASTER:
              │
              ├─ Draft the change
              ├─ Regression test (3-10 golden briefs)
              ├─ Scores improved? → Publish
              ├─ Scores same but target fixed? → Publish
              └─ Scores dropped? → Reject, try different approach
```

---

*This document defines how SaleAnto learns from every failed image and systematically improves. The master prompt should get measurably better every week. If it's not improving, the feedback loop is broken — revisit this process.*
