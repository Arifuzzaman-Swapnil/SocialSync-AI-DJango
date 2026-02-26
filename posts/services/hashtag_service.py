"""
Hashtag Generation Service
- LLM-based generation with 30/40/30 tier ratio (high/mid/niche)
- Banned hashtag filtering
- Platform-specific count limits
"""
import openai
import json
import logging

from posts.models import PostHashtag, BannedHashtag

logger = logging.getLogger(__name__)

# Platform hashtag limits
PLATFORM_LIMITS = {
    'instagram': 20,
    'linkedin': 5,
    'twitter': 3,
    'facebook': 3,
}


def generate_hashtags(post, platform, api_key, count=None, topic=None):
    """Generate hashtags for a post using LLM with tier distribution.

    Returns list of created PostHashtag objects.
    """
    if not api_key:
        logger.warning("No OpenAI API key available for hashtag generation")
        return []

    # Determine count based on platform defaults
    if count is None:
        count = PLATFORM_LIMITS.get(platform, 10)

    # Get banned hashtags for this brand
    banned_tags = set()
    if post.brand:
        banned_tags = set(
            BannedHashtag.objects.filter(brand=post.brand).values_list('tag', flat=True)
        )

    # Build context for LLM
    caption_text = post.caption or ''
    brand_context = ''
    if post.brand:
        brand_context = f"Brand: {post.brand.brand_name}, Industry: {post.brand.industry or 'general'}"
    if post.pillar:
        brand_context += f", Content Pillar: {post.pillar.name}"

    high_count = int(count * 0.3)
    mid_count = int(count * 0.4)
    niche_count = count - high_count - mid_count

    prompt = f"""<task>
Generate exactly {count} hashtags for a {platform} post using a 3-tier volume distribution strategy.
</task>

<context>
Brand: {brand_context}
Caption: {caption_text[:500]}
{f'Topic: {topic}' if topic else ''}
</context>

<tier_distribution>
| Tier | Count | Volume Target |
|------|-------|---------------|
| high_volume | {high_count} | 100k+ posts |
| mid_volume | {mid_count} | 10k-100k posts |
| niche | {niche_count} | <10k posts |
</tier_distribution>

<instructions>
1. Analyze the caption and topic for key themes, keywords, and audience signals.
2. Generate hashtags that are directly relevant to the content.
3. Distribute across tiers as specified.
4. Return WITHOUT the # symbol.
</instructions>

<output_format>
{{
  "hashtags": [
    {{
      "tag": "<hashtag without #>",
      "tier": "<high_volume | mid_volume | niche>",
      "estimated_volume": <number>
    }}
  ]
}}
</output_format>

<constraints>
- Exactly {count} hashtags total.
- No # symbol in tag values.
- EXCLUDE these banned hashtags: {', '.join(banned_tags) if banned_tags else 'none'}
- Platform limits: instagram=20, linkedin=5, twitter=3, facebook=3.
- Return valid JSON only.
</constraints>"""

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a social media growth strategist who engineers hashtag strategies for maximum discoverability. You understand that hashtag strategy is not just about relevance — it's about strategic placement across volume tiers to balance reach (high-volume) with discoverability (niche).\n\nYour approach:\n- High-volume tags (100k+ posts): Cast a wide net, ride popular conversations\n- Mid-volume tags (10k-100k): Sweet spot for appearing in top posts\n- Niche tags (<10k): Low competition, high chance of ranking at top\n\nYou never suggest banned, spam-flagged, or irrelevant hashtags.\n\nReturn ONLY valid JSON — no markdown, no commentary."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        hashtags_data = result.get('hashtags', [])

    except Exception as e:
        logger.error(f"Hashtag generation failed: {e}")
        return []

    # Clear existing hashtags for this platform
    PostHashtag.objects.filter(post=post, platform=platform).delete()

    # Create hashtag objects
    created = []
    for item in hashtags_data:
        tag = item.get('tag', '').strip().lstrip('#').lower()
        if not tag or tag in banned_tags:
            continue

        ht = PostHashtag.objects.create(
            post=post,
            platform=platform,
            tag=tag,
            tier=item.get('tier', 'mid_volume'),
            estimated_volume=item.get('estimated_volume', 0),
            is_selected=True,
        )
        created.append(ht)

    # Update post checklist
    post.update_checklist()
    return created
