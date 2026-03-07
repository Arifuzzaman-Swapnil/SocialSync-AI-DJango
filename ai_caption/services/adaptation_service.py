"""
Caption Adaptation Service
- Platform-specific copy adaptation
- Character limit enforcement
- Tone adaptation per platform
"""
import json
import logging

from accounts.services.llm_service import get_llm_service, UnifiedLLMService
from posts.models import PostCaption

logger = logging.getLogger(__name__)

PLATFORM_GUIDELINES = {
    'twitter': {
        'max_chars': 280,
        'tone': 'concise, punchy, conversational',
        'notes': 'Use short sentences. Thread if needed. Hashtags inline.',
    },
    'linkedin': {
        'max_chars': 3000,
        'tone': 'professional, insightful, thought-leadership',
        'notes': 'Use line breaks for readability. Lead with a hook. End with a CTA or question.',
    },
    'facebook': {
        'max_chars': 63206,
        'tone': 'casual, conversational, community-oriented',
        'notes': 'Use emojis sparingly. Ask questions to drive engagement. Keep under 250 chars for best reach.',
    },
    'instagram': {
        'max_chars': 2200,
        'tone': 'visual, authentic, storytelling',
        'notes': 'Front-load the hook. Use line breaks. Hashtags in first comment or end. Include CTAs.',
    },
}


def adapt_caption(source_caption, target_platform, api_key=None, brand=None, override_prompt=None, user=None, think_harder=False):
    """Adapt a caption for a specific platform.

    Returns tuple (adapted PostCaption object, used_prompt string).

    When `user` is provided, uses get_llm_service(user) for provider routing.
    Falls back to UnifiedLLMService(openai_key=api_key) for backward compat.
    """
    if not api_key and not user:
        # Fallback: simple truncation
        return _simple_adapt(source_caption, target_platform), ''

    guidelines = PLATFORM_GUIDELINES.get(target_platform, PLATFORM_GUIDELINES['facebook'])

    brand_context = ''
    if brand:
        brand_context = f"Brand voice: {brand.voice_tone or 'professional'}"

    prompt = f"""<context>
You are adapting an existing caption from one platform to another.

Target platform: {target_platform}
Platform character limit: {guidelines['max_chars']}
Platform tone guidance: {guidelines['tone']}
Platform-specific notes: {guidelines['notes']}
Brand context: {brand_context}
</context>

<source_caption>
{source_caption.body}
</source_caption>

<instructions>
Think step by step:

1. READ the source caption and extract:
   - The core message (1 sentence summary)
   - The emotional hook
   - The CTA intent (if any)
2. REWRITE for {target_platform} from scratch, as if a native user of that platform wrote it:
   - Adapt tone to match {guidelines['tone']}
   - Restructure for platform reading patterns (e.g., LinkedIn's "see more" fold, Instagram's 125-char preview, Twitter's character constraint)
   - Apply platform-specific engagement mechanics (questions for Facebook, hot takes for Twitter, storytelling for LinkedIn)
3. VERIFY the final caption is within {guidelines['max_chars']} characters.
</instructions>

<output_format>
Return ONLY this JSON structure:
{{
  "adapted_body": "<adapted caption text>",
  "cta_text": "<adapted CTA or empty string>"
}}
</output_format>

<constraints>
- STRICTLY stay within {guidelines['max_chars']} characters — count carefully.
- Do NOT simply truncate or pad the original — fully reimagine it.
- Preserve the core message and intent.
- No generic filler phrases.
- Return valid JSON only.
</constraints>"""

    if override_prompt:
        prompt = override_prompt

    try:
        if user:
            service = get_llm_service(user)
        else:
            service = UnifiedLLMService(openai_key=api_key)

        result = service.chat_completion(
            messages=[
                {"role": "system", "content": "You are a platform-native social media strategist who specializes in cross-platform content adaptation. You understand that each platform has its own culture, algorithm preferences, and audience behavior patterns.\n\nYour expertise:\n- Twitter/X: Punchy, conversational, opinion-driven. Max 280 chars. Threads for depth. Power of brevity and hot takes. Algorithm favors replies and quotes.\n- LinkedIn: Professional thought leadership. First line is everything (it appears before \"see more\"). Story-driven, insight-led. 1300-1700 chars optimal. Algorithm favors comments and dwell time.\n- Facebook: Conversational, community-oriented. Questions drive engagement. Longer posts (400-800 chars) perform well. Algorithm favors meaningful interactions.\n- Instagram: Visual-first but caption matters. Hook in first 125 chars (before truncation). Emojis, line breaks for readability. Hashtag strategy. 2200 char max. Algorithm favors saves and shares.\n- TikTok: Ultra-casual, trend-aware, Gen-Z native language. Short hooks. 150 chars max recommended for overlay. Algorithm favors watch time.\n\nYour job is to translate the SOUL of a caption for a new platform — not just shorten or lengthen it. Rewrite it as if a native user of that platform wrote it from scratch.\n\nCRITICAL OUTPUT RULES:\n- Return ONLY valid JSON\n- Do NOT include explanations, notes, or markdown\n- Stay within character limits — this is non-negotiable"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000 if think_harder else 1500,
            response_format={"type": "json_object"},
            thinking_budget=10000 if think_harder else 0,
        )

        if not result.success:
            raise Exception(result.error)

        parsed = json.loads(result.content)
        body = parsed.get('adapted_body', source_caption.body)
        cta = parsed.get('cta_text', source_caption.cta_text)

    except Exception as e:
        logger.error(f"Caption adaptation failed: {e}")
        return _simple_adapt(source_caption, target_platform), prompt

    # Enforce character limit
    max_chars = guidelines['max_chars']
    if len(body) > max_chars:
        body = body[:max_chars - 3] + '...'

    adapted = PostCaption.objects.create(
        post=source_caption.post,
        platform=target_platform,
        variant_number=source_caption.variant_number,
        body=body,
        cta_text=cta,
        tone=guidelines['tone'].split(',')[0].strip(),
    )

    source_caption.post.update_checklist()
    return adapted, prompt


def _simple_adapt(source_caption, target_platform):
    """Fallback adaptation with simple truncation."""
    guidelines = PLATFORM_GUIDELINES.get(target_platform, {})
    max_chars = guidelines.get('max_chars', 5000)
    body = source_caption.body

    if len(body) > max_chars:
        body = body[:max_chars - 3] + '...'

    adapted = PostCaption.objects.create(
        post=source_caption.post,
        platform=target_platform,
        variant_number=source_caption.variant_number,
        body=body,
        cta_text=source_caption.cta_text,
        tone=source_caption.tone,
    )
    return adapted
