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

class JobExpiryNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Nhóm dành riêng cho người dùng để gửi thông báo hết hạn
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'user_{self.user.id}'  # Mỗi người dùng có một nhóm riêng
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # Từ chối kết nối nếu người dùng chưa xác thực
            await self.close()

    async def disconnect(self, code):
        # Loại người dùng khỏi nhóm khi ngắt kết nối
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_update(self, event):
        job_id = event.get('job_id')
        job_title = event.get('job_title')

        # Gửi thông báo cho người dùng theo dõi
        await self.send(text_data=json.dumps({
            'message': f"Job '{job_title}' is expiring soon!",
            'job_id': job_id
        }))
