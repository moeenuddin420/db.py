import os
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # e.g. @yourchannel or -100xxxxxxxxxx

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def check_config():
    if not BOT_TOKEN or not CHANNEL_ID:
        raise HTTPException(status_code=500, detail="BOT_TOKEN or CHANNEL_ID env variable is missing")


@app.get("/")
def health():
    return {"status": "ok", "message": "tv.py is running"}


@app.post("/send-file")
async def send_file(file: UploadFile = File(...)):
    check_config()

    file_bytes = await file.read()
    filename = file.filename
    content_type = file.content_type or ""

    if content_type.startswith("image/"):
        endpoint = f"{TELEGRAM_API}/sendPhoto"
        files = {"photo": (filename, file_bytes, content_type)}
    elif content_type.startswith("video/"):
        endpoint = f"{TELEGRAM_API}/sendVideo"
        files = {"video": (filename, file_bytes, content_type)}
    elif content_type.startswith("audio/"):
        endpoint = f"{TELEGRAM_API}/sendAudio"
        files = {"audio": (filename, file_bytes, content_type)}
    else:
        endpoint = f"{TELEGRAM_API}/sendDocument"
        files = {"document": (filename, file_bytes, content_type)}

    data = {"chat_id": CHANNEL_ID}

    response = requests.post(endpoint, data=data, files=files)

    if response.status_code == 200:
        return JSONResponse(status_code=200, content={"success": True, "file": filename})
    else:
        return JSONResponse(
            status_code=response.status_code,
            content={"success": False, "error": response.json()}
        )
