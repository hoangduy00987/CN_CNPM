from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from django.conf import settings
import os
import pickle
import base64

JOB_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(JOB_DIR, 'credentials', 'credentials.json')
TOKEN_FILE = os.path.join(JOB_DIR, 'credentials', 'token.json')
KEY_FILE = os.path.join(JOB_DIR, 'credentials', 'key.json')

# Load credentials.json from Google API Console
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def load_token_from_env():
    encoded_token = settings.GOOGLE_API_TOKEN
    if not encoded_token:
        raise ValueError("GOOGLE_API_TOKEN is not set")
    
    # Decode token
    token_data = base64.b64decode(encoded_token.encode('utf-8'))
    creds = pickle.loads(token_data)

    # Refresh token if need:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds

def create_google_meet_event(candidate_name, interview_date, interview_time, duration, interviewer_email):
    try:
        # Load credentials from env file
        creds = load_token_from_env()

        # Kết nối với Calendar API
        service = build('calendar', 'v3', credentials=creds)

        # Tạo thời gian bắt đầu và kết thúc
        start_time = datetime.combine(interview_date, interview_time)
        end_time = start_time + timedelta(minutes=duration)

        # Sự kiện
        event = {
            'summary': f'Interview with {candidate_name}',
            'description': f'Interview for {candidate_name}.',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
            'attendees': [
                {'email': interviewer_email},
            ],
            'conferenceData': {
                'createRequest': {
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                    'requestId': f"meet-{candidate_name.lower().replace(' ', '-')}",
                }
            },
        }

        # Tạo sự kiện trong Calendar
        event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
        return {
            'meet_link': event.get('hangoutLink'),  # Link Google Meet
            'event_id': event.get('id')
        }
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def update_google_calendar_event(event_id, candidate_name, interview_date, interview_time, duration):
    try:
        # Load credentials
        creds = load_token_from_env()

        # Kết nối với Calendar API
        service = build('calendar', 'v3', credentials=creds)

        # Lấy thông tin sự kiện hiện tại
        event = service.events().get(calendarId='primary', eventId=event_id).execute()

        # Tạo thời gian bắt đầu và kết thúc
        start_time = datetime.combine(interview_date, interview_time)
        end_time = start_time + timedelta(minutes=duration)

        # Cập nhật thông tin sự kiện
        updated_data = {
            'summary': f'Updated Interview with {candidate_name}',
            'description': f'Updated description for {candidate_name} interview.',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
        }
        event.update(updated_data)

        # Gửi yêu cầu cập nhật
        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

        print(f"Event {event_id} has been updated.")
        
        return updated_event
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def delete_google_calendar_event(event_id):
    try:
        # Load credentials
        creds = load_token_from_env()

        # Kết nối với Calendar API
        service = build('calendar', 'v3', credentials=creds)

        # Xóa sự kiện
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f"Event {event_id} has been deleted.")
        return True
    except HttpError as error:
        print(f"An error occurred: {error}")
        return False

def authenticate_google_account():
    creds = None
    token_path = TOKEN_FILE  # File lưu thông tin token

    try:
        # Kiểm tra nếu token đã tồn tại
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token_file:
                creds = pickle.load(token_file)
        
        # Nếu token không tồn tại hoặc không hợp lệ, thực hiện xác thực
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file=CREDENTIALS_FILE,
                    scopes=SCOPES
                )
                creds = flow.run_local_server(port=8080)

            # Lưu token vào file để sử dụng lại
            with open(token_path, 'wb') as token_file:
                pickle.dump(creds, token_file)
    
    except FileNotFoundError:
        print(f"Token file not found at {token_path}, creating a new one.")
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=CREDENTIALS_FILE,
            scopes=SCOPES
        )
        creds = flow.run_local_server(port=8080)

        # Lưu token mới vào file token.json
        with open(token_path, 'wb') as token_file:
            pickle.dump(creds, token_file)
    
    except EOFError:
        print("Token file is corrupted or empty. Recreating it.")
        # Xóa file token bị lỗi
        if os.path.exists(token_path):
            os.remove(token_path)

        # Thực hiện xác thực lại
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=CREDENTIALS_FILE,
            scopes=SCOPES
        )
        creds = flow.run_local_server(port=8080)

        # Lưu token mới vào file token.json
        with open(token_path, 'wb') as token_file:
            pickle.dump(creds, token_file)
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
        
    return creds

def encode_token():
    with open(TOKEN_FILE, 'rb') as token_file:
        token_data = token_file.read()
    encoded_token = base64.b64encode(token_data).decode('utf-8')
    print("Encoded token:", encoded_token)

if __name__ == '__main__':
    encode_token()
