from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Workspace(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspaces')
    name = models.CharField(max_length=200)
    timezone = models.CharField(max_length=50, default='UTC')
    team_size = models.IntegerField(null=True, blank=True)
    default_language = models.CharField(max_length=10, default='en')
    max_generations_per_day = models.IntegerField(default=200)
    generations_today = models.IntegerField(default=0)
    generation_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workspaces'
        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    def reset_daily_generations(self):
        today = timezone.now().date()
        if self.generation_date != today:
            self.generations_today = 0
            self.generation_date = today
            self.save()

    def can_generate(self):
        self.reset_daily_generations()
        return self.generations_today < self.max_generations_per_day

    def increment_generation(self, count=1):
        self.reset_daily_generations()
        self.generations_today += count
        self.save()


class Brand(models.Model):
    GOAL_CHOICES = [
        ('leads', 'Lead Generation'),
        ('growth', 'Audience Growth'),
        ('authority', 'Thought Leadership / Authority'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='brands')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='brands')

    # Basic Info
    brand_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=200)
    target_region = models.CharField(max_length=200)
    website_url = models.URLField(blank=True, null=True)
    social_links = models.JSONField(default=dict, blank=True)

    # Brand Assets
    logo = models.ImageField(upload_to='brands/logos/', blank=True, null=True)
    brand_guide_pdf = models.FileField(upload_to='brands/guides/', blank=True, null=True)

    # Voice & Tone
    voice_tone = models.CharField(max_length=100, default='professional')
    do_dont_rules = models.JSONField(default=dict, blank=True)

    # Goals & Audiences
    goals = models.JSONField(default=list, blank=True)
    audiences = models.JSONField(default=list, blank=True)

    # Brand DNA (generated in Step 5)
    brand_dna = models.JSONField(default=dict, blank=True)
    brand_dna_generated_at = models.DateTimeField(null=True, blank=True)
    brand_dna_source = models.CharField(
        max_length=20, blank=True,
        choices=[('website', 'Website Crawl'), ('pdf', 'Brand Guide PDF'), ('manual', 'Manual')]
    )

    is_primary = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return f"{self.brand_name} ({self.workspace.name})"


class BrandAsset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('logo', 'Logo'),
        ('icon', 'Icon'),
        ('banner', 'Banner'),
        ('font', 'Font File'),
        ('color_palette', 'Color Palette'),
        ('template', 'Template'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to='brands/assets/')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'brand_assets'
        verbose_name = 'Brand Asset'
        verbose_name_plural = 'Brand Assets'

    def __str__(self):
        return f"{self.brand.brand_name} - {self.name}"


class LaunchPlan(models.Model):
    VARIANT_LEVEL_CHOICES = [
        ('off', 'Off'),
        ('low', 'Low (1 variant)'),
        ('medium', 'Medium (2 variants)'),
        ('high', 'High (3 variants)'),
    ]

    brand = models.OneToOneField(Brand, on_delete=models.CASCADE, related_name='launch_plan')
    post_frequency = models.IntegerField(default=3, help_text='Posts per week')
    formats_allowed = models.JSONField(default=list, blank=True)
    variant_generation_level = models.CharField(
        max_length=10, choices=VARIANT_LEVEL_CHOICES, default='medium'
    )
    approval_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'launch_plans'
        verbose_name = 'Launch Plan'
        verbose_name_plural = 'Launch Plans'

    def __str__(self):
        return f"Launch Plan - {self.brand.brand_name}"


class ContentIdea(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('saved', 'Saved'),
        ('skipped', 'Skipped'),
        ('drafted', 'Converted to Draft'),
        ('scheduled', 'Linked to Calendar'),
    ]

    FORMAT_CHOICES = [
        ('text', 'Text Post'),
        ('image', 'Image Post'),
        ('video', 'Video'),
        ('carousel', 'Carousel'),
        ('reel', 'Reel/Short'),
        ('thread', 'Thread'),
        ('story', 'Story'),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='content_ideas')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_ideas')
    title = models.CharField(max_length=300)
    hook = models.TextField(blank=True)
    angle = models.CharField(max_length=300, blank=True)
    platform = models.CharField(max_length=20, blank=True)
    goal = models.CharField(max_length=20, blank=True)
    content_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='text')
    language = models.CharField(max_length=10, default='en')
    persona = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    post = models.ForeignKey(
        'posts.Post', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='source_ideas'
    )
    batch_id = models.CharField(max_length=50, blank=True)
    generation_run = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content_ideas'
        verbose_name = 'Content Idea'
        verbose_name_plural = 'Content Ideas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title[:50]} ({self.status})"


class ContentApproval(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('changes_requested', 'Changes Requested'),
        ('rejected', 'Rejected'),
    ]

    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='approvals')
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='submitted_approvals'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    approver = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_approvals'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    compliance_checklist = models.JSONField(default=dict, blank=True)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content_approvals'
        verbose_name = 'Content Approval'
        verbose_name_plural = 'Content Approvals'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Approval for Post #{self.post.id} - {self.status}"


class WeeklyReport(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='weekly_reports')
    period_start = models.DateField()
    period_end = models.DateField()
    data = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weekly_reports'
        verbose_name = 'Weekly Report'
        verbose_name_plural = 'Weekly Reports'
        ordering = ['-period_end']
        unique_together = ['brand', 'period_start']

    def __str__(self):
        return f"Report: {self.brand.brand_name} ({self.period_start} - {self.period_end})"


class GenerationUsage(models.Model):
    GENERATION_TYPES = [
        ('idea', 'Idea Generation'),
        ('caption', 'Caption Generation'),
        ('image', 'Image Generation'),
        ('video', 'Video Generation'),
        ('brand_dna', 'Brand DNA Generation'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='generation_usage')
    generation_type = models.CharField(max_length=20, choices=GENERATION_TYPES)
    date = models.DateField()
    count = models.IntegerField(default=0)

    class Meta:
        db_table = 'generation_usage'
        unique_together = ['workspace', 'generation_type', 'date']

    def __str__(self):
        return f"{self.workspace.name} - {self.generation_type}: {self.count} ({self.date})"

    @classmethod
    def increment(cls, workspace, gen_type, amount=1):
        today = timezone.now().date()
        obj, _ = cls.objects.get_or_create(
            workspace=workspace,
            generation_type=gen_type,
            date=today,
            defaults={'count': 0}
        )
        obj.count += amount
        obj.save()
        return obj.count


class BrandDNAChunk(models.Model):
    """Vectorized chunks of website content for Brand DNA RAG"""

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='dna_chunks')
    text = models.TextField()
    chunk_index = models.IntegerField()
    source_url = models.URLField(max_length=2000)
    page_title = models.CharField(max_length=500, blank=True)
    embedding = models.TextField(help_text="JSON array of vector embeddings")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'brand_dna_chunks'
        verbose_name = 'Brand DNA Chunk'
        verbose_name_plural = 'Brand DNA Chunks'
        ordering = ['chunk_index']
        indexes = [
            models.Index(fields=['brand', 'chunk_index']),
        ]

    def __str__(self):
        return f"Chunk {self.chunk_index} - {self.brand.brand_name}"

    def get_embedding(self):
        """Returns embedding as list of floats"""
        import json
        return json.loads(self.embedding)

    def set_embedding(self, embedding_list):
        """Stores embedding as JSON"""
        import json
        self.embedding = json.dumps(embedding_list)
