from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from .email_sender import EmailSender
import json

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://excel2report.streamlit.app"],  # Streamlit 앱 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gmail API 클라이언트 초기화
email_sender = None

@app.post("/send-email")
async def send_email(
    background_tasks: BackgroundTasks,
    to_email: str = Form(...),
    creator_name: str = Form(...),
    report_file: UploadFile = File(...),
    credentials_file: UploadFile = File(...)
):
    try:
        # credentials 파일 읽기
        credentials_content = await credentials_file.read()
        
        # 보고서 파일 읽기
        report_content = await report_file.read()
        
        # EmailSender 초기화
        global email_sender
        email_sender = EmailSender(credentials_content)
        
        # 백그라운드에서 이메일 전송
        background_tasks.add_task(
            email_sender.send_report,
            to_email=to_email,
            creator_name=creator_name,
            report_content=report_content
        )
        
        return {
            "status": "success",
            "message": f"이메일 발송이 시작되었습니다. ({to_email})"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
