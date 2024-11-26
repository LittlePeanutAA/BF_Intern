from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import re


class GmailVerificationCode:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Xác thực với Gmail API"""
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',  # Tải file này từ Google Cloud Console
            self.SCOPES
        )
        creds = flow.run_local_server(port=0)
        self.service = build('gmail', 'v1', credentials=creds)

    def getVerificationCode(self, sender_email, minutes_ago=5):
        """Lấy mã xác thực từ email gần nhất"""
        try:
            # Tìm email mới nhất từ sender
            print("Truy xuất email... ")
            # In ra các tham số tìm kiếm để debug
            print(f"Sender email: {sender_email}")
            print(f"Minutes ago: {minutes_ago}")

            # Thử query đơn giản hơn trước
            query = f'from:{sender_email}'

            results = self.service.users().messages().list(
                userId='me',
                q=query
            ).execute()

            if 'messages' not in results:
                print("Không tìm thấy email nào")
                return None

            # Lấy email đầu tiên
            print("Lấy email đầu tiên...")
            msg = self.service.users().messages().get(
                userId='me',
                id=results['messages'][0]['id']
            ).execute()

            # Lấy tiêu đề email
            print("Lấy tiêu đề email: ")
            email_subject = msg['payload']['headers']
            subject = ''
            for header in email_subject:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break

            # Tìm mã xác thực trong tiêu đề
            code_match = re.search(r'\b\d{6}\b', subject)
            if code_match:
                return code_match.group(0)
            return None

            # Lấy nội dung email
            # if 'data' in msg['payload']['body']:
            #     content = base64.urlsafe_b64decode(
            #         msg['payload']['body']['data']
            #     ).decode('utf-8')
            # else:
            #     content = base64.urlsafe_b64decode(
            #         msg['payload']['parts'][0]['body']['data']
            #     ).decode('utf-8')

        except Exception as e:
            print(f"Error getting verification code: {str(e)}")
            return None


# gmail_ = GmailVerificationCode()
# co = gmail_.getVerificationCode(sender_email="hi@badoo.com", minutes_ago=100)
# print(co)
