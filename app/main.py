from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/send-email")
async def send_email(
    to_email: str = Form(...),
    creator_name: str = Form(...),
    report_file: UploadFile = File(...),
    email_user: str = Form(...),    # Gmail 계정
    email_password: str = Form(...) # Gmail 앱 비밀번호
):
    try:
        # 이메일 설정
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # 이메일 메시지 생성
        message = MIMEMultipart()
        message["From"] = email_user
        message["To"] = to_email
        message["Subject"] = f"{creator_name} 크리에이터님의 음원 사용현황 보고서"

        # 이메일 본문
        body = f"""안녕하세요, {creator_name} 크리에이터님

첨부된 파일을 통해 음원 사용현황을 확인해주세요.
문의사항이 있으시면 언제든 연락 주시기 바랍니다.

감사합니다."""
        
        message.attach(MIMEText(body, "plain"))

        # 첨부 파일 추가
        report_content = await report_file.read()
        attachment = MIMEApplication(report_content, _subtype="html")
        attachment.add_header(
            "Content-Disposition", "attachment", 
            filename=f"{creator_name}_report.html"
        )
        message.attach(attachment)

        # 이메일 발송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(message)

        return {"status": "success", "message": "이메일이 성공적으로 발송되었습니다."}

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"이메일 발송 실패: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "healthy"}
