import os
import json
import threading
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

from core.worker import SeedingWorker

app = FastAPI(title="Facebook Seeding Manager")

ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), "accounts.json")
CAMPAIGN_FILE = os.path.join(os.path.dirname(__file__), "campaign.json")

logs_buffer = []

def add_log(msg: str):
    import datetime
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    formatted = f"[{now_str}] {msg}"
    print(formatted)
    logs_buffer.append(formatted)
    if len(logs_buffer) > 300:
        logs_buffer.pop(0)

worker = SeedingWorker(logger_callback=add_log)
is_running_campaign = False

def read_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.get("/api/accounts")
def get_accounts():
    return read_json(ACCOUNTS_FILE, [])

class ImportViaRequest(BaseModel):
    raw_text: str

@app.post("/api/accounts/import")
def import_accounts(req: ImportViaRequest):
    """
    Hỗ trợ paste định dạng:
    UID|Pass|2FA|Cookie|Proxy hoặc UID|Pass|2FA hoặc UID|Pass
    """
    accounts = read_json(ACCOUNTS_FILE, [])
    lines = [line.strip() for line in req.raw_text.splitlines() if line.strip()]
    count = 0
    for line in lines:
        parts = line.split("|")
        if len(parts) >= 2:
            uid = parts[0].strip()
            password = parts[1].strip()
            two_fa = parts[2].strip() if len(parts) > 2 else ""
            cookie = parts[3].strip() if len(parts) > 3 else ""
            proxy = parts[4].strip() if len(parts) > 4 else ""
            
            # Cập nhật nếu đã có, hoặc thêm mới
            existing = next((a for a in accounts if a["uid"] == uid), None)
            if existing:
                existing["password"] = password
                existing["two_fa"] = two_fa
                existing["cookie"] = cookie
                existing["proxy"] = proxy
            else:
                accounts.append({
                    "uid": uid,
                    "password": password,
                    "two_fa": two_fa,
                    "cookie": cookie,
                    "proxy": proxy,
                    "status": "Ready"
                })
            count += 1

    write_json(ACCOUNTS_FILE, accounts)
    add_log(f"Đã nhập thành công {count} tài khoản vào hệ thống.")
    return {"status": "success", "imported": count, "total": len(accounts)}

@app.delete("/api/accounts/clear")
def clear_accounts():
    write_json(ACCOUNTS_FILE, [])
    add_log("Đã xóa toàn bộ danh sách tài khoản.")
    return {"status": "success"}

@app.get("/api/campaign")
def get_campaign():
    return read_json(CAMPAIGN_FILE, {})

@app.post("/api/campaign")
def save_campaign(campaign: dict):
    write_json(CAMPAIGN_FILE, campaign)
    add_log("Đã lưu cài đặt kịch bản chiến dịch thành công.")
    return {"status": "success"}

def background_run():
    global is_running_campaign
    is_running_campaign = True
    accounts = read_json(ACCOUNTS_FILE, [])
    campaign = read_json(CAMPAIGN_FILE, {})
    try:
        worker.run_campaign(accounts, campaign)
    finally:
        is_running_campaign = False

@app.post("/api/campaign/start")
def start_campaign(background_tasks: BackgroundTasks):
    global is_running_campaign
    if is_running_campaign:
        return JSONResponse({"status": "error", "message": "Chiến dịch đang chạy!"}, status_code=400)
    
    accounts = read_json(ACCOUNTS_FILE, [])
    if not accounts:
        return JSONResponse({"status": "error", "message": "Chưa có tài khoản nào trong hệ thống!"}, status_code=400)

    threading.Thread(target=background_run, daemon=True).start()
    return {"status": "success", "message": "Đã bắt đầu chạy chiến dịch!"}

@app.get("/api/logs")
def get_logs():
    return {"is_running": is_running_campaign, "logs": logs_buffer}

@app.get("/", response_class=HTMLResponse)
def index():
    html_file = os.path.join(os.path.dirname(__file__), "web", "index.html")
    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()
