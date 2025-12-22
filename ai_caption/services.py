"""
AI Caption Generator
Simple template-based caption generator
Can be replaced with OpenAI API later
"""

import random
"""
AI Caption Generation Service
"""
from .openai_service import OpenAIService


def generate_ai_caption(topic, tone='professional', length='medium', image_path=None):
    """
    Generate AI caption using OpenAI
    
    Args:
        topic: Topic or keywords
        tone: professional, casual, friendly, enthusiastic
        length: short, medium, long
        image_path: Optional path to image for vision-based caption
    """
    
    # If image provided, use vision
    if image_path:
        success, result = OpenAIService.generate_caption_from_image(
            image_path,
            additional_context=topic
        )
    else:
        # Text-based caption
        success, result = OpenAIService.generate_caption_from_text(
            topic,
            tone,
            length
        )
    
    return result if success else f"Error generating caption: {result}"

def get_professional_line():
    """Get professional closing line"""
    lines = [
        "Looking forward to your thoughts.",
        "Let me know what you think.",
        "Your feedback is valuable.",
        "Happy to discuss further.",
        "Interested in your perspective.",
    ]
    return random.choice(lines)


def get_casual_line():
    """Get casual closing line"""
    lines = [
        "What do you think?",
        "Let me know! 💬",
        "Drop your thoughts below!",
        "Would love to hear from you!",
        "Tell me in the comments!",
    ]
    return random.choice(lines)


def get_friendly_line():
    """Get friendly closing line"""
    lines = [
        "Would love to hear your thoughts! 😊",
        "Let's chat about it in the comments!",
        "What's your take on this?",
        "Share your experience below! 👇",
        "Looking forward to connecting!",
    ]
    return random.choice(lines)


def get_enthusiastic_line():
    """Get enthusiastic closing line"""
    lines = [
        "Can't wait to hear what you think! 🎉",
        "This is going to be AMAZING! 💪",
        "Let's make this happen! 🚀",
        "Who's with me?! 🙌",
        "Drop a comment if you agree! 🔥",
    ]
    return random.choice(lines)


def get_additional_content(topic):
    """Get additional content for long posts"""
    contents = [
        f"Here are 3 key takeaways about {topic}:\n• Point 1\n• Point 2\n• Point 3",
        f"Why {topic} matters:\nIt's transforming the way we work and live.",
        f"My experience with {topic} has been eye-opening. Here's what I learned.",
        f"If you're interested in {topic}, here's what you need to know.",
    ]
    return random.choice(contents)


def generate_hashtags(topic):
    """Generate relevant hashtags"""
    # Clean topic
    topic_words = topic.lower().replace(' ', '').replace('-', '')
    
    # Common hashtags
    common = ['#socialmedia', '#marketing', '#digitalmarketing', '#contentcreation', '#business']
    
    # Topic-specific
    specific = f'#{topic_words}'
    
    # Combine
    hashtags = [specific] + random.sample(common, 3)
    
    return ' '.join(hashtags)