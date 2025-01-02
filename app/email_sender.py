import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64

class EmailSender:
    def __init__(self, credentials_content):
        """Gmail API 인증 초기화"""
        self.credentials_info = json.loads(credentials_content)
        self.creds = None
        self._setup_credentials()

    def _setup_credentials(self):
        """Credentials 설정"""
        try:
            self.creds = Credentials.from_authorized_user_info(
                self.credentials_info,
                ['https://www.googleapis.com/auth/gmail.send']
            )
        except Exception as e:
            raise Exception(f"Credentials 설정 실패: {str(e)}")

    async def send_report(self, to_email: str, creator_name: str, report_content: bytes):
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
            report = MIMEApplication(report_content, _subtype='html')
            report.add_header('Content-Disposition', 'attachment', 
                            filename=f'{creator_name}_report.html')
            message.attach(report)

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return True

        except Exception as e:
            raise Exception(f"이메일 발송 실패: {str(e)}")
