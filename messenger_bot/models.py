"""
Messenger Bot Models
Complete database models for AI-powered Facebook Messenger chatbot with RAG
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json
import secrets


class MessengerConnection(models.Model):
    """Facebook Messenger Page connection"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='messenger_connection'
    )
    
    # Facebook Page details
    page_id = models.CharField(max_length=255, unique=True)
    page_name = models.CharField(max_length=255)
    page_access_token = models.TextField()
    
    # Webhook configuration
    verify_token = models.CharField(
        max_length=255, 
        unique=True,
        default=secrets.token_urlsafe
    )
    webhook_url = models.URLField(blank=True, null=True)
    is_webhook_verified = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    auto_reply_enabled = models.BooleanField(default=True)
    
    # Greeting message
    greeting_text = models.TextField(
        default="Hi! I'm an AI assistant. How can I help you today?"
    )
    
    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messenger_connections'
        verbose_name = 'Messenger Connection'
        verbose_name_plural = 'Messenger Connections'
    
    def __str__(self):
        return f"{self.page_name} - {self.user.username}"


class AIConfiguration(models.Model):
    """OpenAI and AI service configuration"""
    
    connection = models.OneToOneField(
        MessengerConnection, 
        on_delete=models.CASCADE, 
        related_name='ai_config'
    )
    
    # OpenAI settings
    openai_api_key = models.CharField(max_length=255)
    openai_model = models.CharField(
        max_length=100,
        choices=[
            ('gpt-4o', 'GPT-4o (Best - Vision + Latest)'),
            ('gpt-4o-mini', 'GPT-4o Mini (Faster & Cheaper)'),
            ('gpt-4-turbo', 'GPT-4 Turbo'),
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo (Legacy)'),
        ],
        default='gpt-4o-mini'
    )
    
    # Embedding model for RAG
    embedding_model = models.CharField(
        max_length=100,
        choices=[
            ('text-embedding-3-small', 'Text Embedding 3 Small (Recommended)'),
            ('text-embedding-3-large', 'Text Embedding 3 Large'),
            ('text-embedding-ada-002', 'Ada 002 (Legacy)'),
        ],
        default='text-embedding-3-small'
    )
    
    # RAG settings
    rag_enabled = models.BooleanField(default=True)
    top_k_results = models.IntegerField(
        default=3,
        help_text="Number of relevant chunks to retrieve from knowledge base"
    )
    similarity_threshold = models.FloatField(
        default=0.7,
        help_text="Minimum similarity score (0-1) for RAG results"
    )
    
    # Response settings
    temperature = models.FloatField(
        default=0.7,
        help_text="Creativity (0-2). Lower = focused, Higher = creative"
    )
    max_tokens = models.IntegerField(
        default=500,
        help_text="Maximum response length"
    )
    
    # Image understanding
    image_understanding_enabled = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_configurations'
        verbose_name = 'AI Configuration'
        verbose_name_plural = 'AI Configurations'
    
    def __str__(self):
        return f"AI Config - {self.connection.page_name}"


class PDFKnowledgeBase(models.Model):
    """Uploaded PDFs for RAG knowledge base"""
    
    connection = models.ForeignKey(
        MessengerConnection, 
        on_delete=models.CASCADE, 
        related_name='pdfs'
    )
    
    # File details
    file = models.FileField(upload_to='messenger_bot/pdfs/%Y/%m/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="Size in bytes")
    
    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending Processing'),
        ('processing', 'Processing...'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Vectorization metadata
    total_chunks = models.IntegerField(default=0)
    total_pages = models.IntegerField(default=0)
    vectorized_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'pdf_knowledge_base'
        verbose_name = 'PDF Knowledge Base'
        verbose_name_plural = 'PDF Knowledge Bases'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} ({self.status})"
    
    @property
    def status_icon(self):
        """Returns emoji for status"""
        icons = {
            'pending': '⏳',
            'processing': '⚙️',
            'completed': '✅',
            'failed': '❌',
        }
        return icons.get(self.status, '❓')


class PDFChunk(models.Model):
    """Vectorized chunks of PDF content for RAG"""
    
    pdf = models.ForeignKey(
        PDFKnowledgeBase, 
        on_delete=models.CASCADE, 
        related_name='chunks'
    )
    
    # Content
    text = models.TextField()
    chunk_index = models.IntegerField()
    page_number = models.IntegerField(blank=True, null=True)
    
    # Vector embedding (stored as JSON array)
    embedding = models.TextField(
        help_text="JSON array of vector embeddings"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pdf_chunks'
        verbose_name = 'PDF Chunk'
        verbose_name_plural = 'PDF Chunks'
        ordering = ['chunk_index']
        indexes = [
            models.Index(fields=['pdf', 'chunk_index']),
        ]
    
    def __str__(self):
        return f"Chunk {self.chunk_index} - {self.pdf.filename}"
    
    def get_embedding(self):
        """Returns embedding as list of floats"""
        return json.loads(self.embedding)
    
    def set_embedding(self, embedding_list):
        """Stores embedding as JSON"""
        self.embedding = json.dumps(embedding_list)


class CustomPrompt(models.Model):
    """Custom system prompts for AI personality and behavior"""
    
    connection = models.ForeignKey(
        MessengerConnection, 
        on_delete=models.CASCADE, 
        related_name='prompts'
    )
    
    # Prompt details
    name = models.CharField(max_length=255)
    system_prompt = models.TextField(
        help_text="Define AI personality, role, and behavior",
        default="""You are a helpful AI assistant for a business. 
You have access to company documents and product information through a knowledge base.
Provide accurate, professional, and friendly responses based on the available knowledge.
If you don't know something, politely say so and offer to help in another way.
Keep responses concise and helpful."""
    )
    
    # Behavior settings
    tone = models.CharField(
        max_length=50,
        choices=[
            ('professional', 'Professional'),
            ('casual', 'Casual & Friendly'),
            ('friendly', 'Warm & Friendly'),
            ('technical', 'Technical & Detailed'),
            ('sales', 'Sales-Oriented'),
            ('support', 'Customer Support'),
        ],
        default='friendly'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Only one prompt can be active at a time"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'custom_prompts'
        verbose_name = 'Custom Prompt'
        verbose_name_plural = 'Custom Prompts'
        ordering = ['-created_at']
    
    def __str__(self):
        active = "✅" if self.is_active else "⭕"
        return f"{active} {self.name} - {self.get_tone_display()}"
    
    def save(self, *args, **kwargs):
        """Ensure only one active prompt per connection"""
        if self.is_active:
            # Deactivate other prompts for this connection
            CustomPrompt.objects.filter(
                connection=self.connection, 
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Conversation(models.Model):
    """Individual user conversations"""
    
    connection = models.ForeignKey(
        MessengerConnection, 
        on_delete=models.CASCADE, 
        related_name='conversations'
    )
    
    # Facebook user details
    sender_id = models.CharField(max_length=255, db_index=True)
    sender_name = models.CharField(max_length=255, blank=True, null=True)
    sender_profile_pic = models.URLField(blank=True, null=True)
    
    # Conversation metadata
    started_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    message_count = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['connection', 'sender_id']),
        ]
    
    def __str__(self):
        return f"{self.sender_name or self.sender_id} ({self.message_count} messages)"


class Message(models.Model):
    """Individual messages in conversations"""
    
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    
    # Message type
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('sticker', 'Sticker'),
        ('quick_reply', 'Quick Reply'),
    ]
    message_type = models.CharField(
        max_length=20, 
        choices=MESSAGE_TYPE_CHOICES, 
        default='text'
    )
    
    # Sender
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    
    # Content
    text = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    
    # AI metadata (for bot messages)
    rag_context_used = models.TextField(
        blank=True, 
        null=True,
        help_text="Retrieved context from RAG"
    )
    prompt_used = models.TextField(blank=True, null=True)
    model_used = models.CharField(max_length=100, blank=True, null=True)
    tokens_used = models.IntegerField(default=0)
    processing_time = models.FloatField(
        default=0.0, 
        help_text="Processing time in seconds"
    )
    
    # Image understanding (for user images)
    image_description = models.TextField(blank=True, null=True)
    
    # Timestamps
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Delivery status
    delivered = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
        ]
    
    def __str__(self):
        preview = self.text[:50] if self.text else self.message_type
        return f"{self.sender}: {preview}"
    
    @property
    def sender_icon(self):
        """Returns emoji for sender"""
        return "👤" if self.sender == 'user' else "🤖"