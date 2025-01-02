from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64
from .config import settings

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailSender:
    def __init__(self):
        self.creds = None
        self.initialize_credentials()

    def initialize_credentials(self):
        """Gmail API 인증 초기화"""
        self.creds = Credentials(
            None,
            refresh_token=settings.GOOGLE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )

        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())

    async def send_report(self, to_email: str, creator_name: str, report_content: bytes, 
                         report_type: str = 'html'):
        """보고서를 첨부하여 이메일 발송"""
        try:
            service = build('gmail', 'v1', credentials=self.creds)

            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = f"{creator_name} 크리에이터님의 음원 사용현황 보고서"

            body = f"""안녕하세요, {creator_name} 크리에이터님

첨부된 파일을 통해 음원 사용현황을 확인해주세요.
문의사항이 있으시면 언제든 연락 주시기 바랍니다.

감사합니다."""

            message.attach(MIMEText(body, 'plain'))

            # 보고서 첨부
            report = MIMEApplication(report_content, _subtype=report_type)
            report.add_header('Content-Disposition', 'attachment', 
                            filename=f'{creator_name}_report.{report_type}')
            message.attach(report)

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return {"status": "success", "message": f"이메일이 성공적으로 발송되었습니다. ({to_email})"}

        except Exception as e:
            return {"status": "error", "message": f"이메일 발송 실패: {str(e)}"}