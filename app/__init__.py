from flask import Flask, request, redirect, url_for, session, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import base64
from email.mime.text import MIMEText


app = Flask(__name__)
app.secret_key = '1212'  # 보안을 위한 키 설정

# Google OAuth 설정
CLIENT_ID = "209346899317-ktoia8i5t0euic559fjao5otmnvspfns.apps.googleusercontent.com"
CLIENT_SECRET = "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"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
REDIRECT_URI = "https://127.0.0.1:8080/"


# Gmail API로 이메일 전송 함수
def send_email_with_gmail_api(user_email, recipient_email, subject, body):
    """
    Gmail API를 사용하여 이메일 전송
    """
    try:
        credentials = Credentials(**session['credentials'])
        service = build('gmail', 'v1', credentials=credentials)

        # 이메일 생성
        message = MIMEText(body)
        message['to'] = recipient_email
        message['from'] = user_email
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Gmail API로 이메일 전송
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        return "이메일 전송 성공!"
    except Exception as e:
        return f"이메일 전송 중 오류 발생: {e}"

@app.route('/')
def index():
    return '<a href="/authorize">이메일 전송</a>'

@app.route('/authorize')
def authorize():
    # Google OAuth 2.0 플로우 시작
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    authorization_url, _ = flow.authorization_url(prompt='consent')
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # Google OAuth 2.0 콜백 처리
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(authorization_response=request.url)
    session['credentials'] = flow.credentials_to_dict()
    return redirect(url_for('send_email'))

@app.route('/send-email')
def send_email():
    # Gmail API로 이메일 전송
    user_email = "dkdla93@gmail.com"  # 발신자 이메일
    recipient_email = "dkdla93@gmail.com"  # 수신자 이메일
    subject = "테스트 이메일"
    body = "이것은 Google OAuth를 통한 이메일 테스트입니다."
    result = send_email_with_gmail_api(user_email, recipient_email, subject, body)
    return result

if __name__ == "__main__":
    # HTTPS로 Flask 앱 실행
    app.run(host="0.0.0.0", port=8080, ssl_context=("cert.pem", "key.pem"))
