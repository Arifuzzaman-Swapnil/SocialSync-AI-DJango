# messenger_bot/services/message_handler.py

"""
Message Handler Service
Processes incoming messages and generates AI responses
"""

import logging
import requests
import time
from django.utils import timezone
from ..models import MessengerConnection, Conversation, Message
from .rag_engine import RAGEngine

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Handles incoming Facebook Messenger messages
    """
    
    def __init__(self, connection: MessengerConnection):
        """
        Initialize message handler
        
        Args:
            connection: MessengerConnection instance
        """
        self.connection = connection
        self.page_access_token = connection.page_access_token
        self.rag_engine = RAGEngine(connection.ai_config) if hasattr(connection, 'ai_config') else None
    
    def process_message(self, sender_id: str, message_text: str, message_id: str = None):
        """
        Process incoming message and generate response
        
        Args:
            sender_id: Facebook user ID
            message_text: Message text from user
            message_id: Facebook message ID
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Processing message from {sender_id}: {message_text}")
            
            # Get or create conversation
            conversation = self._get_or_create_conversation(sender_id)
            
            # Save user message
            user_message = Message.objects.create(
                conversation=conversation,
                sender='user',
                message_type='text',
                text=message_text,
                timestamp=timezone.now()
            )
            
            # Update conversation
            conversation.message_count += 1
            conversation.last_message_at = timezone.now()
            conversation.save()
            
            # Check if auto-reply is enabled
            if not self.connection.auto_reply_enabled:
                logger.info("Auto-reply is disabled")
                return True
            
            # Generate AI response
            start_time = time.time()
            response_data = self._generate_response(message_text, conversation)
            processing_time = time.time() - start_time
            
            # Save bot message
            bot_message = Message.objects.create(
                conversation=conversation,
                sender='bot',
                message_type='text',
                text=response_data['response'],
                model_used=response_data.get('model'),
                tokens_used=response_data.get('tokens', 0),
                processing_time=processing_time,
                rag_context_used=response_data.get('context_used', ''),
                timestamp=timezone.now()
            )
            
            # Update conversation
            conversation.message_count += 1
            conversation.save()
            
            # Send response to Facebook
            success = self._send_facebook_message(sender_id, response_data['response'])
            
            if success:
                bot_message.delivered = True
                bot_message.save()
                logger.info(f"Response sent successfully to {sender_id}")
            else:
                bot_message.failed = True
                bot_message.error_message = "Failed to send to Facebook"
                bot_message.save()
                logger.error(f"Failed to send response to {sender_id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    def _get_or_create_conversation(self, sender_id: str) -> Conversation:
        """
        Get existing conversation or create new one
        
        Args:
            sender_id: Facebook user ID
            
        Returns:
            Conversation instance
        """
        conversation, created = Conversation.objects.get_or_create(
            connection=self.connection,
            sender_id=sender_id,
            defaults={
                'is_active': True,
                'message_count': 0
            }
        )
        
        if created:
            # Try to get user info from Facebook
            user_info = self._get_facebook_user_info(sender_id)
            if user_info:
                conversation.sender_name = user_info.get('name')
                conversation.sender_profile_pic = user_info.get('profile_pic')
                conversation.save()
        
        return conversation
    
    def _get_facebook_user_info(self, user_id: str) -> dict:
        """
        Get user information from Facebook API
        
        Args:
            user_id: Facebook user ID
            
        Returns:
            dict with user info or empty dict
        """
        try:
            print(f"🔍 Attempting to get user info for: {user_id}")
            print(f"🔑 Token exists: {bool(self.page_access_token)}")
            print(f"🔑 Token length: {len(self.page_access_token) if self.page_access_token else 0}")
            
            if not self.page_access_token:
                print("❌ No page access token available!")
                return {}
            
            url = f"https://graph.facebook.com/v18.0/{user_id}"
            params = {
                'fields': 'name,profile_pic',
                'access_token': self.page_access_token
            }
            
            print(f"📡 Making API call to: {url}")
            response = requests.get(url, params=params, timeout=10)
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User info retrieved: {data}")
                return data
            else:
                print(f"❌ Failed to get user info: {response.text}")
                return {}
        
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _generate_response(self, message_text: str, conversation: Conversation) -> dict:
        """
        Generate AI response using RAG
        
        Args:
            message_text: User's message
            conversation: Conversation instance
            
        Returns:
            dict with response and metadata
        """
        try:
            if self.rag_engine:
                # Get conversation history (last 5 messages)
                recent_messages = Message.objects.filter(
                    conversation=conversation
                ).order_by('-timestamp')[:5]
                
                history = []
                for msg in reversed(recent_messages):
                    role = 'user' if msg.sender == 'user' else 'assistant'
                    history.append({
                        'role': role,
                        'content': msg.text
                    })
                
                # Generate response with RAG
                response_data = self.rag_engine.generate_response(
                    query=message_text,
                    connection=self.connection,
                    conversation_history=history[:-1]  # Exclude current message
                )
                
                return response_data
            else:
                # Fallback: Simple response without RAG
                return {
                    'response': self.connection.greeting_text or "Hi! I'm an AI assistant. How can I help you?",
                    'model': 'none',
                    'tokens': 0,
                    'context_used': ''
                }
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'response': "I'm sorry, I encountered an error. Please try again.",
                'model': 'error',
                'tokens': 0,
                'context_used': '',
                'error': str(e)
            }
    
    def _send_facebook_message(self, recipient_id: str, message_text: str) -> bool:
        """
        Send message to Facebook user
        
        Args:
            recipient_id: Facebook user ID
            message_text: Message to send
            
        Returns:
            bool: Success status
        """
        try:
            url = "https://graph.facebook.com/v18.0/me/messages"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                'recipient': {'id': recipient_id},
                'message': {'text': message_text},
                'messaging_type': 'RESPONSE'
            }
            
            params = {
                'access_token': self.page_access_token
            }
            
            response = requests.post(
                url,
                json=data,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully: {response.json()}")
                return True
            else:
                logger.error(f"Failed to send message: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending Facebook message: {e}")
            return False