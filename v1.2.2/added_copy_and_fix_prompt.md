# SocialSync v1.2.2 — Release Notes & Detailed Changelog

**Release Date:** March 8, 2026
**Branch:** `v1-2-2/claudeAPI-setup`

---

## Table of Contents

1. [Summary of Changes](#1-summary-of-changes)
2. [Claude API Integration (Default LLM Provider Switch)](#2-claude-api-integration)
3. [Copy Overlay Feature (New)](#3-copy-overlay-feature)
4. [AI Typography Styles (New)](#4-ai-typography-styles)
5. [9-Layer Prompt Engineering System (New)](#5-9-layer-prompt-engineering-system)
6. [Trending Service Rewrite (Google Trends)](#6-trending-service-rewrite)
7. [Extended Thinking (`think_harder`) Support](#7-extended-thinking-think_harder-support)
8. [All Prompt Changes (Before vs After)](#8-all-prompt-changes-before-vs-after)
9. [Database & Model Changes](#9-database--model-changes)
10. [API Endpoint Changes](#10-api-endpoint-changes)
11. [Frontend Changes](#11-frontend-changes)
12. [Complete File Inventory](#12-complete-file-inventory)

---

## 1. Summary of Changes

### Major Features
- **Claude API as default LLM** — Switched from OpenAI to Anthropic Claude (claude-sonnet-4-20250514) as the primary AI provider across all services
- **Copy Overlay on Images** — New full-stack feature: AI generates marketing copy text, user picks or writes custom, text is rendered onto images with professional typography via Pillow
- **AI Typography Styles** — AI generates 4 distinct visual style variants (font, color, position, opacity) with base64 preview renders
- **9-Layer Prompt Engineering** — Structured system for generating optimized DALL-E/Imagen prompts with failure diagnosis and re-prompting
- **Real Google Trends Integration** — Trending service rewritten to use live `pytrends` data instead of LLM-only generation with static seasonal tables
- **Extended Thinking** — `think_harder` mode added across all AI services, enabling Claude's 10,000-token thinking budget for deeper analysis

### New Files Created (13)
- `ai_image/fonts/` (5 TTF font files)
- `ai_image/services/copy_overlay_service.py`
- `ai_image/services/copy_generation_service.py`
- `ai_image/migrations/0005_add_prompt_engineering_fields.py`
- `ai_image/migrations/0006_add_copy_overlay_fields.py`
- `ai_video/migrations/0002_add_reference_image.py`
- `frontend/src/types/copyOverlay.ts`
- `frontend/src/types/promptEngineering.ts`
- `frontend/src/components/ai-image/CopyOverlayModal.tsx`
- `frontend/src/components/ai-image/ImageDiagnosisModal.tsx`
- `frontend/src/components/ai-image/PromptPreviewPanel.tsx`
- `frontend/src/components/ai-image/RepromptPanel.tsx`
- `frontend/src/pages/APITestPage.tsx`

### Files Modified (20)
- `accounts/services/llm_service.py`
- `ai_caption/openai_service.py`
- `ai_caption/services/adaptation_service.py`
- `ai_image/models.py`
- `ai_image/services/alt_text_service.py`
- `ai_image/services/prompt_engineering_service.py`
- `api/analytics_views.py`
- `api/caption_views.py`
- `api/creative_views.py`
- `api/scheduling_views.py`
- `api/serializers.py`
- `api/strategy_views.py`
- `api/trending_service.py`
- `api/urls.py`
- `api/views.py`
- `posts/services/hashtag_service.py`
- `frontend/src/App.tsx`
- `frontend/src/pages/AIImagePage.tsx`
- `frontend/src/pages/OverflowPage.tsx`
- `frontend/src/pages/index.ts`
- `frontend/src/services/imageService.ts`
- `frontend/src/services/videoService.ts`
- `frontend/src/types/index.ts`
- `frontend/src/components/layout/Footer.tsx`

---

## 2. Claude API Integration

### What Changed
The `UnifiedLLMService` in `accounts/services/llm_service.py` was rewritten from a 2-provider system to a 3-provider system with Claude as the new default.

### Before (v1.2.1)
- **Default provider:** `openai`
- **Supported providers:** OpenAI, Gemini
- **Fallback chain:** OpenAI → Gemini
- **Error message:** `"No AI API key configured. Go to Settings to add your OpenAI or Gemini key."`
- **LLMResponse:** No `thinking` field
- **Model mappings:** Only `OPENAI_TO_GEMINI` and `GEMINI_TO_OPENAI`

### After (v1.2.2)
- **Default provider:** `claude` (hardcoded, ignores `UserAPISettings.default_llm_provider`)
- **Supported providers:** Claude, OpenAI, Gemini
- **Fallback chain:** Claude → OpenAI → Gemini
- **Error message:** `"No AI API key configured. Please contact the administrator."`
- **LLMResponse:** New `thinking: str = ''` field for Claude extended thinking output
- **Default model:** `claude-sonnet-4-20250514`

### New Model Mapping Tables
```python
OPENAI_TO_CLAUDE = {
    'gpt-4o': 'claude-sonnet-4-20250514',
    'gpt-4o-mini': 'claude-haiku-4-5-20251001',
    'gpt-4-turbo': 'claude-sonnet-4-20250514',
}
GEMINI_TO_CLAUDE = {
    'gemini-2.0-flash': 'claude-sonnet-4-20250514',
    'gemini-2.0-flash-lite': 'claude-haiku-4-5-20251001',
    'gemini-1.5-pro': 'claude-sonnet-4-20250514',
}
```

### New `_claude_completion()` Method
- Full Anthropic SDK integration via `anthropic.Anthropic(api_key=...)`
- JSON mode: Injects instruction `"IMPORTANT: You MUST respond with ONLY valid JSON..."` into system prompt when `response_format={"type": "json_object"}`
- Extended thinking: When `thinking_budget >= 1024`, passes `{'type': 'enabled', 'budget_tokens': thinking_budget}` and omits `temperature`
- Markdown code fence stripping for JSON responses
- Vision format conversion from OpenAI `image_url` to Anthropic `source` format
- Message order enforcement: `_ensure_valid_claude_message_order()` ensures alternating user/assistant pattern

### New `chat_completion()` Parameter
```python
def chat_completion(self, messages, temperature=0.7, max_tokens=1000,
                    response_format=None, thinking_budget=0):
    # thinking_budget: enables Claude extended thinking when >= 1024
```

---

## 3. Copy Overlay Feature

### Overview
A complete full-stack feature that allows users to add professional marketing copy text on top of generated brand images. Located in the Overflow page's Media step (Step 4).

### Data Flow
```
Image generated in Media step
  → User clicks "Add Copy" button under image
  → CopyOverlayModal opens
  → Auto-calls POST /copy-overlay/generate-text/ (Claude generates 5 suggestions)
  → User picks a suggestion or types custom text
  → User adjusts styling (CSS preview updates instantly)
  → User clicks "Apply Overlay"
  → POST /assets/{asset_id}/copy-overlay/ (Pillow renders text on image)
  → New image URL returned, saved to copy_overlay_image field
  → Image in media accordion updates with overlaid version
```

### Backend: `ai_image/services/copy_overlay_service.py` (NEW)
Pillow-based text rendering engine with these capabilities:
- **4 layout modes:** `center`, `bottom_banner`, `top_banner`, `top_bottom_split`
- **5 fonts:** Montserrat Bold, Montserrat Regular, Playfair Display Bold, Roboto Bold, Bebas Neue
- **Auto font-sizing:** Base = `image_width // 15`, with min/max bounds
- **Semi-transparent background strips** behind text for readability
- **Text shadow** at (2,2) offset in RGBA(0,0,0,128)
- **Word wrapping** via pixel-width measurement
- **2x supersampling + LANCZOS downscale** for smooth anti-aliased text

### Backend: `ai_image/services/copy_generation_service.py` (NEW)
Uses Claude to generate short marketing copy suggestions for image overlay.

### Font Files Added: `ai_image/fonts/`
- `Montserrat-Bold.ttf` — Modern sans-serif headlines
- `Montserrat-Regular.ttf` — Clean body text
- `PlayfairDisplay-Bold.ttf` — Premium/luxury serif
- `Roboto-Bold.ttf` — Neutral/tech sans-serif
- `BebasNeue-Regular.ttf` — Impact display headlines

### Frontend: `CopyOverlayModal.tsx` (NEW, ~591 lines)
Two-step workflow in a full-screen modal:
- **Step 1 — Copy Text:** AI Suggestions tab (5 cards with style badges) or Custom Text textarea
- **Step 2 — Design Style:** Generate AI Styles button (2x2 grid of 4 variants) or manual controls (position, font, color, opacity, alignment, shadow)
- **Live CSS preview** on the left panel shows text on image in real-time
- **Apply** calls backend Pillow renderer, updates parent state

### API Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/copy-overlay/generate-text/` | POST | Generate 5 AI copy suggestions |
| `/api/v1/assets/<id>/copy-overlay/` | POST | Render text overlay on image via Pillow |
| `/api/v1/assets/<id>/copy-overlay/ai-styles/` | POST | Generate 4 AI typography style variants with base64 previews |

---

## 4. AI Typography Styles

### Overview
After selecting copy text, users can click "Generate AI Styles" to have Claude design 4 visually distinct typography configurations. Each variant is rendered server-side via Pillow and returned as a base64 data URL preview.

### Backend: `GenerateAIStylesView` in `api/creative_views.py`
1. Calls `generate_ai_styles()` — Claude designs 4 style configs (font, color, position, opacity, alignment, shadow)
2. Each config is rendered via `render_copy_overlay()` using Pillow
3. Results returned as base64 data URLs (no disk save until user selects one)

### Style Config Shape
```json
{
  "name": "Bold Impact",
  "description": "High contrast white on dark strip",
  "font_style": "bebas_neue",
  "text_color": "#FFFFFF",
  "position": "bottom_banner",
  "overlay_opacity": 70,
  "text_alignment": "center",
  "add_text_shadow": true
}
```

---

## 5. 9-Layer Prompt Engineering System

### Overview
A new service (`ai_image/services/prompt_engineering_service.py`) that uses Claude to generate structured, high-quality image generation prompts for DALL-E and Imagen. It includes failure diagnosis and re-prompting capabilities.

### 9-Layer Prompt Architecture
Every generated prompt follows this structure (written as a single flowing paragraph):
1. **FORMAT & PLATFORM** — Image format, dimensions, platform context
2. **SUBJECT & SCENE** — Primary subject in vivid, specific detail
3. **ART STYLE & AESTHETIC** — Visual style and artistic approach
4. **COLOR & PALETTE** — Color palette with descriptive names and hex codes
5. **COMPOSITION & LAYOUT** — Spatial arrangement, focal points, camera angle
6. **LIGHTING & ATMOSPHERE** — Lighting direction, quality, temperature, mood
7. **TEXTURES & MATERIALS** — Surface qualities and tactile details
8. **BRAND CONSISTENCY ANCHOR** — Brand style tag for consistency
9. **NEGATIVE PROMPT / EXCLUSIONS** — What to avoid

### Failure Taxonomy (22 codes across 8 categories)
| Category | Codes | Examples |
|---|---|---|
| Color | C1, C2, C3 | Wrong colors, dull, over-saturated |
| Style | S1, S2 | Mismatch, generic stock |
| Layout | L1, L2, L3, L4 | Cluttered, no safe zone, subject small, wrong angle |
| Artifact | A1, A2, A3 | Distortion, unwanted text, extra objects |
| Mood | M1, M2 | Wrong tone, flat impact |
| Background | B1, B2 | Busy, wrong setting |
| Texture | T1, T2 | Plastic look, wrong materials |
| Prompt | P1, P2 | Instruction ignored, intent altered |

### API Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/prompt-engineer/generate/` | POST | Generate 9-layer optimized image prompt |
| `/api/v1/prompt-engineer/diagnose/` | POST | Diagnose why a generated image failed |
| `/api/v1/prompt-engineer/reprompt/` | POST | Generate corrected prompt with targeted patches |

### Frontend Components
- `PromptPreviewPanel.tsx` — Inline panel previewing engineered prompts before generation
- `ImageDiagnosisModal.tsx` — Modal for AI-powered image failure diagnosis
- `RepromptPanel.tsx` — Panel for regenerating images using corrected prompts

---

## 6. Trending Service Rewrite

### What Changed
`api/trending_service.py` was completely rewritten from an LLM-only trend generation approach with static seasonal context tables to a **real Google Trends first approach** using `pytrends`.

### Before (v1.2.1)
- **Data source:** LLM imagination + static seasonal tables
- **Seasonal context:** Hardcoded `_get_seasonal_context()` and `_format_seasonal_context()` helper functions (~150 lines) containing Islamic calendar events, regional holidays, and seasonal event tables
- **Google Trends usage:** Minimal, used as supplementary context
- **System prompt focus:** "Identifies timely, relevant content opportunities"

### After (v1.2.2)
- **Data source:** 3-layer live Google Trends data via `pytrends` library
- **Seasonal context:** Removed all static tables; replaced by live daily trending data
- **Google Trends usage:** Primary data source with 3 query types:
  1. `pytrend.trending_searches(pn=region)` — Up to 20 daily trending searches
  2. `pytrend.related_queries()` — Rising + top queries for brand keywords (batches of 5, up to 15 keywords)
  3. `_build_seasonal_keywords()` — Month-based and industry-based seasonal keyword queries
- **New context sections:** `<brand_dna>`, `<content_pillars>`, `<competitor_insights>`, `<google_trends_data>` tags
- **System prompt focus:** "You receive REAL Google Trends data and must identify the most relevant trending opportunities"

### Deleted Functions
- `_get_seasonal_context()` — All hardcoded Islamic/regional holiday tables (~100 lines)
- `_format_seasonal_context()` — Seasonal text formatter (~50 lines)

### New Functions
- `_build_seasonal_keywords()` — Generates month-based + industry-based seasonal search terms (~40 lines)
- `_fetch_daily_trending()` — Fetches real-time daily trending searches from Google Trends
- `_fetch_related_queries()` — Fetches rising and top queries related to brand keywords

---

## 7. Extended Thinking (`think_harder`) Support

### What Changed
A `think_harder=False` parameter was added to 6 AI services. When `True`:
1. Increases `max_tokens` (roughly 2x)
2. Passes `thinking_budget=10000` to `chat_completion()`
3. For Claude: enables extended thinking with 10,000-token budget; `temperature` automatically omitted
4. For OpenAI/Gemini: `thinking_budget` ignored; only increased `max_tokens` applies

### Affected Services

| Service | Method | Before max_tokens | After (normal) | After (think_harder) |
|---|---|---|---|---|
| `openai_service.py` | `generate_from_text()` | 500 | 800 | 1500 + thinking |
| `openai_service.py` | `generate_from_image()` | 800 | 800 | 1500 + thinking |
| `openai_service.py` | `generate_from_video()` | 800 | 800 | 1500 + thinking |
| `openai_service.py` | `regenerate_with_feedback()` | 500 | 500 | 1500 + thinking |
| `openai_service.py` | `generate_multiple_variations()` | 1000 | 1000 | 2000 + thinking |
| `adaptation_service.py` | `adapt_caption()` | 1000 | 1500 | 2000 + thinking |
| `alt_text_service.py` | `generate_alt_text()` | 100 | 150 | 300 + thinking |
| `hashtag_service.py` | `generate_hashtags()` | 1000 | 1500 | 2000 + thinking |
| `trending_service.py` | `generate_trending_for_brand()` | 2500 | 2500 | 5000 + thinking |
| `prompt_engineering_service.py` | `generate_image_prompt()` | N/A (new) | 2000 | 4000 + thinking |
| `prompt_engineering_service.py` | `reprompt_image()` | N/A (new) | 2000 | 4000 + thinking |
| `prompt_engineering_service.py` | `diagnose_failure()` | N/A (new) | 500 | 1000 + thinking |

---

## 8. All Prompt Changes (Before vs After)

### 8.1 LLM Service — Claude Default Provider

**Before:** No Claude support. OpenAI was default.
**After:** Claude is default. New `_claude_completion()` method with JSON mode instruction:
```
IMPORTANT: You MUST respond with ONLY valid JSON. No markdown code fences, no explanatory
text, no comments. Start your response with { or [ and end with } or ].
```

---

### 8.2 Trending Service — System Prompt

**BEFORE (v1.2.1):**
```
You are a real-time social media trend analyst who identifies timely, relevant content
opportunities at the intersection of cultural moments and brand relevance.

Your trending topics are not generic industry keywords — they are specific, timely
conversation hooks that a content creator can act on THIS WEEK.

You prioritize:
- Specificity over breadth ("Ramadan marketing for SaaS" over "Ramadan")
- Timeliness — topics that are peaking or about to peak
- Brand relevance — every topic must connect to the brand's audience
- Actionability — each topic should clearly suggest content to create

Return ONLY valid JSON — no markdown, no commentary.
```

**AFTER (v1.2.2):**
```
You are a real-time social media trend analyst. You receive REAL Google Trends data and
must identify the most relevant trending opportunities for a specific brand.

Your job:
1. Analyze the real-time Google Trends data provided
2. Cross-reference with the brand's products, audience, and niche
3. Pick trends that the brand can actually create content about
4. Add brand-specific context to make each topic actionable

You prioritize:
- REAL data from Google Trends over guessing
- Brand-specific relevance — every topic must connect to what the brand sells
- Timeliness — topics that are trending RIGHT NOW
- Actionability — each topic should clearly suggest content to create

Return ONLY valid JSON — no markdown, no commentary.
```

**Key difference:** Changed from "identifies timely content opportunities" (LLM imagination) to "receives REAL Google Trends data" (data-driven analysis).

---

### 8.3 Trending Service — User Prompt `<data_sources>` Section

**BEFORE (v1.2.1):**
```xml
<data_sources>
Seasonal/cultural context: {seasonal_text}
Google Trends data: {trend_list}
</data_sources>
```
Where `seasonal_text` was generated from hardcoded tables like:
- Islamic calendar events (Ramadan, Eid ul-Fitr, Eid ul-Adha, etc.)
- Regional holidays (Independence Day, Victory Day, etc.)
- Seasonal events (Summer sale, Winter collection, etc.)

**AFTER (v1.2.2):**
```xml
<brand_dna>
{dna_summary or 'No Brand DNA available — use industry and brand name to infer.'}
</brand_dna>

<content_pillars>
{pillar_names list or 'No content pillars defined.'}
</content_pillars>

<competitor_insights>
{insight_texts list or 'No competitor data.'}
</competitor_insights>

<google_trends_data>
DAILY TRENDING SEARCHES ({region} — real-time):
{daily_trending[:20]}

RISING QUERIES (related to brand keywords — gaining momentum):
{rising_queries[:20]}

TOP QUERIES (most searched related to brand keywords):
{top_queries[:15]}
</google_trends_data>
```

**Key difference:** Removed static seasonal tables. Added live `<google_trends_data>` with 3 data types, plus `<brand_dna>`, `<content_pillars>`, and `<competitor_insights>` sections for brand context.

---

### 8.4 Trending Service — Instructions Section

**BEFORE (v1.2.1):**
```
1. Cross-reference the date, region, industry, seasonal events, and Google Trends.
2. Generate exactly 15 trending topics relevant to "{brand_name}".
3. Include AT LEAST 4-5 topics tied to current seasonal or cultural events in {region}.
```

**AFTER (v1.2.2):**
```
1. Study the brand DNA to understand what "{brand_name}" sells and who its audience is.
2. From the REAL Google Trends data above, identify topics relevant to this brand.
3. For topics from Google Trends, adapt them to the brand's niche (e.g., if "Eid" is
   trending and the brand sells dresses → "Eid dress collection trends").
4. You may also add 2-3 topics based on your knowledge of current events if they are
   highly relevant to the brand, even if not in the Google data.
```

**Key difference:** Changed from "include 4-5 seasonal/cultural" to "adapt trends to brand's niche" + "you may add 2-3 from your knowledge."

---

### 8.5 Trending Service — Constraints Section

**BEFORE (v1.2.1):**
```
- At least 4-5 seasonal/cultural.
- Volume scores should be realistic — not all 85+.
```

**AFTER (v1.2.2):**
```
- Prefer topics backed by REAL Google Trends data.
- Volume scores should reflect actual search volume — higher for daily trending, lower for niche.
- Every topic MUST directly relate to the brand's products, services, or audience.
```

---

### 8.6 Copy Generation — System Prompt (NEW in v1.2.2)

```
You are a senior copywriter specializing in social media graphics and brand imagery.
Generate short, punchy text overlays for brand images. These are NOT social media
captions — they are SHORT headline text that will be overlaid directly on the image,
like a professional graphic designer would create.

Rules:
- Maximum 8 words per line, maximum 2 lines total
- Each suggestion should have a distinctly different tone
- The text must be impactful and readable when overlaid on an image
- Consider the brand voice and industry context
- Return ONLY valid JSON, no markdown or extra text
```

### 8.7 Copy Generation — User Prompt (NEW in v1.2.2)

```
Generate {count} text overlay suggestions for a brand image.

<brand_context>
Brand: {brand_name}
Industry: {industry}
Target Audience: {target_audience}
Brand Voice: {voice_tone}
</brand_context>

<image_context>
Caption: {caption_text[:300]}
Image Description: {image_description[:200]}
CTA: {cta_text}
</image_context>

Return JSON in this exact format:
{"suggestions": [
  {"text": "Your Bold Headline Here", "style": "bold", "recommended_layout": "center"},
  ...
]}

Each suggestion must use a different style from: bold, inspirational, question, cta, minimal
Each must use a recommended_layout from: center, bottom_banner, top_banner
```

---

### 8.8 AI Style Generation — System Prompt (NEW in v1.2.2)

```
You are a senior graphic designer specializing in social media brand imagery and typography.
Given a copy text and brand context, generate distinct professional typography style
configurations. Each style should look completely different — vary the font, color palette,
position, background opacity, and alignment.
Think like a designer creating mood boards with different aesthetic directions.

Return ONLY valid JSON, no markdown.
```

### 8.9 AI Style Generation — User Prompt (NEW in v1.2.2)

```
Create {count} distinct typography styles for this copy text overlay on a brand image:

Copy text: "{copy_text}"
Brand: {brand_name}
Industry: {industry}

Return JSON:
{"styles": [
  {
    "name": "Bold Impact",
    "description": "High contrast white on dark strip",
    "font_style": "bebas_neue",
    "text_color": "#FFFFFF",
    "position": "bottom_banner",
    "overlay_opacity": 70,
    "text_alignment": "center",
    "add_text_shadow": true
  },
  ...
]}

Available font_style: montserrat_bold, montserrat_regular, playfair_bold, roboto_bold, bebas_neue
Available position: center, bottom_banner, top_banner, top_bottom_split
Available text_alignment: left, center, right
overlay_opacity: 0-100
text_color: any hex color

Make each style VERY different — mix elegant serif with bold sans-serif, light vs dark text,
minimal vs heavy backgrounds, centered vs left-aligned. Think: luxury, urban, minimalist,
editorial, etc.
```

---

### 8.10 Prompt Engineering — System Prompt (NEW in v1.2.2)

```
You are an expert AI Image Prompt Engineer specializing in generating high-quality,
brand-consistent image prompts for OpenAI's DALL-E and Google's Imagen image generation APIs.

PROMPT ARCHITECTURE — Every prompt you produce MUST follow this 9-layer structure,
written as a single flowing paragraph:

LAYER 1 — FORMAT & PLATFORM
LAYER 2 — SUBJECT & SCENE
LAYER 3 — ART STYLE & AESTHETIC
LAYER 4 — COLOR & PALETTE
LAYER 5 — COMPOSITION & LAYOUT
LAYER 6 — LIGHTING & ATMOSPHERE
LAYER 7 — TEXTURES & MATERIALS
LAYER 8 — BRAND CONSISTENCY ANCHOR
LAYER 9 — NEGATIVE PROMPT / EXCLUSIONS

RULES:
- NEVER generate vague or generic prompts
- ALWAYS write prompts as a single natural-language paragraph
- ALWAYS prioritize brand consistency
- ALWAYS consider the "thumb-stop test"
- ALWAYS include negative exclusions
- AVOID prompt cliches like "stunning", "beautiful", "amazing"
- AVOID requesting readable text in images
- For product images, describe physical attributes in detail
```

### 8.11 Re-Prompt Engineering — System Prompt (NEW in v1.2.2)

```
You are an expert AI Image Prompt Engineer specializing in diagnosing and fixing failed
image generation prompts.

FAILURE TAXONOMY — Use these codes to classify problems:
C1: COLOR_WRONG, C2: COLOR_DULL, C3: COLOR_OVER
S1: STYLE_MISMATCH, S2: STYLE_GENERIC
L1: LAYOUT_CLUTTERED, L2: LAYOUT_NO_SAFE_ZONE, L3: LAYOUT_SUBJECT_SMALL, L4: LAYOUT_WRONG_ANGLE
A1: ARTIFACT_DISTORTION, A2: ARTIFACT_TEXT, A3: ARTIFACT_EXTRA_OBJECTS
M1: MOOD_WRONG, M2: MOOD_FLAT
B1: BACKGROUND_BUSY, B2: BACKGROUND_WRONG
T1: TEXTURE_PLASTIC, T2: TEXTURE_WRONG
P1: PROMPT_IGNORED, P2: PROMPT_REWRITTEN

RE-PROMPT RULES:
- NEVER rewrite the entire prompt. PATCH it.
- Apply targeted correction patches at the END of the prompt.
- Maximum 2 patches per re-prompt attempt.
- Maximum 3 total attempts before redesigning.
```

### 8.12 Brand Style Anchor Generator — System Prompt (NEW in v1.2.2)

```
You are a brand visual identity specialist. Generate a compact 1-2 sentence Brand Style
Anchor — a reusable visual DNA summary for image generation prompts. Format: [BrandName
Brand Style: style, palette, textures, lighting, mood, motif.] Respond with ONLY the
anchor text, nothing else.
```

---

### 8.13 Caption Generation — System Prompt (UNCHANGED)

The system prompt in `ai_caption/openai_service.py` was NOT changed. It remains the same comprehensive prompt with:
- `<role>` — Elite social media content creator
- `<writing_philosophy>` — Hook first, authentic voice, emotional resonance, value density, platform intelligence
- `<engagement_techniques>` — Open loops, specificity, pattern interrupts, power words, micro-stories
- `<anti_patterns>` — 11 banned AI-sounding phrases

**What changed:** Only `max_tokens` and `thinking_budget` parameters (see Section 7).

---

### 8.14 Caption Adaptation — System Prompt (UNCHANGED)

The system prompt in `ai_caption/services/adaptation_service.py` was NOT changed. It remains the platform-native adaptation prompt covering Twitter/X, LinkedIn, Facebook, Instagram, TikTok.

**What changed:** Only `max_tokens` and `thinking_budget` parameters (see Section 7).

---

### 8.15 Alt Text Generation — System Prompt (UNCHANGED)

The system prompt in `ai_image/services/alt_text_service.py` was NOT changed. It remains the WCAG 2.1 accessibility specialist prompt.

**What changed:** Only `max_tokens` and `thinking_budget` parameters (see Section 7).

---

### 8.16 Hashtag Generation — System Prompt (UNCHANGED)

The system prompt in `posts/services/hashtag_service.py` was NOT changed. It remains the 3-tier volume distribution strategy prompt.

**What changed:** Only `max_tokens` and `thinking_budget` parameters (see Section 7).

---

## 9. Database & Model Changes

### `ImageGeneration` Model — 7 New Fields

#### Copy Overlay Fields (Migration 0006)
```python
copy_overlay_image = models.ImageField(
    upload_to=generated_image_path, blank=True, null=True,
    help_text="Image with copy text overlay applied"
)
copy_overlay_text = models.CharField(
    max_length=200, blank=True, default='',
    help_text="The copy text overlaid on the image"
)
copy_overlay_settings = models.JSONField(
    blank=True, null=True,
    help_text="Overlay styling settings (position, font, color, etc.)"
)
```

#### Prompt Engineering Metadata Fields (Migration 0005)
```python
brand_style_anchor = models.TextField(blank=True, null=True,
    help_text="Reusable brand visual DNA summary")
prompt_engineering_used = models.BooleanField(default=False,
    help_text="Whether 9-layer prompt engineering was applied")
failure_codes = models.JSONField(blank=True, null=True,
    help_text="Failure taxonomy codes e.g. ['C1','L2']")
reprompt_attempt = models.IntegerField(default=0,
    help_text="Re-prompt attempt number (max 3)")
```

### Updated `get_display_image()` Priority
```python
# BEFORE:
def get_display_image(self):
    if self.composited_image:
        return self.composited_image
    if self.generated_image_with_logo:
        return self.generated_image_with_logo
    return self.generated_image

# AFTER:
def get_display_image(self):
    if self.copy_overlay_image:        # NEW — highest priority
        return self.copy_overlay_image
    if self.composited_image:
        return self.composited_image
    if self.generated_image_with_logo:
        return self.generated_image_with_logo
    return self.generated_image
```

### `VideoGeneration` Model — 1 New Field (Migration ai_video/0002)
```python
reference_image = models.ImageField(
    upload_to='video_references/%Y/%m/', blank=True, null=True,
    help_text="Product photo used as reference for video generation"
)
```

---

## 10. API Endpoint Changes

### New Serializers (5)

| Serializer | Fields | Purpose |
|---|---|---|
| `PromptEngineerGenerateSerializer` | brand_id, subject, platform, mood, key_message, must_include, must_exclude, text_overlay_position | Generate 9-layer image prompt |
| `PromptEngineerDiagnoseSerializer` | image_description, original_prompt, revised_prompt | Diagnose image failure |
| `PromptEngineerRepromptSerializer` | brand_id, original_prompt, failure_description, attempt_number | Re-prompt with patches |
| `CopyOverlayGenerateSerializer` | brand_id, caption_text, image_description, cta_text, count | Generate copy suggestions |
| `CopyOverlayApplySerializer` | copy_text, position, font_style, text_color, overlay_opacity, font_size, text_alignment, add_text_shadow | Render text overlay |

### New URL Patterns (6)

```python
# Prompt Engineering
path('prompt-engineer/generate/',   PromptEngineerGenerateView.as_view())
path('prompt-engineer/diagnose/',   PromptEngineerDiagnoseView.as_view())
path('prompt-engineer/reprompt/',   PromptEngineerRepromptView.as_view())

# Copy Overlay
path('copy-overlay/generate-text/',                    GenerateCopyOverlayTextView.as_view())
path('assets/<int:asset_id>/copy-overlay/',            ApplyCopyOverlayView.as_view())
path('assets/<int:asset_id>/copy-overlay/ai-styles/',  GenerateAIStylesView.as_view())
```

### New Views (6)

| View | Method | Description |
|---|---|---|
| `PromptEngineerGenerateView` | POST | Generate 9-layer optimized image prompt |
| `PromptEngineerDiagnoseView` | POST | Diagnose failed image using failure taxonomy |
| `PromptEngineerRepromptView` | POST | Generate corrected prompt with targeted patches |
| `GenerateCopyOverlayTextView` | POST | Generate 5 AI copy text suggestions |
| `ApplyCopyOverlayView` | POST | Render Pillow text overlay, save to model |
| `GenerateAIStylesView` | POST | Generate 4 AI typography variants with base64 previews |

---

## 11. Frontend Changes

### New Components (4)

| Component | File | Description |
|---|---|---|
| `CopyOverlayModal` | `components/ai-image/CopyOverlayModal.tsx` | Full copy overlay workflow (2-step: copy text → design style) |
| `ImageDiagnosisModal` | `components/ai-image/ImageDiagnosisModal.tsx` | AI-powered image failure diagnosis modal |
| `PromptPreviewPanel` | `components/ai-image/PromptPreviewPanel.tsx` | Inline panel previewing engineered prompts |
| `RepromptPanel` | `components/ai-image/RepromptPanel.tsx` | Panel for corrected prompt regeneration |

### New Pages (1)

| Page | Route | Description |
|---|---|---|
| `APITestPage` | `/test-api` | Developer tool to verify Claude API connectivity |

### New Type Files (2)

| File | Types Defined |
|---|---|
| `types/copyOverlay.ts` | CopySuggestion, CopyOverlayGenerateRequest/Response, CopyOverlayApplyRequest/Response, AIStyleVariant, AIStylesRequest/Response, OverlayPosition, FontStyle, TextAlignment |
| `types/promptEngineering.ts` | FailureCode (22 codes), FAILURE_TAXONOMY, getFailureCodeColor(), PromptEngineerGenerate/Diagnose/Reprompt Request/Response |

### Modified Services

**`imageService.ts`** — 6 new methods:
- `generateEngineeredPrompt()` — POST `/prompt-engineer/generate/`
- `diagnoseImage()` — POST `/prompt-engineer/diagnose/`
- `repromptImage()` — POST `/prompt-engineer/reprompt/`
- `generateCopySuggestions()` — POST `/copy-overlay/generate-text/`
- `applyCopyOverlay()` — POST `/assets/{id}/copy-overlay/`
- `generateAIStyles()` — POST `/assets/{id}/copy-overlay/ai-styles/`

**`videoService.ts`** — Added `reference_image?: File` to `GenerateVideoRequest`

### Modified Pages

**`OverflowPage.tsx`:**
- Added `copyOverlayOpen` state (caption ID or null)
- Added "Add Copy" button (purple) in single-provider and dual-provider result sections
- Added `<CopyOverlayModal>` rendering with `onOverlayApplied` callback

**`AIImagePage.tsx`:**
- Integrated `PromptPreviewPanel`, `ImageDiagnosisModal`, `RepromptPanel`
- Added diagnosis/reprompt state management

**`App.tsx`:** Added `/test-api` route for `APITestPage`
**`pages/index.ts`:** Added `APITestPage` export
**`types/index.ts`:** Added 4 prompt engineering fields to `ImageGeneration` interface

### Footer Update
**`components/layout/Footer.tsx`:** Version string updated to `"All systems operational · v1.2.2"`

---

## 12. Complete File Inventory

### New Files
| # | File | Lines | Purpose |
|---|---|---|---|
| 1 | `ai_image/fonts/Montserrat-Bold.ttf` | binary | Font file |
| 2 | `ai_image/fonts/Montserrat-Regular.ttf` | binary | Font file |
| 3 | `ai_image/fonts/PlayfairDisplay-Bold.ttf` | binary | Font file |
| 4 | `ai_image/fonts/Roboto-Bold.ttf` | binary | Font file |
| 5 | `ai_image/fonts/BebasNeue-Regular.ttf` | binary | Font file |
| 6 | `ai_image/services/copy_overlay_service.py` | ~287 | Pillow text rendering engine |
| 7 | `ai_image/services/copy_generation_service.py` | ~226 | Claude copy + style generation |
| 8 | `ai_image/migrations/0005_add_prompt_engineering_fields.py` | ~28 | 4 new fields migration |
| 9 | `ai_image/migrations/0006_add_copy_overlay_fields.py` | ~28 | 3 new fields migration |
| 10 | `ai_video/migrations/0002_add_reference_image.py` | ~18 | Reference image migration |
| 11 | `frontend/src/types/copyOverlay.ts` | ~63 | Copy overlay TypeScript types |
| 12 | `frontend/src/types/promptEngineering.ts` | ~120 | Prompt engineering TypeScript types |
| 13 | `frontend/src/components/ai-image/CopyOverlayModal.tsx` | ~591 | Copy overlay modal component |
| 14 | `frontend/src/components/ai-image/ImageDiagnosisModal.tsx` | ~200 | Image diagnosis modal |
| 15 | `frontend/src/components/ai-image/PromptPreviewPanel.tsx` | ~150 | Prompt preview panel |
| 16 | `frontend/src/components/ai-image/RepromptPanel.tsx` | ~180 | Reprompt panel |
| 17 | `frontend/src/pages/APITestPage.tsx` | ~80 | Claude API test page |

### Modified Files
| # | File | Changes |
|---|---|---|
| 1 | `accounts/services/llm_service.py` | Claude provider, 3-provider fallback, extended thinking, vision format |
| 2 | `ai_caption/openai_service.py` | think_harder parameter on all 5 methods |
| 3 | `ai_caption/services/adaptation_service.py` | think_harder parameter |
| 4 | `ai_image/models.py` | 7 new fields + get_display_image() update |
| 5 | `ai_image/services/alt_text_service.py` | think_harder parameter |
| 6 | `ai_image/services/prompt_engineering_service.py` | 9-layer system (new service, existed in branch) |
| 7 | `api/serializers.py` | 5 new serializers + updated ImageGenerationSerializer fields |
| 8 | `api/creative_views.py` | 6 new views (3 prompt engineer + 3 copy overlay) |
| 9 | `api/urls.py` | 6 new URL patterns |
| 10 | `api/views.py` | Updated LLM service imports |
| 11 | `api/trending_service.py` | Complete rewrite with Google Trends |
| 12 | `posts/services/hashtag_service.py` | think_harder parameter |
| 13 | `frontend/src/App.tsx` | /test-api route |
| 14 | `frontend/src/pages/AIImagePage.tsx` | Prompt engineering integration |
| 15 | `frontend/src/pages/OverflowPage.tsx` | Copy overlay integration |
| 16 | `frontend/src/pages/index.ts` | APITestPage export |
| 17 | `frontend/src/services/imageService.ts` | 6 new API methods |
| 18 | `frontend/src/services/videoService.ts` | reference_image field |
| 19 | `frontend/src/types/index.ts` | 4 prompt engineering fields |
| 20 | `frontend/src/components/layout/Footer.tsx` | v1.2.2 version string |

---

*Document generated: March 8, 2026*
*Version: SocialSync v1.2.2*
*Branch: v1-2-2/claudeAPI-setup*
