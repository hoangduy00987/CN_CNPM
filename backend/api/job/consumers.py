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

        # Nhóm người dùng cá nhân
        user_group_name = f"user_{self.scope['user'].id}"
        await self.channel_layer.group_add(
            user_group_name,
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
        user_id = event.get('user_id')
        # Nếu không có user_id, tức là gửi thông báo chung cho toàn bộ nhóm
        if user_id is None:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'job_id': event.get('job_id')
            }))
        else:
            # Nếu có user_id, kiểm tra người dùng hiện tại có khớp không
            if self.scope['user'].id == user_id:
                await self.send(text_data=json.dumps({
                    'message': event['message'],
                    'job_id': event.get('job_id')
                }))
        
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

class ApplicationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Tham gia nhóm thông báo cá nhân
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'company_new_apply_{self.user.id}'  # Mỗi người dùng có một nhóm riêng
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # Từ chối kết nối nếu người dùng chưa xác thực
            await self.close()

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
        # Tham gia nhóm thông báo cá nhân
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'user_job_notification_{self.user.id}'  # Mỗi người dùng có một nhóm riêng
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # Từ chối kết nối nếu người dùng chưa xác thực
            await self.close()

    async def disconnect(self, close_code):
        # Xử lý khi kết nối bị ngắt
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

class JobExpiryNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Nhóm dành riêng cho người dùng để gửi thông báo hết hạn
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'user_{self.user.id}'  # Mỗi người dùng có một nhóm riêng
            print("group_consumer:", self.group_name)
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
    
    async def receive(self, text_data):
        # Xử lý khi nhận dữ liệu từ WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Gửi phản hồi lại cho client
        await self.send(text_data=json.dumps({
            'message': message
        }))
    
    async def send_expired_job_notification(self, event):
        job_id = event['job_id']
        job_title = event['job_title']
        message = event['message']
        # Gửi thông báo cho người dùng theo dõi
        await self.send(text_data=json.dumps({
            'message': message,
            'job_id': job_id,
            'job_title': job_title
        }))

