"""
SLA Escalation Management Command
- 12h → reminder to approver
- 24h → escalate to Owner + Admin
- 48h → flag as stale
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from posts.models import Post
from brands.models import ApprovalLog
from accounts.services.notification_service import notify_approval_reminder


class Command(BaseCommand):
    help = 'Check approval SLA and send escalation notifications'

    def handle(self, *args, **options):
        now = timezone.now()

        pending_posts = Post.objects.filter(
            status='pending_approval',
            submitted_at__isnull=False,
        ).select_related('user', 'brand__workspace__owner')

        escalated_12h = 0
        escalated_24h = 0
        flagged_stale = 0

        for post in pending_posts:
            hours_pending = (now - post.submitted_at).total_seconds() / 3600

            if hours_pending >= 48:
                # Flag as stale
                ApprovalLog.objects.get_or_create(
                    post=post,
                    action='escalated',
                    defaults={
                        'acted_by': post.user,
                        'comment': 'Auto-flagged: Approval pending for 48+ hours (stale)',
                    }
                )
                flagged_stale += 1

                if post.brand and post.brand.workspace:
                    notify_approval_reminder(post, post.brand.workspace.owner, int(hours_pending))

            elif hours_pending >= 24:
                # Escalate to owner + admin
                if post.brand and post.brand.workspace:
                    owner = post.brand.workspace.owner
                    # Only notify if we haven't already sent 24h escalation
                    existing = ApprovalLog.objects.filter(
                        post=post, action='escalated',
                        comment__contains='24h'
                    ).exists()
                    if not existing:
                        ApprovalLog.objects.create(
                            post=post,
                            action='escalated',
                            acted_by=post.user,
                            comment='Auto-escalation: Approval pending for 24+ hours',
                        )
                        notify_approval_reminder(post, owner, 24)
                        escalated_24h += 1

            elif hours_pending >= 12:
                # Reminder to approver
                existing = ApprovalLog.objects.filter(
                    post=post, action='escalated',
                    comment__contains='12h'
                ).exists()
                if not existing:
                    if post.brand and post.brand.workspace:
                        notify_approval_reminder(post, post.brand.workspace.owner, 12)
                        escalated_12h += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'SLA check complete: {escalated_12h} 12h reminders, '
                f'{escalated_24h} 24h escalations, {flagged_stale} stale flags'
            )
        )
