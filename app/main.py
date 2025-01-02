from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import json
from .email_sender import EmailSender

app = FastAPI(title="Email Service API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/initialize-auth")
async def initialize_auth(client_secrets: UploadFile = File(...)):
    """Gmail API 인증 초기화"""
    try:
        contents = await client_secrets.read()
        client_secrets_data = json.loads(contents)
        
        email_sender = EmailSender(client_secrets_data)
        auth_url, flow = email_sender.get_authorization_url()
        
        return {
            "auth_url": auth_url,
            "message": "Please visit this URL to authorize the application"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-email")
async def send_email(
    client_secrets: UploadFile = File(...),
    auth_code: str = Form(...),
    to_email: str = Form(...),
    creator_name: str = Form(...),
    report_file: UploadFile = Form(...),
    report_type: str = Form(default="html")
):
    """이메일 발송"""
    try:
        # client_secrets 읽기
        contents = await client_secrets.read()
        client_secrets_data = json.loads(contents)
        
        # EmailSender 초기화 및 인증
        email_sender = EmailSender(client_secrets_data)
        flow = email_sender.initialize_flow()
        credentials = email_sender.get_credentials_from_code(auth_code, flow)
        
        # 보고서 파일 읽기
        report_content = await report_file.read()
        
        # 이메일 발송
        result = await email_sender.send_report(
            credentials=credentials,
            to_email=to_email,
            creator_name=creator_name,
            report_content=report_content,
            report_type=report_type
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}