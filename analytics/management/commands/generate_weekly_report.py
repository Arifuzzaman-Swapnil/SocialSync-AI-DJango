"""
Weekly Report Generator Management Command
- Aggregate weekly analytics
- LLM-generated recommendations
- Run Sunday midnight
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Max
from datetime import timedelta

from brands.models import Brand, WeeklyReport
from analytics.models import PostAnalytics, LearningSignal
from posts.models import Post


class Command(BaseCommand):
    help = 'Generate weekly reports for all active brands'

    def handle(self, *args, **options):
        now = timezone.now()
        period_end = now.date()
        period_start = period_end - timedelta(days=7)

        brands = Brand.objects.filter(workspace__is_active=True)
        generated = 0

        for brand in brands:
            # Check if report already exists for this period
            existing = WeeklyReport.objects.filter(
                brand=brand,
                period_start=period_start,
                period_end=period_end,
            ).exists()
            if existing:
                continue

            # Aggregate analytics for the week
            analytics = PostAnalytics.objects.filter(
                post__brand=brand,
                fetched_at__date__gte=period_start,
                fetched_at__date__lte=period_end,
            )

            posts = Post.objects.filter(
                brand=brand,
                posted_at__date__gte=period_start,
                posted_at__date__lte=period_end,
            )

            # Find winners (top 3 by engagement)
            winners = list(
                analytics.order_by('-engagement_rate').values(
                    'post_id', 'platform', 'engagement_rate', 'impressions', 'likes'
                )[:3]
            )

            # Find losers (bottom 3)
            losers = list(
                analytics.order_by('engagement_rate').values(
                    'post_id', 'platform', 'engagement_rate', 'impressions', 'likes'
                )[:3]
            )

            # Best hooks from winning posts
            winner_ids = [w['post_id'] for w in winners]
            best_hooks = list(
                Post.objects.filter(id__in=winner_ids).values_list('hook', flat=True)
            )

            # Pillar performance
            pillar_perf = {}
            for pillar in brand.content_pillars.filter(is_active=True):
                pillar_analytics = analytics.filter(post__pillar=pillar)
                agg = pillar_analytics.aggregate(
                    avg_engagement=Avg('engagement_rate'),
                    total_posts=Count('post_id', distinct=True),
                )
                pillar_perf[pillar.name] = {
                    'avg_engagement': round(agg['avg_engagement'] or 0, 2),
                    'total_posts': agg['total_posts'],
                    'target_percentage': pillar.target_percentage,
                }

            # Overall aggregates
            agg = analytics.aggregate(
                avg_engagement=Avg('engagement_rate'),
                total_impressions=Sum('impressions'),
                total_likes=Sum('likes'),
                total_shares=Sum('shares'),
            )

            data = {
                'total_posts': posts.count(),
                'avg_engagement_rate': round(agg['avg_engagement'] or 0, 2),
                'total_impressions': agg['total_impressions'] or 0,
                'total_likes': agg['total_likes'] or 0,
                'total_shares': agg['total_shares'] or 0,
            }

            report = WeeklyReport.objects.create(
                brand=brand,
                workspace=brand.workspace,
                period_start=period_start,
                period_end=period_end,
                data=data,
                winners=winners,
                losers=losers,
                best_hooks=[h for h in best_hooks if h],
                best_times={},  # Populated by best_time_service
                pillar_performance=pillar_perf,
                ab_test_results={},
                recommendations=[],  # Populated by LLM in production
                test_plan={},
            )

            # Extract learning signals from winners
            for w in winners:
                LearningSignal.objects.create(
                    brand=brand,
                    signal_type='best_hook',
                    reference_id=str(w['post_id']),
                    data_json=w,
                )

            generated += 1

        self.stdout.write(
            self.style.SUCCESS(f'Weekly reports generated: {generated} brands')
        )
