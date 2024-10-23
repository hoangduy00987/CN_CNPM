from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ..submodels.models_recruitment import Job, JobFollow
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@receiver(post_save, sender=Job)
def send_websocket_notification(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'updates_group',
        {
            'type': 'send_update',
            'message': f'New update: {instance.title}'
        }
    )
    print('send to frontend')

@shared_task
def notify_expiring_jobs():
    three_days_later = timezone.now() + timedelta(days=3)
    jobs_about_to_expire = Job.objects.filter(expired_at__lte=three_days_later, expired_at__gte=timezone.now())

    for job in jobs_about_to_expire:
        # Lấy danh sách ứng viên theo dõi công việc này
        followers = JobFollow.objects.filter(job=job, is_notified=False)
        
        for follow in followers:
            candidate = follow.candidate

            # Gửi thông báo qua WebSocket cho ứng viên theo dõi, qua nhóm riêng của họ
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)( 
                f'user_{candidate.user.id}',  # Nhóm dành riêng cho người dùng
                {
                    'type': 'send_update',
                    'message': f"Job '{job.title}' is expiring in 3 days, don't miss it!",
                    'job_id': job.id,
                    'user_id': candidate.user.id  # Gửi kèm ID người dùng
                }
            )

            # Đánh dấu là đã thông báo để không thông báo lại
            follow.is_notified = True
            follow.save()