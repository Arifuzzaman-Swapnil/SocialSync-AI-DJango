"""
OpenAI Service for Caption Generation
"""
import openai
from django.conf import settings
import base64
import os


class OpenAIService:
    
    @staticmethod
    def generate_caption_from_text(topic, tone='professional', length='medium'):
        """
        Generate caption from text using GPT-4
        
        Args:
            topic: Topic or keywords
            tone: professional, casual, friendly, enthusiastic
            length: short, medium, long
        """
        try:
            # Set API key
            openai.api_key = settings.OPENAI_API_KEY
            
            # Define length
            word_counts = {
                'short': '20-40 words',
                'medium': '40-80 words',
                'long': '80-120 words'
            }
            
            # Create prompt
            prompt = f"""Create a social media caption about: {topic}

Tone: {tone}
Length: {word_counts.get(length, '40-80 words')}

Requirements:
- Engaging and authentic
- Include relevant hashtags (3-5)
- Call to action at the end
- Professional formatting

Generate only the caption text, no explanations."""
            
            # Call GPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert social media content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            caption = response.choices[0].message.content.strip()
            return True, caption
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def generate_caption_from_image(image_path, additional_context=""):
        """
        Generate caption from image using GPT-4 Vision
        
        Args:
            image_path: Path to image file
            additional_context: Optional context about the image
        """
        try:
            # Set API key
            openai.api_key = settings.OPENAI_API_KEY
            
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Get file extension
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            # Create prompt
            prompt = f"""Analyze this image and create an engaging social media caption.

{f'Context: {additional_context}' if additional_context else ''}

Requirements:
- Describe what you see
- Create engaging copy (40-80 words)
- Include relevant hashtags (3-5)
- Add a call to action
- Professional and authentic tone

Generate only the caption text."""
            
            # Call GPT-4 Vision
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            caption = response.choices[0].message.content.strip()
            return True, caption
            
        except Exception as e:
            return False, f"Error: {str(e)}"