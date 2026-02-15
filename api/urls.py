from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import admin_views

# Create router for viewsets
router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'platforms', views.SocialAccountViewSet, basename='platform')
router.register(r'platforms-detail', views.SocialAccountDetailViewSet, basename='platform-detail')

# AI Caption routers
router.register(r'ai-caption/templates', views.CaptionTemplateViewSet, basename='caption-template')
router.register(r'ai-caption/saved', views.SavedCaptionViewSet, basename='saved-caption')

# AI Image routers
router.register(r'ai-image/logos', views.UserLogoViewSet, basename='user-logo')
router.register(r'ai-image/saved', views.SavedImageViewSet, basename='saved-image')
router.register(r'ai-image/templates', views.ImagePromptTemplateViewSet, basename='image-template')

# AI Video routers
router.register(r'ai-video/logos', views.VideoLogoViewSet, basename='video-logo')
router.register(r'ai-video/saved', views.SavedVideoViewSet, basename='saved-video')
router.register(r'ai-video/templates', views.VideoPromptTemplateViewSet, basename='video-template')

# Messenger routers
router.register(r'messenger/connections', views.MessengerConnectionViewSet, basename='messenger-connection')
router.register(r'messenger/notifications', views.NotificationViewSet, basename='notification')

# Onboarding & Brands routers
router.register(r'workspaces', views.WorkspaceViewSet, basename='workspace')
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'brand-assets', views.BrandAssetViewSet, basename='brand-asset')
router.register(r'content-ideas', views.ContentIdeaViewSet, basename='content-idea')
router.register(r'content-approvals', views.ContentApprovalViewSet, basename='content-approval')
router.register(r'weekly-reports', views.WeeklyReportViewSet, basename='weekly-report')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.RegisterView.as_view(), name='api-register'),
    path('auth/login/', views.LoginView.as_view(), name='api-login'),
    path('auth/logout/', views.LogoutView.as_view(), name='api-logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('auth/me/', views.CurrentUserView.as_view(), name='api-current-user'),

    # User Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='api-profile'),
    path('profile/api-keys/', views.GlobalAPIKeysView.as_view(), name='api-global-keys'),

    # Dashboard endpoints
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='api-dashboard-stats'),
    path('dashboard/recent/', views.RecentPostsView.as_view(), name='api-recent-posts'),

    # Onboarding endpoints
    path('onboarding/', views.OnboardingProgressView.as_view(), name='api-onboarding'),
    path('onboarding/step/<int:step_number>/', views.OnboardingStepView.as_view(), name='api-onboarding-step'),
    path('onboarding/skip/', views.OnboardingSkipView.as_view(), name='api-onboarding-skip'),

    # Launch Plan endpoints
    path('brands/<int:brand_id>/launch-plan/', views.LaunchPlanView.as_view(), name='api-launch-plan'),
    path('launch-plans/', views.CreateLaunchPlanView.as_view(), name='api-create-launch-plan'),

    # Generation Usage endpoints
    path('generation-usage/', views.GenerationUsageView.as_view(), name='api-generation-usage'),

    # AI Caption endpoints
    path('ai-caption/generate/', views.generate_caption, name='api-generate-caption'),
    path('ai-caption/regenerate/<int:pk>/', views.regenerate_caption, name='api-regenerate-caption'),
    path('ai-caption/history/', views.CaptionHistoryView.as_view(), name='api-caption-history'),
    path('ai-caption/settings/', views.CaptionAPISettingsView.as_view(), name='api-caption-settings'),

    # AI Image endpoints
    path('ai-image/generate/', views.generate_image, name='api-generate-image'),
    path('ai-image/history/', views.ImageGenerationHistoryView.as_view(), name='api-image-history'),
    path('ai-image/settings/', views.ImageSettingsView.as_view(), name='api-image-settings'),

    # AI Video endpoints
    path('ai-video/generate/', views.generate_video, name='api-generate-video'),
    path('ai-video/history/', views.VideoGenerationHistoryView.as_view(), name='api-video-history'),
    path('ai-video/settings/', views.VideoSettingsView.as_view(), name='api-video-settings'),

    # AI Voice endpoints
    path('ai-voice/generate/', views.generate_voice, name='api-generate-voice'),
    path('ai-voice/preview/', views.preview_voice, name='api-preview-voice'),
    path('ai-voice/history/', views.VoiceGenerationHistoryView.as_view(), name='api-voice-history'),
    path('ai-voice/settings/', views.VoiceSettingsView.as_view(), name='api-voice-settings'),
    path('ai-voice/generation/<int:generation_id>/', views.get_voice_generation, name='api-voice-generation'),
    path('ai-voice/generation/<int:generation_id>/delete/', views.delete_voice_generation, name='api-voice-delete'),
    path('ai-voice/generation/<int:generation_id>/regenerate/', views.regenerate_voice, name='api-voice-regenerate'),

    # Messenger Bot endpoints
    path('messenger/dashboard/', views.MessengerDashboardView.as_view(), name='api-messenger-dashboard'),
    path('messenger/connections/<int:connection_id>/config/', views.AIConfigurationView.as_view(), name='api-ai-config'),
    path('messenger/connections/<int:connection_id>/pdfs/', views.PDFKnowledgeBaseViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='api-pdf-list'),
    path('messenger/connections/<int:connection_id>/pdfs/<int:pk>/', views.PDFKnowledgeBaseViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy',
    }), name='api-pdf-detail'),
    path('messenger/connections/<int:connection_id>/conversations/', views.ConversationViewSet.as_view({
        'get': 'list',
    }), name='api-conversations'),
    path('messenger/connections/<int:connection_id>/conversations/<int:pk>/', views.ConversationViewSet.as_view({
        'get': 'retrieve',
    }), name='api-conversation-detail'),
    path('messenger/connections/<int:connection_id>/conversations/<int:pk>/toggle-takeover/', views.ConversationViewSet.as_view({
        'post': 'toggle_takeover',
    }), name='api-conversation-takeover'),
    path('messenger/connections/<int:connection_id>/conversations/<int:pk>/send-message/', views.ConversationViewSet.as_view({
        'post': 'send_message',
    }), name='api-conversation-send'),
    path('messenger/connections/<int:connection_id>/prompts/', views.CustomPromptViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='api-prompts'),
    path('messenger/connections/<int:connection_id>/prompts/<int:pk>/', views.CustomPromptViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy',
    }), name='api-prompt-detail'),
    path('messenger/connections/<int:connection_id>/prompts/<int:pk>/activate/', views.CustomPromptViewSet.as_view({
        'post': 'activate',
    }), name='api-prompt-activate'),
    path('messenger/connections/<int:connection_id>/crawl-website/', views.CrawlWebsiteView.as_view(), name='api-crawl-website'),

    # E-Commerce endpoints
    path('messenger/connections/<int:connection_id>/ecommerce/', views.ECommerceSettingsView.as_view(), name='api-ecommerce-settings'),
    path('messenger/connections/<int:connection_id>/ecommerce/test/', views.TestECommerceConnectionView.as_view(), name='api-ecommerce-test'),
    path('messenger/connections/<int:connection_id>/ecommerce/sync/', views.SyncProductsView.as_view(), name='api-ecommerce-sync'),
    path('messenger/connections/<int:connection_id>/ecommerce/embeddings/', views.RegenerateEmbeddingsView.as_view(), name='api-ecommerce-embeddings'),
    path('messenger/connections/<int:connection_id>/ecommerce/products/', views.ProductListView.as_view(), name='api-ecommerce-products'),

    # Brand DNA endpoints
    path('brands/<int:brand_id>/generate-dna/', views.GenerateBrandDNAView.as_view(), name='api-generate-brand-dna'),
    path('brands/<int:brand_id>/dna-status/', views.BrandDNAStatusView.as_view(), name='api-brand-dna-status'),

    # Analytics endpoints
    path('analytics/summary/', views.AnalyticsSummaryView.as_view(), name='api-analytics-summary'),
    path('analytics/platforms/', views.PlatformAnalyticsView.as_view(), name='api-analytics-platforms'),
    path('analytics/trends/', views.AnalyticsTrendView.as_view(), name='api-analytics-trends'),
    path('analytics/top-posts/', views.TopPostsView.as_view(), name='api-top-posts'),

    # Support Chat
    path('support-chat/', views.SupportChatView.as_view(), name='api-support-chat'),

    # Admin Panel API
    path('admin/dashboard/', admin_views.AdminDashboardView.as_view(), name='api-admin-dashboard'),
    path('admin/users/', admin_views.AdminUserListView.as_view(), name='api-admin-users'),
    path('admin/users/<int:user_id>/', admin_views.AdminUserDetailView.as_view(), name='api-admin-user-detail'),
    path('admin/users/<int:user_id>/approve/', admin_views.AdminApproveUserView.as_view(), name='api-admin-approve'),
    path('admin/users/<int:user_id>/reject/', admin_views.AdminRejectUserView.as_view(), name='api-admin-reject'),
    path('admin/users/<int:user_id>/plan/', admin_views.AdminUpdatePlanView.as_view(), name='api-admin-plan'),
    path('admin/users/<int:user_id>/api-settings/', admin_views.AdminAPISettingsView.as_view(), name='api-admin-api-settings'),
    path('admin/users/<int:user_id>/posts/', admin_views.AdminUserPostsView.as_view(), name='api-admin-user-posts'),
    path('admin/users/<int:user_id>/accounts/', admin_views.AdminUserAccountsView.as_view(), name='api-admin-user-accounts'),
    path('admin/users/<int:user_id>/captions/', admin_views.AdminUserCaptionsView.as_view(), name='api-admin-user-captions'),
    path('admin/users/<int:user_id>/images/', admin_views.AdminUserImagesView.as_view(), name='api-admin-user-images'),
    path('admin/users/<int:user_id>/videos/', admin_views.AdminUserVideosView.as_view(), name='api-admin-user-videos'),
    path('admin/users/<int:user_id>/messenger/', admin_views.AdminUserMessengerView.as_view(), name='api-admin-user-messenger'),
    path('admin/conversations/<int:conv_id>/messages/', admin_views.AdminConversationMessagesView.as_view(), name='api-admin-conv-messages'),
    path('admin/analytics/', admin_views.AdminAnalyticsView.as_view(), name='api-admin-analytics'),
    path('admin/bulk-approve/', admin_views.AdminBulkApproveView.as_view(), name='api-admin-bulk-approve'),

    # ViewSet routes
    path('', include(router.urls)),
]
