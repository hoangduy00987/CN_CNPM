from channels.generic.websocket import AsyncWebsocketConsumer
import json

class JobConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Chấp nhận kết nối
        self.group_name = "updates_group"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        # Xử lý khi kết nối bị ngắt
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Xử lý khi nhận dữ liệu từ WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Gửi phản hồi lại cho client
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def send_update(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

class ApplicationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Chấp nhận kết nối
        self.group_name = "application_group"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        # Xử lý khi kết nối bị ngắt
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Xử lý khi nhận dữ liệu từ WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Gửi phản hồi lại cho client
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def add_new_application(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

class NotificationJobConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f"user_{self.user.id}"

        # Tham gia nhóm thông báo cá nhân
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Rời nhóm thông báo cá nhân
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))