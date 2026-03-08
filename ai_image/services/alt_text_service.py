"""
Alt Text Generation Service
- LLM vision-based alt text generation
- Max 125 characters for accessibility compliance
"""
import logging

from accounts.services.llm_service import get_llm_service, UnifiedLLMService

logger = logging.getLogger(__name__)

MAX_ALT_TEXT_LENGTH = 125


def generate_alt_text(image_generation, api_key=None, user=None, think_harder=False):
    """Generate accessibility alt text for an image using LLM vision.

    Args:
        image_generation: ImageGeneration model instance
        api_key: OpenAI API key (legacy, used as fallback)
        user: Django user instance (preferred — uses unified LLM service)

    Returns:
        str: Generated alt text (max 125 chars)
    """
    # Build the LLM service: prefer user-based, fall back to raw key
    if user:
        service = get_llm_service(user)
    elif api_key:
        from accounts.api_keys import get_claude_key
        service = UnifiedLLMService(openai_key=api_key, claude_key=get_claude_key())
    else:
        return _fallback_alt_text(image_generation)

    # Build context from the image's prompt and title
    context = f"Image title: {image_generation.title or 'Untitled'}\n"
    context += f"Generation prompt: {image_generation.prompt or ''}\n"
    if image_generation.style:
        context += f"Style: {image_generation.style}"

    prompt = f"""<task>
Generate accessible alt text for an image.
</task>

<context>
{context}
</context>

<rules>
- Maximum {MAX_ALT_TEXT_LENGTH} characters (strict limit)
- Start with the most important visual element
- Be specific: "Woman presenting quarterly sales chart to four colleagues" not "People in a meeting"
- Include relevant colors, text, or branding only if meaningful
- Return ONLY the alt text string — no quotes, no labels
</rules>"""

    try:
        messages = [
            {"role": "system", "content": "You are a web accessibility specialist who writes alt text that meets WCAG 2.1 guidelines. Your alt text is concise, descriptive, and useful for screen reader users who cannot see the image.\n\nYour alt text:\n- Describes the CONTENT and FUNCTION of the image\n- Prioritizes the most important visual information first\n- Uses specific, concrete language\n- Stays under 125 characters\n- Never starts with \"Image of,\" \"Photo of,\" or \"Picture of\"\n- Conveys the same information a sighted user would get from the image"},
            {"role": "user", "content": prompt}
        ]

        result = service.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=300 if think_harder else 150,
            thinking_budget=10000 if think_harder else 0,
        )

        if not result.success:
            raise Exception(result.error)

        alt_text = result.content.strip().strip('"')

        # Enforce character limit
        if len(alt_text) > MAX_ALT_TEXT_LENGTH:
            alt_text = alt_text[:MAX_ALT_TEXT_LENGTH - 3] + '...'

    except Exception as e:
        logger.error(f"Alt text generation failed: {e}")
        return _fallback_alt_text(image_generation)

    # Save to model
    image_generation.alt_text = alt_text
    image_generation.save(update_fields=['alt_text'])

    return alt_text


def _fallback_alt_text(image_generation):
    """Generate basic alt text from available metadata."""
    parts = []
    if image_generation.title:
        parts.append(image_generation.title)
    if image_generation.style:
        parts.append(f"{image_generation.style} style")

    alt_text = ', '.join(parts) if parts else 'Generated image'
    if len(alt_text) > MAX_ALT_TEXT_LENGTH:
        alt_text = alt_text[:MAX_ALT_TEXT_LENGTH - 3] + '...'

    image_generation.alt_text = alt_text
    image_generation.save(update_fields=['alt_text'])
    return alt_text
