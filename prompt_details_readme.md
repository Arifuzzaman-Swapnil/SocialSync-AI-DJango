# SocialSync - AI Prompt Details

> A comprehensive reference of every AI/LLM prompt used in the SocialSync project.
> Total prompts documented: **33**

---

## Table of Contents

| #  | Prompt Name                          | AI Model       | File                                    |
|----|--------------------------------------|----------------|-----------------------------------------|
| 1  | Caption Generation (Post)            | GPT-4o-mini    | api/caption_views.py                    |
| 2  | Caption Adaptation                   | GPT-4o-mini    | ai_caption/services/adaptation_service.py |
| 3  | AI Caption from Text (System)        | GPT-4o         | ai_caption/openai_service.py            |
| 4  | AI Caption from Text (User)          | GPT-4o         | ai_caption/openai_service.py            |
| 5  | Image Analysis                       | GPT-4o Vision  | ai_caption/openai_service.py            |
| 6  | Caption from Image                   | GPT-4o Vision  | ai_caption/openai_service.py            |
| 7  | Caption from Video                   | GPT-4o Vision  | ai_caption/openai_service.py            |
| 8  | Caption Regeneration with Feedback   | GPT-4o         | ai_caption/openai_service.py            |
| 9  | Multiple Caption Variations          | GPT-4o         | ai_caption/openai_service.py            |
| 10 | Competitor Analysis (Crawl)          | GPT-4o-mini    | api/strategy_views.py                   |
| 11 | Content Idea Generation              | GPT-4o-mini    | api/strategy_views.py                   |
| 12 | Idea Regeneration                    | GPT-4o-mini    | api/strategy_views.py                   |
| 13 | Competitor Suggestion                | GPT-4o-mini    | api/strategy_views.py                   |
| 14 | Content Pillar Generation            | GPT-4o-mini    | api/strategy_views.py                   |
| 15 | Trending Topics Generation           | GPT-4o-mini    | api/trending_service.py                 |
| 16 | Brand DNA from Website               | GPT-4o-mini    | api/views.py                            |
| 17 | Brand DNA Enhancement (Website)      | GPT-4o-mini    | api/views.py                            |
| 18 | Brand DNA Enhancement (Input)        | GPT-4o-mini    | api/views.py                            |
| 19 | AI Comment Reply                     | GPT-4o-mini    | api/analytics_views.py                  |
| 20 | Optimal Posting Times                | GPT-4o-mini    | api/scheduling_views.py                 |
| 21 | Video Generation (Veo 2)             | Gemini Veo 2   | ai_video/gemini_service.py              |
| 22 | Overflow Page - Caption Prompt       | GPT-4o         | frontend/src/pages/OverflowPage.tsx     |
| 23 | Overflow Page - Image Prompt         | Gemini/DALL-E  | frontend/src/pages/OverflowPage.tsx     |
| 24 | Caption System Prompt (Shared)       | GPT-4o         | ai_caption/openai_service.py            |
| 25 | DALL-E 3 Image Generation            | DALL-E 3       | ai_image/openai_service.py              |
| 26 | Gemini Image Generation              | Gemini Flash   | ai_image/gemini_service.py              |
| 27 | Alt Text Generation                  | GPT-4o-mini    | ai_image/services/alt_text_service.py   |
| 28 | Hashtag Generation                   | GPT-4o-mini    | posts/services/hashtag_service.py       |
| 29 | Messenger AI Importance Detection    | GPT-4o-mini    | messenger_bot/services/message_handler.py |
| 30 | Messenger Image Description          | GPT-4o Vision  | messenger_bot/services/message_handler.py |
| 31 | Messenger Image Response (Context)   | GPT-4o (configurable) | messenger_bot/services/message_handler.py |
| 32 | RAG System Prompt (Messenger Bot)    | Configurable   | messenger_bot/services/rag_engine.py    |
| 33 | Product Scene Background Prompt      | DALL-E / Gemini | ai_image/product_compositor.py          |

---

## 1. Caption Generation (Post)

- **File Location:** D:/Projects/Final_version_socialSync/api/caption_views.py
- **Lines:** 98-116
- **API:** `POST /api/v1/drafts/{post_id}/captions/generate/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.8, max_tokens: 2000)
- **Goal:** Generate multiple unique social media caption variants for a draft post, each with a different hook, structure, or angle. Also generates DALL-E 3 image prompts for each caption.

**System Prompt:**
```
You are an expert social media copywriter. Return only valid JSON.
```

**User Prompt:**
```
Generate {count} unique social media caption variants.

Context:
{brand_context}{pillar_context}
Original text: {(post.caption or post.hook or 'No caption provided')[:500]}
{f'Hook/angle: {post.hook}' if post.hook else ''}
{f'Goal: {post.goal}' if post.goal else ''}
Tone: {tone}
{'Include a clear call-to-action in each variant.' if include_cta else ''}

Rules:
- Each variant must be meaningfully different (different hook, structure, or angle)
- Match the requested tone
- Make them engaging and platform-appropriate
- For each caption, also generate a concise image prompt for DALL-E 3 that would create a perfect visual to accompany the caption

Return JSON:
{{"captions": [{{"body": "...", "cta_text": "...", "image_prompt": "A concise DALL-E 3 image prompt..."}}]}}
```

---

## 2. Caption Adaptation

- **File Location:** D:/Projects/Final_version_socialSync/ai_caption/services/adaptation_service.py
- **Lines:** 54-73
- **API:** Called internally via `POST /api/v1/drafts/{post_id}/captions/adapt/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.7, max_tokens: 1000)
- **Goal:** Adapt an existing caption for a specific platform (Twitter: 280 chars, LinkedIn: 3000 chars, Facebook: 63206 chars, Instagram: 2200 chars) while keeping the core message intact and adjusting tone/length.

**System Prompt:**
```
You are a social media copywriter. Return only valid JSON.
```

**User Prompt:**
```
Adapt this caption for {target_platform}.

Original caption:
{source_caption.body}

Platform guidelines:
- Max characters: {guidelines['max_chars']}
- Tone: {guidelines['tone']}
- Notes: {guidelines['notes']}
{brand_context}

Rules:
- Keep the core message intact
- Adapt tone and length for the platform
- Stay within character limit
- If the original has a CTA, adapt it for the platform

Return JSON:
{{"adapted_body": "...", "cta_text": "..."}}
```

---

## 3. AI Caption from Text — System Prompt (Shared)

- **File Location:** D:/Projects/Final_version_socialSync/ai_caption/openai_service.py
- **Lines:** 57-89
- **API:** Used by `POST /api/v1/ai-caption/generate/` and all caption methods
- **AI Model:** OpenAI GPT-4o
- **Goal:** Define the AI's persona, writing style, platform guidelines, and output rules for all caption generation. This shared system prompt is used by prompts #4, #6, #7, #8, and #9.

**System Prompt:**
```
You are an expert social media content creator and copywriter with years of experience crafting viral, engaging content.

Your writing style is: {tone_descriptions.get(tone, 'Professional and engaging')}

{platform_guidelines}

Guidelines:
- Write authentic, human-sounding content (avoid AI-sounding phrases)
- Create scroll-stopping opening lines
- Use power words that trigger emotion
- {"Include relevant emojis naturally throughout the caption" if include_emojis else "Do NOT use any emojis"}
- {"Include a clear call-to-action at the end" if include_cta else "Do NOT include any call-to-action"}
- {"Include relevant hashtags (separated at the end)" if include_hashtags else "Do NOT include any hashtags"}

Output Format:
- Return ONLY the caption text
- If hashtags are requested, put them on a new line at the very end
- No explanations, no markdown formatting, no quotes around the text
```

**Tone Options:**
- professional: "Professional, polished, and authoritative"
- casual: "Relaxed, conversational, and approachable"
- friendly: "Warm, welcoming, and personable"
- enthusiastic: "Energetic, excited, and passionate"
- humorous: "Witty, playful, and entertaining"
- inspirational: "Motivating, uplifting, and empowering"
- formal: "Formal, sophisticated, and refined"
- conversational: "Natural, flowing, like talking to a friend"

**Platform Guidelines:**
- general: "Create a versatile caption suitable for any platform."
- facebook: "Optimize for Facebook: longer captions work well, include engaging questions..."
- instagram: "Optimize for Instagram: strong opening line, use line breaks..."
- twitter: "Optimize for Twitter/X: Keep it concise (under 280 characters ideally)..."
- linkedin: "Optimize for LinkedIn: Professional tone, industry insights..."
- tiktok: "Optimize for TikTok: Trendy, casual tone..."
- youtube: "Optimize for YouTube: SEO-friendly, include keywords..."
- pinterest: "Optimize for Pinterest: Descriptive, SEO-rich..."

---

## 4. AI Caption from Text — User Prompt

- **File Location:** D:/Projects/Final_version_socialSync/ai_caption/openai_service.py
- **Lines:** 121-126
- **API:** `POST /api/v1/ai-caption/generate/`
- **AI Model:** OpenAI GPT-4o (temperature: 0.8, max_tokens: 500)
- **Goal:** Generate a social media caption from a text topic with customizable tone, length, platform, hashtags, emojis, and CTA settings.

**User Prompt:**
```
Create a social media caption about: {topic}

Target length: {self._get_word_count(length)}
{f'Additional instructions: {custom_instructions}' if custom_instructions else ''}

Generate the caption now:
```

**Length Options:**
- short: "20-40 words"
- medium: "40-80 words"
- long: "80-120 words"
- extra_long: "120-200 words"

---

## 5. Image Analysis

- **File Location:** D:/Projects/Final_version_socialSync/ai_caption/openai_service.py
- **Lines:** 257-267
- **API:** Internal method `analyze_image()` — used within caption generation when media is uploaded
- **AI Model:** OpenAI GPT-4o Vision (max_tokens: 800)
- **Goal:** Analyze an uploaded image in detail to extract information for contextual caption generation.

**User Prompt:**
```
Analyze this image in detail. Describe:
1. Main subject/focus
2. Setting/background
3. Colors and mood
4. Any text visible
5. People (if any) - their actions, expressions
6. Objects and their arrangement
7. Overall theme/message
8. Potential use cases for social media

Be specific and detailed.
```

---

## 6. Caption from Image

- **File Location:** D:/Projects/Final_version_socialSync/ai_caption/openai_service.py
- **Lines:** 314-326
- **API:** `POST /api/v1/ai-caption/generate/` (with media_file image attachment)
- **AI Model:** OpenAI GPT-4o Vision (temperature: 0.8, max_tokens: 800)
- **Goal:** Analyze an uploaded image and create an engaging social media caption based on what the AI sees in the image.

**User Prompt:**
```
Analyze this image and create an engaging social media caption for it.

{f'Context provided: {additional_context}' if additional_context else ''}
{f'Additional instructions: {custom_instructions}' if custom_instructions else ''}

Target length: {self._get_word_count(length)}

First, briefly describe what you see in the image (2-3 sentences).
Then, create the caption.

Format your response as:
ANALYSIS: [your image analysis]
CAPTION: [the generated caption]
```

---

## 7. Caption from Video

- **File Location:** D:/Projects/Final_version_socialSync/ai_caption/openai_service.py
- **Lines:** 429-441
- **API:** `POST /api/v1/ai-caption/generate/` (with media_file video attachment)
- **AI Model:** OpenAI GPT-4o Vision with multiple frames (temperature: 0.8, max_tokens: 800)
- **Goal:** Extract frames from a video, analyze them to understand the video's story/action, and generate a caption based on the visual content.

**User Prompt:**
```
These are frames extracted from a video. Analyze them to understand the video content and create an engaging social media caption.

{f'Context provided: {additional_context}' if additional_context else ''}
{f'Additional instructions: {custom_instructions}' if custom_instructions else ''}

Target length: {self._get_word_count(length)}

First, describe what you see across these video frames (the story/action).
Then, create the caption.

Format your response as:
ANALYSIS: [your video analysis]
CAPTION: [the generated caption]
```

---

## 8. Caption Regeneration with Feedback

- **File Location:** D:/Projects/Final_version_socialSync/ai_caption/openai_service.py
- **Lines:** 530-537
- **API:** `POST /api/v1/ai-caption/regenerate/{id}/`
- **AI Model:** OpenAI GPT-4o (temperature: 0.8, max_tokens: 500)
- **Goal:** Regenerate a previously generated caption incorporating user feedback while maintaining quality.

**User Prompt:**
```
Here is a social media caption that was previously generated:

"{original_caption}"

The user wants changes based on this feedback: {feedback}

Please regenerate the caption incorporating this feedback while maintaining quality.
Return ONLY the new caption.
```

---

## 9. Multiple Caption Variations

- **File Location:** D:/Projects/Final_version_socialSync/ai_caption/openai_service.py
- **Lines:** 600-610
- **API:** Internal method `generate_multiple_variations()` — used within the caption service
- **AI Model:** OpenAI GPT-4o (temperature: 0.9, max_tokens: 1000)
- **Goal:** Generate multiple distinct caption variations at once, each with a unique angle, opening hook, and emotional appeal.

**User Prompt:**
```
Create {num_variations} DIFFERENT social media caption variations for: {topic_or_analysis}

Target length per caption: {self._get_word_count(length)}

Requirements:
- Each caption should have a unique angle/approach
- Vary the opening hooks
- Different emotional appeals
- Number each variation (1., 2., 3., etc.)

Generate {num_variations} distinct captions now:
```

---

## 10. Competitor Analysis (Crawl)

- **File Location:** D:/Projects/Final_version_socialSync/api/strategy_views.py
- **Lines:** 361-387
- **API:** `POST /api/v1/brands/{brand_id}/competitors/crawl/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.5, max_tokens: 4500)
- **Goal:** Crawl up to 8 pages from a competitor's website, then use AI to extract 10 specific competitive insights with actionable content strategies, each referencing a specific crawled page URL.

**System Prompt:**
```
You are a competitive intelligence analyst. Analyze the actual page content provided. Each insight must reference a specific page URL from the crawled pages. Return only valid JSON arrays.
```

**User Prompt:**
```
Analyze this competitor for my brand based on their ACTUAL page content.

MY BRAND:
- Name: "{brand.brand_name}"
- Industry: {brand.industry}
- Target Region: {brand.target_region}
- Content Pillars: {pillar_context}

COMPETITOR:
- URL/Handle: {profile.handle_or_url}
- Platform: {profile.get_platform_display()}
{page_context}

Based on the ACTUAL content from their site, provide 10 specific competitive insights.
Each insight MUST reference a specific page from the crawled URLs above.
Use DIFFERENT source_url values - pick the most relevant page URL for each insight.

For each insight provide:
- hook_text: A specific content strategy or post idea for MY brand to compete (max 200 chars)
- angle: Why this works based on what you see in their content (max 150 chars)
- format_type: Best format (text/image/video/carousel/reel/story)
- engagement_score: Effectiveness for MY brand (1-10)
- recommendation: Exact action step for "{brand.brand_name}" (max 200 chars)
- based_on: What specific part of their content inspired this insight (max 100 chars)
- source_url: The EXACT page URL from the list above that this insight is based on. MUST be one of the actual crawled URLs, not the base URL unless the insight is actually from the homepage.

Return as JSON array only.
```

---

## 11. Content Idea Generation

- **File Location:** D:/Projects/Final_version_socialSync/api/strategy_views.py
- **Lines:** 644-668
- **API:** `POST /api/v1/ideas/generate/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.85, max_tokens: 3000)
- **Goal:** Generate unique, actionable content ideas for social media inspired by trending topics, brand DNA, competitor insights, and learning signals. Each idea includes a title, hook, angle, platform recommendation, and engagement tier.

**System Prompt:**
```
You are a senior social media analyst and business development strategist. You analyze trending topics and create viral, high-converting content ideas that drive real business results — more followers, more engagement, more sales. Return only valid JSON arrays.
```

**User Prompt:**
```
I have a {brand.industry} brand/business called "{brand.brand_name}" in {brand.target_region}.

{dna_context}{competitor_context}{trending_context}{learning_context}
Content pillars: {pillar_context}
{f'Focus pillar: {specific_pillar.name}' if specific_pillar else ''}
Platform: {platform_text}

Based on the above context — especially the trending topics — generate exactly {count} unique, actionable content ideas that I can post on social media to increase my brand visibility, engagement, and sales.

Each idea must be:
- Directly inspired by one of the trending topics or current events
- Tailored to my brand, industry, and target audience
- Ready to execute — specific enough to write a caption from

For each idea, return:
- title: A catchy, scroll-stopping title (max 80 chars, NO generic text like "Idea 1")
- hook: An attention-grabbing opening line that makes people stop scrolling
- angle: The unique perspective, story, or approach
- platform: Best platform for this idea (twitter/linkedin/facebook/instagram)
- goal: Content goal (leads/growth/authority)
- content_format: Format type (text/image/video/carousel/reel/thread)
- pillar_name: Which content pillar this fits
- engagement_tier: Expected engagement (high/mid/low)

Return as JSON array. Only return the JSON array, no other text.
```

---

## 12. Idea Regeneration

- **File Location:** D:/Projects/Final_version_socialSync/api/strategy_views.py
- **Lines:** 797-814
- **API:** `POST /api/v1/ideas/{idea_id}/regenerate/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.9, max_tokens: 500)
- **Goal:** Regenerate a single content idea with a completely fresh hook and angle while keeping the same platform, goal, and format.

**System Prompt:**
```
You are an expert social media strategist. Return only valid JSON.
```

**User Prompt:**
```
Regenerate a single content idea with a fresh angle.

{brand_context}{pillar_context}

Original idea to improve:
- Title: {idea.title}
- Hook: {idea.hook}
- Angle: {idea.angle}
- Platform: {idea.platform}
- Goal: {idea.goal}
- Format: {idea.content_format}

{f'Additional instructions: {request.data.get("instructions", "")}' if request.data.get("instructions") else ''}

Create a completely new version with a different hook and angle, keeping the same platform, goal, and format.

Return JSON:
{{"title": "...", "hook": "...", "angle": "...", "goal": "...", "content_format": "...", "engagement_tier": "high|medium|low"}}
```

---

## 13. Competitor Suggestion

- **File Location:** D:/Projects/Final_version_socialSync/api/strategy_views.py
- **Lines:** 1140-1158
- **API:** `POST /api/v1/competitors/suggest/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.3, max_tokens: 1500)
- **Goal:** AI-suggest real competitor companies/brands based on brand DNA, industry, region, and target audience. Avoids duplicating already-added competitors.

**User Prompt:**
```
You are a competitive intelligence analyst. Suggest {count} real competitor companies/brands for this brand.

Brand: {brand.brand_name}
Industry: {brand.industry}
Region: {brand.target_region}
Target Audience: {dna.get('target_audience', 'general')}
Products/Services: {dna.get('products_services', 'N/A')}
Brand Values: {', '.join(dna.get('brand_values', [])) if dna.get('brand_values') else 'N/A'}

Existing competitors (DO NOT suggest these): {', '.join(existing) if existing else 'None'}

Return a JSON object:
{{"competitors": [{{"name": "Company Name", "platform": "website", "handle_or_url": "https://example.com", "reason": "Brief reason why they are a competitor"}}]}}

Rules:
- Suggest REAL companies that actually exist
- Include their actual website URL or social media handle
- Focus on direct and indirect competitors in the same region/market
- platform should be one of: website, twitter, linkedin, facebook, instagram
```

---

## 14. Content Pillar Generation

- **File Location:** D:/Projects/Final_version_socialSync/api/strategy_views.py
- **Lines:** 1226-1249
- **API:** `POST /api/v1/brands/{brand_id}/pillars/generate/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.5, max_tokens: 1500)
- **Goal:** AI-generate content strategy pillars for a brand based on brand DNA, competitor strategies, and trending topics. Each pillar includes a name, description, target percentage, and color code.

**User Prompt:**
```
You are a content strategy expert. Generate {count} content pillars for this brand.

Brand: {brand.brand_name}
Industry: {brand.industry}
Target Audience: {dna.get('target_audience', 'general')}
Brand Voice: {dna.get('brand_voice', 'professional')}
Brand Values: {', '.join(dna.get('brand_values', [])) if dna.get('brand_values') else 'N/A'}
Products/Services: {dna.get('products_services', 'N/A')}

Competitor Strategies: {'; '.join(insight_texts[:5]) if insight_texts else 'None analyzed yet'}
Current Trending Topics: {', '.join(trending_texts[:5]) if trending_texts else 'None'}

Existing pillars (DO NOT duplicate these): {', '.join(existing_pillars) if existing_pillars else 'None'}
{f'Focus areas to emphasize: {", ".join(focus_areas)}' if focus_areas else ''}

Return a JSON object:
{{"pillars": [{{"name": "Pillar Name", "description": "1-2 sentence description", "target_percentage": 20, "color_code": "#hex"}}]}}

Rules:
- Percentages must sum to exactly 100
- Each pillar should be distinct and actionable
- Use vibrant, distinct hex color codes for each pillar
- Name should be concise (2-4 words)
- Description should explain what content falls under this pillar
```

---

## 15. Trending Topics Generation

- **File Location:** D:/Projects/Final_version_socialSync/api/trending_service.py
- **Lines:** 293-323
- **API:** `POST /api/v1/brands/{brand_id}/trending/generate/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.7, max_tokens: 2500)
- **Goal:** Generate the top 15 most relevant trending topics for a brand's content strategy based on Brand DNA, content pillars, competitor strategies, current seasonal/cultural events, Google Trends data, and user feedback (accepted/rejected topics for learning).

**User Prompt:**
```
You are a social media trend analyst. Today's date is {today_str}.

Given a brand's context, the CURRENT seasonal/cultural moment, and Google Trends data, generate the TOP 15 most relevant trending topics for this brand's content strategy RIGHT NOW.

═══ BRAND CONTEXT ═══
Brand: {brand.brand_name}
Industry: {brand.industry}
Target Region: {brand.target_region or 'Global'}
Target Audience: {dna.get('target_audience', 'general')}
Brand Voice: {dna.get('brand_voice', 'professional')}
Content Pillars: {', '.join(pillar_names) if pillar_names else 'Not set'}
Brand Values: {', '.join(dna.get('brand_values', [])[:5]) if dna.get('brand_values') else 'Not set'}
Competitor Strategies: {'; '.join(insight_texts[:5]) if insight_texts else 'None analyzed yet'}

═══ CURRENT SEASONAL & CULTURAL CONTEXT ({today_str}) ═══
{seasonal_text}

═══ GOOGLE TRENDS DATA ═══
{trend_list}
{feedback_context}

═══ INSTRUCTIONS ═══
Generate exactly 15 trending topics. Your response MUST include:
- At least 4-5 topics tied to the CURRENT seasonal/cultural events listed above (Ramadan content, Eid prep, seasonal campaigns, etc.) — these should be the highest-scored topics
- The remaining topics should be industry-specific trends, viral social media themes, or Google Trends-based topics relevant to the brand
- Each topic should be specific and actionable for social media content (not generic like "post more")
- volume_score should reflect CURRENT relevance: seasonal/active events = 80-95, industry trends = 50-80, evergreen = 30-50
- category should classify the topic: "seasonal", "cultural", "industry", "viral", "evergreen"

Return a JSON object:
{{"topics": [{{"topic": "specific topic name", "volume_score": 0-100, "relevance_explanation": "1-sentence why this matters NOW for the brand", "platform": "google", "category": "seasonal|cultural|industry|viral|evergreen"}}]}}
```

---

## 16. Brand DNA from Website

- **File Location:** D:/Projects/Final_version_socialSync/api/views.py
- **Lines:** 2827-2854
- **API:** `POST /api/v1/brands/{brand_id}/generate-dna/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.3, max_tokens: 2500)
- **Goal:** Crawl a brand's website (up to 5 pages), extract the content, and use AI to build a complete 15-field Brand DNA profile with brand name, tagline, industry, products, audience, voice, values, colors, keywords, and more.

**System Prompt:**
```
You are a brand strategist. Analyze the website content and extract detailed brand DNA. Return only valid JSON.
```

**User Prompt:**
```
Analyze this website and extract a complete Brand DNA profile.

WEBSITE: {url}
TITLE: {page_data['title']}
DESCRIPTION: {page_data['description']}

PAGE CONTENT:
{page_data['content']}

Extract a Brand DNA with these sections (be specific, use actual details from the page):

1. brand_name: The brand's name
2. tagline: Their tagline or slogan (if visible)
3. industry: Their industry/niche
4. description: What the brand does in 2-3 sentences
5. products_services: List of main products or services offered (array of strings)
6. target_audience: Who their target customers are
7. unique_selling_points: What makes them different (array of strings, max 5)
8. brand_voice: Their communication tone/style (e.g., professional, casual, bold, friendly)
9. brand_values: Core values (array of strings, max 5)
10. color_theme: Dominant colors observed (array of strings)
11. content_themes: Main content topics/themes they focus on (array of strings)
12. cta_style: How they write calls-to-action
13. social_platforms: Any social media platforms mentioned (array of strings)
14. keywords: Key SEO/marketing terms used (array of strings, max 10)
15. competitor_positioning: How they position themselves vs competitors

Return as a single JSON object. Only return valid JSON, no other text.
```

---

## 17. Brand DNA Enhancement (Website)

- **File Location:** D:/Projects/Final_version_socialSync/api/views.py
- **Lines:** 171-183
- **API:** `POST /api/v1/auth/register-with-brand/` (best-effort AI enhancement during registration)
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.3, max_tokens: 2500)
- **Goal:** During user registration with a brand, enhance the manually-entered Brand DNA by crawling the brand's website and filling in gaps/improving descriptions using actual website content.

**System Prompt:**
```
You are a brand strategist. Enhance the brand DNA using website data. Return only valid JSON.
```

**User Prompt:**
```
Enhance this existing Brand DNA using the website content below.
Keep all existing values but fill in gaps and improve descriptions.

EXISTING DNA:
{existing_dna}

WEBSITE: {brand.website_url}
TITLE: {page_data.get('title', '')}
CONTENT:
{page_data.get('content', '')}

Return the enhanced Brand DNA as a single JSON object with the same 15 fields.
Only return valid JSON, no other text.
```

---

## 18. Brand DNA Enhancement (Input)

- **File Location:** D:/Projects/Final_version_socialSync/api/views.py
- **Lines:** 3003-3011
- **API:** `POST /api/v1/brands/{brand_id}/regenerate-dna-inputs/` (with `use_ai: true`)
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.3, max_tokens: 2500)
- **Goal:** Enhance user-provided Brand DNA fields by making descriptions richer, filling empty fields with reasonable defaults, and ensuring consistency across all 15 DNA fields.

**System Prompt:**
```
You are a brand strategist. Enhance the brand DNA. Return only valid JSON.
```

**User Prompt:**
```
Enhance and fill in gaps for this Brand DNA profile.
Keep user-provided values but make descriptions richer and more specific.
Fill in any empty fields with reasonable defaults based on the other information.

CURRENT DNA:
{json.dumps(dna_data, indent=2)}

Return the enhanced Brand DNA as a single JSON object with the same 15 fields.
Only return valid JSON, no other text.
```

---

## 19. AI Comment Reply

- **File Location:** D:/Projects/Final_version_socialSync/api/analytics_views.py
- **Lines:** 113-126
- **API:** `POST /api/v1/comments/{comment_id}/ai-reply/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.7, max_tokens: 200)
- **Goal:** Generate a brief, friendly, brand-voice-matched reply to a social media comment. The reply references the actual comment content to avoid generic responses.

**System Prompt:**
```
You are a social media community manager.
```

**User Prompt:**
```
Generate a brief, friendly reply to this social media comment.

Comment: "{comment.body}"
Author: {comment.author_name or 'Someone'}
Post caption: {(post.caption or '')[:300]}
{brand_voice}

Rules:
- Keep it concise (1-3 sentences)
- Be warm and engaging
- Match the brand voice if provided
- Don't be generic — reference the comment content

Return only the reply text, nothing else.
```

---

## 20. Optimal Posting Times

- **File Location:** D:/Projects/Final_version_socialSync/api/scheduling_views.py
- **Lines:** 250-273
- **API:** `POST /api/v1/schedule/compute-times/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.3, max_tokens: 2000)
- **Goal:** Analyze competitor posting patterns and engagement data to recommend the top 3-5 optimal posting time slots per platform, including day of week, hour (UTC), confidence score, and reasoning.

**User Prompt:**
```
You are a social media scheduling analyst. Analyze competitor data and recommend optimal posting times.

Brand: {brand.brand_name}
Industry: {brand.industry}
Region: {brand.target_region}
{f'Target platforms: {", ".join(platforms_filter)}' if platforms_filter else 'Target platforms: twitter, linkedin, facebook, instagram'}

Competitor Insights:
{chr(10).join(insight_texts[:15]) if insight_texts else 'No competitor data yet — use industry best practices instead.'}

Recommend the top 3-5 optimal posting time slots PER platform. Consider:
- When competitors are most active/successful
- Industry-standard best times for the region
- Different content types may need different times

Return a JSON object:
{{"recommendations": [{{"platform": "twitter", "day_of_week": 0, "hour_utc": 14, "score": 0.85, "reason": "Brief reason"}}]}}

Rules:
- day_of_week: 0=Monday, 6=Sunday
- hour_utc: 0-23 (UTC time)
- score: 0.0-1.0 (confidence)
- Include 3-5 slots per platform
- Order by score descending
```

---

## 21. Video Generation (Gemini Veo 2)

- **File Location:** D:/Projects/Final_version_socialSync/ai_video/gemini_service.py
- **Lines:** 76-127
- **API:** `POST /api/v1/ai-video/generate/`
- **AI Model:** Google Gemini Veo 2 (`veo-2.0-generate-001`)
- **Goal:** Generate AI videos from text prompts. The prompt is enhanced with style descriptors, camera motion instructions, and motion intensity before being sent to the Veo 2 model.

**Prompt Construction:**
```
{base_prompt}. {style_prompt}. {camera_motion_prompt}. {motion_intensity_prompt}. Duration: {duration} seconds, aspect ratio: {aspect_ratio}
```

**Available Style Prompts:**
- realistic: "photorealistic, cinematic quality, natural lighting, detailed textures, lifelike"
- cinematic: "cinematic, movie-like, dramatic lighting, film grain, professional cinematography, widescreen"
- anime: "anime style, Japanese animation, vibrant colors, expressive, dynamic, 2D animated"
- cartoon: "cartoon style, animated, colorful, playful, exaggerated expressions, fun"
- 3d_animation: "3D animated, Pixar-style, rendered, smooth animation, CGI quality"
- artistic: "artistic, creative, painterly, expressive, unique visual style"
- vintage: "vintage film, retro, nostalgic, old movie aesthetic, film scratches, sepia tones"
- slow_motion: "slow motion, smooth, detailed motion, time-stretched, cinematic slow-mo"
- timelapse: "timelapse, accelerated time, smooth transitions, time compression"
- documentary: "documentary style, realistic, informative, natural, observational"
- sci_fi: "science fiction, futuristic, high-tech, neon lights, cyberpunk elements"
- fantasy: "fantasy, magical, ethereal, mystical, enchanting atmosphere"
- horror: "dark, atmospheric, suspenseful, moody lighting, eerie"
- comedy: "bright, colorful, fun, energetic, lighthearted"
- music_video: "music video style, dynamic cuts, rhythmic, visually striking, artistic"

**Available Camera Motions:**
- static: "static camera, fixed shot, no camera movement"
- pan_left: "camera panning left, horizontal movement left"
- pan_right: "camera panning right, horizontal movement right"
- tilt_up: "camera tilting up, vertical movement upward"
- tilt_down: "camera tilting down, vertical movement downward"
- zoom_in: "camera zooming in, getting closer, push in"
- zoom_out: "camera zooming out, pulling back, wide reveal"
- orbit: "camera orbiting, circling around subject, 360 movement"
- dolly: "dolly shot, camera tracking, smooth forward movement"
- crane: "crane shot, elevated camera movement, sweeping"
- handheld: "handheld camera, slight shake, documentary feel"

**Available Motion Intensities:**
- subtle: "subtle movement, gentle motion, calm"
- moderate: "moderate movement, balanced motion"
- dynamic: "dynamic movement, energetic, active"
- intense: "intense movement, fast-paced, high energy, dramatic action"

---

## 22. Overflow Page - Caption Prompt (Frontend)

- **File Location:** D:/Projects/Final_version_socialSync/frontend/src/pages/OverflowPage.tsx
- **Lines:** 1431-1446
- **API:** `POST /api/v1/ai-caption/generate/` (called from frontend with custom_instructions)
- **AI Model:** OpenAI GPT-4o (via backend)
- **Goal:** Auto-generate 3 caption variants for each selected content idea in the Overflow flow. Each variant must use a completely different creative angle, be ready to copy-paste and post directly, and never mention internal IDs.

**Hardcoded Base Instructions (sent as `custom_instructions`):**
```
Write a ready-to-post social media caption for {platform}. The caption must be engaging, scroll-stopping, and ready to copy-paste and post directly. Do NOT mention any idea number, internal ID, or the word "idea". Do NOT include any reference numbers. Variant {VAR} of 3 — each must use a completely different creative angle.
```

**Additional user instructions appended as:**
```
USER INSTRUCTIONS (must follow): {customInstructions}
```

**Parameters sent:**
- topic: `{idea.title}\n\nHook: {idea.hook}\nAngle: {idea.angle}`
- tone: `enthusiastic`
- length: `medium`
- platform: from idea's platform
- include_hashtags: `true`
- include_emojis: `true`
- include_cta: `true`

---

## 23. Overflow Page - Image Prompt (Frontend)

- **File Location:** D:/Projects/Final_version_socialSync/frontend/src/pages/OverflowPage.tsx
- **Lines:** 1797-1798
- **API:** `POST /api/v1/ai-image/generate/`
- **AI Model:** Gemini or DALL-E (via backend, provider selected by user)
- **Goal:** Generate professional social media content images with a safety-conscious prompt wrapper that ensures brand-appropriate, clean, and marketing-suitable output.

**Prompt Template:**
```
Professional social media content image: {prompt.trim()}. Clean, brand-appropriate, high quality, suitable for marketing.
```

**Parameters sent:**
- prompt: the safety-wrapped prompt above
- style: user-selected style
- enhance_prompt: `true`

---

## 24. AI Caption System Prompt — Platform Guidelines Reference

- **File Location:** D:/Projects/Final_version_socialSync/ai_caption/openai_service.py
- **Lines:** 43-55
- **API:** Used internally by all caption generation methods
- **AI Model:** N/A (reference data used in system prompts)
- **Goal:** Provide platform-specific optimization guidelines that are injected into the system prompt for all caption generation. These guidelines ensure captions are optimized for each platform's unique characteristics.

**Platform Guidelines Map:**
```
general:   "Create a versatile caption suitable for any platform."
facebook:  "Optimize for Facebook: longer captions work well, include engaging questions, consider Facebook's algorithm favoring meaningful interactions."
instagram: "Optimize for Instagram: strong opening line, use line breaks for readability, hashtags at the end (up to 30 allowed but 5-10 recommended), consider Instagram's visual-first nature."
twitter:   "Optimize for Twitter/X: Keep it concise (under 280 characters ideally), punchy and engaging, 1-3 hashtags max, consider thread potential."
linkedin:  "Optimize for LinkedIn: Professional tone, industry insights, thought leadership angle, minimal hashtags (3-5), strong opening hook."
tiktok:    "Optimize for TikTok: Trendy, casual tone, use trending sounds/challenges references if relevant, short and catchy, viral potential."
youtube:   "Optimize for YouTube: SEO-friendly, include keywords, compelling description, call to subscribe/engage."
pinterest: "Optimize for Pinterest: Descriptive, SEO-rich, include keywords users might search for, inspirational tone."
```

---

## Summary

### AI Models Used

| Model                                          | Provider | Usage Count | Primary Use                              |
|-------------------------------------------------|----------|-------------|------------------------------------------|
| GPT-4o-mini                                     | OpenAI   | 14          | Strategy, DNA, trending, competitors, alt text |
| GPT-4o                                          | OpenAI   | 7           | Captions, image/video analysis           |
| GPT-4o (Vision)                                 | OpenAI   | 3           | Image analysis, video frame analysis     |
| DALL-E 3 / DALL-E 2                             | OpenAI   | 1           | Image generation                         |
| Gemini 2.0 Flash Exp / Imagen 3                 | Google   | 1           | Image generation                         |
| Gemini Veo 2 (veo-2.0-generate-001)             | Google   | 1           | Video generation                         |

### API Endpoints with AI Prompts

| Endpoint                                          | Method | Prompt # |
|---------------------------------------------------|--------|----------|
| `/api/v1/drafts/{id}/captions/generate/`          | POST   | 1        |
| `/api/v1/drafts/{id}/captions/adapt/`             | POST   | 2        |
| `/api/v1/ai-caption/generate/`                    | POST   | 3-7      |
| `/api/v1/ai-caption/regenerate/{id}/`             | POST   | 8        |
| `/api/v1/brands/{id}/competitors/crawl/`          | POST   | 10       |
| `/api/v1/ideas/generate/`                         | POST   | 11       |
| `/api/v1/ideas/{id}/regenerate/`                  | POST   | 12       |
| `/api/v1/competitors/suggest/`                    | POST   | 13       |
| `/api/v1/brands/{id}/pillars/generate/`           | POST   | 14       |
| `/api/v1/brands/{id}/trending/generate/`          | POST   | 15       |
| `/api/v1/brands/{id}/generate-dna/`               | POST   | 16       |
| `/api/v1/auth/register-with-brand/`               | POST   | 17       |
| `/api/v1/brands/{id}/regenerate-dna-inputs/`      | POST   | 18       |
| `/api/v1/comments/{id}/ai-reply/`                 | POST   | 19       |
| `/api/v1/schedule/compute-times/`                 | POST   | 20       |
| `/api/v1/ai-video/generate/`                      | POST   | 21       |
| `/api/v1/ai-caption/generate/` (via Overflow)     | POST   | 22       |
| `/api/v1/ai-image/generate/` (via Overflow)       | POST   | 23       |
| `/api/v1/ai-image/generate/` (DALL-E)             | POST   | 25       |
| `/api/v1/ai-image/generate/` (Gemini)             | POST   | 26       |
| `/api/v1/assets/{id}/alt-text/`                   | POST   | 27       |


---

## BONUS: Image & Alt Text Generation Prompts

---

## 25. DALL-E 3 Image Generation (Prompt Enhancement)

- **File Location:** D:/Projects/Final_version_socialSync/ai_image/openai_service.py
- **Lines:** 27-98, 131-186
- **API:** `POST /api/v1/ai-image/generate/` (with provider = openai)
- **AI Model:** OpenAI DALL-E 3 / DALL-E 2
- **Goal:** Generate images using DALL-E. The user's prompt is enhanced with style descriptors, lighting instructions, and camera angle prompts before being sent to the API. Supports HD quality, vivid/natural styles, and multiple sizes.

**Prompt Enhancement Construction:**
```
{user_prompt}. {style_prompt}. {lighting_prompt}. {camera_angle_prompt}
```

**Available Style Prompts:**
```
realistic:    "photorealistic, highly detailed, 8k resolution, professional photography"
artistic:     "artistic, creative, expressive brushstrokes, fine art style"
anime:        "anime style, manga art, vibrant colors, Japanese animation aesthetic"
cartoon:      "cartoon style, bold outlines, bright colors, playful, illustrated"
3d_render:    "3D rendered, CGI, volumetric lighting, ray tracing, octane render"
watercolor:   "watercolor painting, soft edges, flowing colors, paper texture"
oil_painting: "oil painting, rich textures, classical art style, canvas texture"
digital_art:  "digital art, modern, clean lines, vibrant, concept art style"
pixel_art:    "pixel art, retro game style, 16-bit, nostalgic, crisp pixels"
sketch:       "pencil sketch, hand-drawn, artistic lines, shading, detailed drawing"
cinematic:    "cinematic, movie scene, dramatic lighting, widescreen, film grain"
fantasy:      "fantasy art, magical, ethereal, mystical atmosphere, epic"
minimalist:   "minimalist, simple, clean, modern design, negative space"
vintage:      "vintage, retro, nostalgic, aged look, classic aesthetic"
neon:         "neon lights, cyberpunk, futuristic, glowing, vibrant colors, sci-fi"
vivid:        "vivid colors, hyper-detailed, dramatic, bold"
natural:      "natural, soft lighting, realistic, subtle tones"
```

**Available Lighting Prompts:**
```
natural:     "natural lighting, soft shadows, outdoor light"
studio:      "studio lighting, professional, controlled light, softbox"
dramatic:    "dramatic lighting, high contrast, chiaroscuro, moody"
soft:        "soft diffused light, gentle shadows, even illumination"
golden_hour: "golden hour lighting, warm tones, sunset glow"
neon:        "neon lighting, colorful glow, cyberpunk atmosphere"
backlit:     "backlit, silhouette edges, rim lighting, glowing outline"
```

**Available Camera Angle Prompts:**
```
front:     "front view, facing camera, straight on"
side:      "side view, profile shot, lateral angle"
aerial:    "aerial view, bird's eye view, top down perspective"
low_angle: "low angle shot, looking up, powerful perspective"
high_angle:"high angle shot, looking down, overview"
closeup:   "close-up shot, detailed, intimate framing"
wide:      "wide shot, full scene, environmental context"
macro:     "macro shot, extreme close-up, fine details visible"
```

**Negative Prompt Handling:**
```
{enhanced_prompt}. Avoid: {negative_prompt}
```

---

## 26. Gemini Image Generation (Prompt Enhancement)

- **File Location:** D:/Projects/Final_version_socialSync/ai_image/gemini_service.py
- **Lines:** 27-96, 98-153
- **API:** `POST /api/v1/ai-image/generate/` (with provider = gemini)
- **AI Model:** Gemini 2.0 Flash Experimental (`gemini-2.0-flash-exp-image-generation`) / Imagen 3 (`imagen-3.0-generate-001`, `imagen-3.0-fast-generate-001`)
- **Goal:** Generate images using Google Gemini. The user's prompt is enhanced with the same style, lighting, and camera angle descriptors as DALL-E. Falls back from Gemini 2.0 Flash to Imagen 3 if the first model fails.

**Prompt Enhancement Construction:**
```
{user_prompt}. {style_prompt}. {lighting_prompt}. {camera_angle_prompt}
```

**Negative Prompt Handling:**
```
{enhanced_prompt}. Do not include: {negative_prompt}
```

*(Style, lighting, and camera angle prompts are identical to DALL-E — see Prompt #25 above)*

---

## 27. Alt Text Generation

- **File Location:** D:/Projects/Final_version_socialSync/ai_image/services/alt_text_service.py
- **Lines:** 33-46
- **API:** `POST /api/v1/assets/{asset_id}/alt-text/`
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.3, max_tokens: 100)
- **Goal:** Generate concise, accessible alt text (max 125 characters) for images based on their title, generation prompt, and style. Used for web accessibility compliance.

**System Prompt:**
```
You generate concise image alt text for accessibility.
```

**User Prompt:**
```
Generate a concise, descriptive alt text for an image.

Context about the image:
{context}

Rules:
- Maximum 125 characters
- Be descriptive but concise
- Focus on what the image shows, not interpretation
- Don't start with "Image of" or "Photo of"
- Include key visual elements, colors, and subjects

Return only the alt text string, nothing else.
```

---

## 28. Hashtag Generation

- **File Location:** D:/Projects/Final_version_socialSync/posts/services/hashtag_service.py
- **Lines:** 52-69
- **API:** Internal service (called from post creation/editing flows)
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.7, max_tokens: 1000, JSON mode)
- **Goal:** Generate platform-specific hashtags with a 3-tier distribution strategy (30% high-volume, 40% mid-volume, 30% niche). Respects per-platform hashtag limits (Instagram: 20, LinkedIn: 5, Twitter: 3, Facebook: 3) and filters out banned hashtags.

**System Prompt:**
```
You are a social media hashtag expert. Return only valid JSON.
```

**User Prompt:**
```
Generate exactly {count} hashtags for a {platform} post.

Context:
{brand_context}
Caption: {caption_text[:500]}
{f'Topic: {topic}' if topic else ''}

Rules:
- Return hashtags WITHOUT the # symbol
- Organize into three tiers:
  * high_volume ({int(count * 0.3)} tags): Popular, broad reach hashtags (100k+ posts)
  * mid_volume ({int(count * 0.4)} tags): Moderately popular, relevant hashtags (10k-100k posts)
  * niche ({count - int(count * 0.3) - int(count * 0.4)} tags): Specific, low-competition hashtags (<10k posts)
- Banned hashtags to EXCLUDE: {', '.join(banned_tags) if banned_tags else 'none'}

Return JSON format:
{{"hashtags": [{{"tag": "hashtagname", "tier": "high_volume|mid_volume|niche", "estimated_volume": 50000}}]}}
```

**Dynamic Context Variables:**
```
brand_context = "Brand: {brand_name}, Industry: {industry}"  (+ ", Content Pillar: {pillar_name}" if pillar exists)
Platform limits: instagram=20, linkedin=5, twitter=3, facebook=3
```

---

## 29. Messenger AI Importance Detection

- **File Location:** D:/Projects/Final_version_socialSync/messenger_bot/services/message_handler.py
- **Lines:** 357-380
- **API:** Internal service (called automatically when a Messenger message is received)
- **AI Model:** OpenAI GPT-4o-mini (temperature: 0.1, max_tokens: 200)
- **Goal:** Classify incoming Facebook Messenger messages to determine if they require business attention. Detects message type (product inquiry, appointment, order, urgent, complaint, pricing, availability, contact, or general) and assigns priority. Falls back to keyword-based detection if AI is unavailable.

**User Prompt:**
```
Analyze this customer message and determine if it requires business attention.

Message: "{message}"

Respond in JSON format only:
{{
    "is_important": true/false,
    "type": "product_inquiry" | "appointment" | "order" | "urgent" | "complaint" | "pricing" | "availability" | "contact" | "general",
    "priority": "high" | "medium" | "low",
    "title": "Brief title (max 50 chars)",
    "summary": "Brief summary of what the customer wants (max 100 chars)"
}}

Important messages include:
- Product purchase inquiries
- Appointment/meeting requests
- Order confirmations
- Urgent requests
- Complaints or issues
- Pricing questions
- Stock/availability checks
- Contact/location requests

General greetings or casual chat are NOT important.
```

**Fallback Keyword Detection:**
When AI is unavailable, the system uses a keyword map with categories: `product_inquiry`, `appointment`, `order`, `urgent`, `complaint`, `pricing`, `availability`, `contact` — supporting both English and Bengali (বাংলা) keywords.

---

## 30. Messenger Image Description (GPT-4o Vision)

- **File Location:** D:/Projects/Final_version_socialSync/messenger_bot/services/message_handler.py
- **Lines:** 625-631
- **API:** Internal service (called when a user sends an image via Messenger)
- **AI Model:** OpenAI GPT-4o Vision (max_tokens: 1000)
- **Goal:** Analyze images sent by Messenger users using GPT-4o Vision. Provides detailed description covering content type, main subject, product details, text extraction, and other relevant details. The description is then used for knowledge base matching and response generation.

**User Prompt (with image):**
```
Analyze this image in detail:
1. What type of content? (screenshot, photo, product, document)
2. Main subject/content
3. If product: brand, features, specifications, price if visible
4. If screenshot: extract all visible text
5. Any other relevant details
```

**Note:** Facebook CDN images are automatically downloaded and converted to base64 before being sent to OpenAI Vision API, since Facebook CDN URLs are temporary and may not be directly accessible.

---

## 31. Messenger Image Response with Knowledge Context

- **File Location:** D:/Projects/Final_version_socialSync/messenger_bot/services/message_handler.py
- **Lines:** 839-852
- **API:** Internal service (called after image analysis to generate a contextual response)
- **AI Model:** Configurable via `ai_config.openai_model` (default GPT-4o), temperature and max_tokens from config
- **Goal:** Generate a response that combines the image analysis with knowledge base context (PDFs, Brand DNA, product catalog). Uses the connection's active custom system prompt for brand-specific tone and behavior.

**System Prompt:** *(Loaded dynamically from the connection's active prompt configuration)*
```
{active_prompt.system_prompt}  (or fallback: "You are a helpful business assistant.")
```

**User Prompt (with knowledge context):**
```
User question: "{user_question}"

Image analysis: {image_description}

Company knowledge:
{knowledge_context}

Provide helpful response using company information.
```

**User Prompt (without knowledge context):**
```
User question: "{user_question}"

Image analysis: {image_description}

Provide helpful response.
```

---

## 32. RAG System Prompt (Messenger Bot)

- **File Location:** D:/Projects/Final_version_socialSync/messenger_bot/services/rag_engine.py
- **Lines:** 307-326, 336-341, 354-359
- **API:** Internal service (used for all Messenger bot AI responses when RAG is enabled)
- **AI Model:** Configurable via `ai_config.openai_model`, temperature and max_tokens from config
- **Goal:** Core system prompt for the Messenger bot's RAG (Retrieval-Augmented Generation) engine. Enforces language detection (responds in the same language as the user — supports Bengali, English, and any other language), disables markdown formatting for messaging apps, and sets conversational response style. Dynamically adds e-commerce product catalog context when available.

**System Prompt:**
```
{base_system_prompt}

IMPORTANT RULES:
1. LANGUAGE: Detect the language of the user's message and ALWAYS respond in the SAME language.
   - If user writes in Bengali (বাংলা), respond in Bengali
   - If user writes in English, respond in English
   - If user writes in any other language, respond in that language
   - If user mixes languages, respond in the dominant language

2. FORMATTING:
   - Do NOT use markdown formatting like **bold**, *italic*, ### headers
   - Do NOT use bullet points with - or *
   - Write in natural, conversational paragraphs
   - Keep responses clean and readable for messaging apps

3. RESPONSE STYLE:
   - Be helpful and friendly
   - Give complete answers, don't cut off mid-sentence
   - Be concise but thorough
   - When sharing product info, include the price, availability, and link if available
```

**Dynamic E-Commerce Context Addition:**
```
You have access to a product catalog with {product_count} products. When users ask about products, use the product information from the knowledge base to provide accurate answers including prices (in {currency_symbol}), availability, and direct links. If a user wants to order, provide the product link.
```

**RAG User Message (with context):**
```
Based on the following information:

{context_text}

Please answer this question: {query}
```

**RAG User Message (without context):**
```
{query}
```

**Context Sources:** The RAG engine retrieves context from 3 sources:
1. **PDF Knowledge Base** — uploaded business documents, vectorized into chunks
2. **Brand DNA** — crawled website content with page titles and URLs
3. **Product Catalog** — WooCommerce products with name, price, stock, description, SKU, and permalink

---

## 33. Product Scene Background Prompt Enhancement

- **File Location:** D:/Projects/Final_version_socialSync/ai_image/product_compositor.py
- **Lines:** 210-224
- **API:** Internal service (called when user uploads a product image for AI scene generation)
- **AI Model:** DALL-E 3 or Gemini (whichever provider is selected for image generation)
- **Goal:** When a user uploads their own product image, this prompt modifies the user's scene description to generate ONLY a background/scene (no product). The AI-generated scene is then used as a backdrop, and the user's product is composited on top with background removal and shadow effects.

**Prompt Enhancement:**
```
The user has uploaded their own product image. Generate a professional product photography background/scene based on this description: {original_prompt}. This scene will be used to showcase the user's product. Create a clean, professional environment that complements a product placement. Leave clear space in the center of the composition for the product to be placed. Do NOT generate any product or object in the image — only the background, scene, and environment.
```

**Negative Prompt Addition:**
```
product, item, object in center, subject in foreground
```
*(Appended to any existing negative prompt to ensure the AI does not generate objects in the scene)*
