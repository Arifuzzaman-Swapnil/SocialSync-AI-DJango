"""
Centralized Notification Service
- Create notifications for all system events
- Handles in-app and email channels
"""
import logging

from accounts.models import SystemNotification

logger = logging.getLogger(__name__)


def notify(user, event_type, title, message='', data_json=None, channel='in_app'):
    """Create a system notification for a user.

    Args:
        user: User model instance
        event_type: One of SystemNotification.EVENT_TYPE_CHOICES
        title: Notification title (max 200 chars)
        message: Optional notification body
        data_json: Optional dict of additional data
        channel: 'in_app', 'email', or 'both'

    Returns:
        SystemNotification instance
    """
    if data_json is None:
        data_json = {}

    notification = SystemNotification.objects.create(
        user=user,
        event_type=event_type,
        title=title,
        message=message,
        data_json=data_json,
        channel=channel,
    )

    # If channel includes email, trigger email (stub for now)
    if channel in ('email', 'both'):
        _send_email_notification(user, title, message)

    logger.info(f"Notification created: {event_type} for {user.username}")
    return notification


def notify_post_submitted(post, submitted_by):
    """Notify relevant users when a post is submitted for approval."""
    # Notify workspace owner/admins
    if post.brand and post.brand.workspace:
        owner = post.brand.workspace.owner
        if owner != submitted_by:
            notify(
                user=owner,
                event_type='post_submitted',
                title=f'Post submitted for approval',
                message=f'{submitted_by.username} submitted a post for review.',
                data_json={'post_id': post.id},
            )


def notify_post_approved(post, approved_by):
    """Notify post creator when approved."""
    if post.user != approved_by:
        notify(
            user=post.user,
            event_type='post_approved',
            title='Your post has been approved',
            message=f'{approved_by.username} approved your post.',
            data_json={'post_id': post.id},
        )


def notify_changes_requested(post, reviewer, comment):
    """Notify post creator when changes are requested."""
    notify(
        user=post.user,
        event_type='changes_requested',
        title='Changes requested on your post',
        message=comment,
        data_json={'post_id': post.id},
    )


def notify_post_rejected(post, rejected_by, reason):
    """Notify post creator when rejected."""
    notify(
        user=post.user,
        event_type='post_rejected',
        title='Your post was rejected',
        message=f'Reason: {reason}',
        data_json={'post_id': post.id, 'reason': reason},
    )


def notify_post_published(post):
    """Notify creator when post is published."""
    notify(
        user=post.user,
        event_type='post_published',
        title='Post published successfully',
        data_json={'post_id': post.id},
    )


def notify_publish_failed(post, error_message):
    """Notify creator when post publish fails."""
    notify(
        user=post.user,
        event_type='publish_failed',
        title='Post publish failed',
        message=error_message,
        data_json={'post_id': post.id},
        channel='both',
    )


def notify_new_comment(post, comment):
    """Notify post creator of new comment."""
    notify(
        user=post.user,
        event_type='new_comment',
        title=f'New comment on your post',
        message=f'{comment.author_name}: {comment.body[:100]}',
        data_json={'post_id': post.id, 'comment_id': comment.id},
    )


def notify_weekly_report(user, brand, report):
    """Notify user about weekly report."""
    notify(
        user=user,
        event_type='weekly_report',
        title=f'Weekly report ready for {brand.brand_name}',
        data_json={'brand_id': brand.id, 'report_id': report.id},
    )


def notify_approval_reminder(post, approver, hours_pending):
    """Send approval reminder notification."""
    event = 'approval_reminder_12h' if hours_pending <= 12 else 'approval_escalation_24h'
    notify(
        user=approver,
        event_type=event,
        title=f'Approval pending for {hours_pending}h',
        message=f'A post has been waiting for approval for {hours_pending} hours.',
        data_json={'post_id': post.id},
        channel='both',
    )


def _send_email_notification(user, title, message):
    """Stub: Send email notification. Implement with Django email or service."""
    logger.info(f"Email notification stub: {title} to {user.email}")
