from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ..submodels.models_recruitment import Job, Application, JobFollow, Notification
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

# @receiver(post_save, sender=Job)
# def send_websocket_notification(sender, instance, **kwargs):
#     if instance.status == Job.STATUS_ACTIVE:
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             'updates_group',
#             {
#                 'type': 'send_update',
#                 'message': f'New update: {instance.title}'
#             }
#         )
#         print('send to frontend')


@receiver(post_save, sender=Application)
def send_notification_when_new_apply(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'company_new_apply_{instance.job.company.user.id}',
            {
                'type': 'add_new_application',
                'message': f'{instance.candidate.full_name} has just applied for {instance.job.title}. Please check it out./job_id={instance.job.id}'
            }
        )

@shared_task
def notify_expiring_jobs():
    days_later = timezone.now() + timedelta(days=7)
    jobs_about_to_expire = Job.objects.filter(expired_at__isnull=False, expired_at__lte=days_later, expired_at__gte=timezone.now())

    for job in jobs_about_to_expire:
        # Lấy danh sách ứng viên theo dõi công việc này
        followers = JobFollow.objects.filter(job=job, is_notified=False)
        time_difference = job.expired_at - timezone.localtime(timezone.now())
        duration = round(time_difference.total_seconds() / 86400)
        message = f'Job {job.title} will expire in {duration} days.'
        
        for follow in followers:
            candidate = follow.candidate

            send_mail(
                subject=settings.EMAIL_TITLE,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[candidate.user.email],
                fail_silently=False
            )
            print(f'Da gui mail toi {candidate.full_name}')
            print("group_signal: ", f'user_{candidate.user.id}')

            # Gửi thông báo qua WebSocket cho ứng viên theo dõi, qua nhóm riêng của họ
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{candidate.user.id}',  # Gửi tới nhóm người dùng cụ thể
                {
                    'type': 'send_expired_job_notification',
                    'message': message,
                    'job_id': job.id,
                    'job_title': job.title
                }
            )
            print('Da gui message toi client')

            # # Đánh dấu là đã thông báo để không thông báo lại
            # follow.is_notified = True
            # follow.save()

@receiver(post_save, sender=Notification)
def send_new_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_job_notification_{instance.user.id}',
            {
                'type': 'send_notification',
                'message': instance.message
            }
        )
        print('Da gui thong bao toi nguoi dung')

@receiver(pre_save, sender=Application)
def save_old_is_seen_by_recruiter(sender, instance, **kwargs):
    if instance.pk:
        instance._old_is_seen_by_recruiter = Application.objects.get(pk=instance.pk).is_seen_by_recruiter

@receiver(post_save, sender=Application)
def handle_application_seen(sender, instance, created, **kwargs):
    if not created:
        if hasattr(instance, '_old_is_seen_by_recruiter') and not instance._old_is_seen_by_recruiter and instance.is_seen_by_recruiter:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_application_seen_{instance.candidate.user.id}',
                {
                    'type': 'application_seen',
                    'message': f'Recruiter has seen your application./application_id={instance.id}'
                }
            )
