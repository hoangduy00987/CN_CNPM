from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ..submodels.models_recruitment import Job

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
