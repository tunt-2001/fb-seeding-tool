import os
import json
import threading
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from core.worker import SeedingWorker
from core.telegram_bot import TelegramNotifier

app = FastAPI(title="Facebook Seeding Manager Pro")

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

def update_account_status(uid: str, status: str):
    accounts = read_json(ACCOUNTS_FILE, [])
    for acc in accounts:
        if acc.get("uid") == uid:
            acc["status"] = status
            break
    write_json(ACCOUNTS_FILE, accounts)

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

telegram_notifier = TelegramNotifier()
worker = SeedingWorker(logger_callback=add_log, account_update_callback=update_account_status, telegram_notifier=telegram_notifier)
is_running_campaign = False

def handle_telegram_command(cmd: str, args: list):
    global is_running_campaign
    if cmd == "/status":
        accounts = read_json(ACCOUNTS_FILE, [])
        live = len([a for a in accounts if a.get("status") == "Live"])
        cp = len([a for a in accounts if "Checkpoint" in a.get("status", "")])
        state = "Đang chạy chiến dịch 🔥" if is_running_campaign else "Đang rảnh rỗi 🟢"
        msg = (
            f"📊 <b>TRẠNG THÁI HỆ THỐNG</b>\n"
            f"• Trạng thái máy: {state}\n"
            f"• Tổng số Nick: {len(accounts)}\n"
            f"• Nick Live: {live}\n"
            f"• Nick Checkpoint: {cp}"
        )
        telegram_notifier.send_message(msg)

    elif cmd == "/stop":
        worker.is_running = False
        is_running_campaign = False
        telegram_notifier.send_message("🛑 <b>ĐÃ DỪNG TOÀN BỘ CHIẾN DỊCH!</b>")

    elif cmd == "/farm":
        if is_running_campaign:
            telegram_notifier.send_message("⚠️ Hệ thống đang có chiến dịch đang chạy!")
            return
        campaign = read_json(CAMPAIGN_FILE, {})
        campaign["mode"] = "farm"
        write_json(CAMPAIGN_FILE, campaign)
        threading.Thread(target=background_run, daemon=True).start()
        telegram_notifier.send_message("🌾 <b>Đã nhận lệnh: BẮT ĐẦU NUÔI DÀN NICK (FARM MODE)!</b>")

    elif cmd == "/seed":
        if is_running_campaign:
            telegram_notifier.send_message("⚠️ Hệ thống đang có chiến dịch đang chạy!")
            return
        if not args:
            telegram_notifier.send_message("❌ Thiếu link bài viết! Cú pháp: <code>/seed https://facebook.com/...</code>")
            return
        url = args[0]
        campaign = read_json(CAMPAIGN_FILE, {})
        campaign["mode"] = "seeding"
        campaign["target_url"] = url
        write_json(CAMPAIGN_FILE, campaign)
        threading.Thread(target=background_run, daemon=True).start()
        telegram_notifier.send_message(f"🚀 <b>Đã nhận lệnh: BẮT ĐẦU SEEDING BÀI VIẾT!</b>\nLink: {url}")

def init_telegram():
    campaign = read_json(CAMPAIGN_FILE, {})
    token = campaign.get("telegram_bot_token", "")
    chat_id = campaign.get("telegram_chat_id", "")
    if token and chat_id:
        telegram_notifier.bot_token = token
        telegram_notifier.chat_id = chat_id
        telegram_notifier.command_dispatcher = handle_telegram_command
        telegram_notifier.start_polling()

@app.on_event("startup")
def startup_event():
    init_telegram()

@app.get("/api/accounts")
def get_accounts():
    return read_json(ACCOUNTS_FILE, [])

class ImportViaRequest(BaseModel):
    raw_text: str

@app.post("/api/accounts/import")
def import_accounts(req: ImportViaRequest):
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
            
            existing = next((a for a in accounts if a["uid"] == uid), None)
            if existing:
                existing["password"] = password
                existing["two_fa"] = two_fa
                existing["cookie"] = cookie
                existing["proxy"] = proxy
                existing["status"] = "Ready"
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
    add_log(f"Đã nạp {count} tài khoản vào hệ thống.")
    return {"status": "success", "imported": count, "total": len(accounts)}

@app.delete("/api/accounts/clear")
def clear_accounts():
    write_json(ACCOUNTS_FILE, [])
    add_log("Đã xóa sạch danh sách tài khoản.")
    return {"status": "success"}

@app.get("/api/campaign")
def get_campaign():
    default_campaign = {
        "mode": "seeding",
        "target_url": "https://www.facebook.com",
        "threads": 1,
        "headless": false,
        "enable_reaction": true,
        "farm_duration_minutes": 3,
        "use_dcom_hilink": false,
        "rotate_proxy_api": "",
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "comments": [
            "Mẫu này còn hàng không shop ơi?",
            "Tư vấn cho mình với nhé shop!",
            "Chất lượng sản phẩm rất tuyệt vời ạ"
        ]
    }
    return read_json(CAMPAIGN_FILE, default_campaign)

@app.post("/api/campaign")
def save_campaign(campaign: dict):
    write_json(CAMPAIGN_FILE, campaign)
    init_telegram()
    add_log("Đã cập nhật cài đặt chiến dịch & cấu hình Telegram Bot.")
    return {"status": "success"}

@app.post("/api/telegram/test")
def test_telegram(campaign: dict):
    token = campaign.get("telegram_bot_token", "").strip()
    chat_id = campaign.get("telegram_chat_id", "").strip()
    if not token or not chat_id:
        return JSONResponse({"status": "error", "message": "Vui lòng nhập Bot Token và Chat ID!"}, status_code=400)
    
    test_notifier = TelegramNotifier(bot_token=token, chat_id=chat_id)
    try:
        test_notifier.send_message("🎉 <b>KẾT NỐI TELEGRAM BOT THÀNH CÔNG!</b>\nBạn đã có thể điều khiển tool seeding từ xa qua điện thoại!")
        return {"status": "success", "message": "Đã gửi tin nhắn test thành công tới Telegram!"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Không thể gửi: {e}"}, status_code=500)

def background_run():
    global is_running_campaign
    is_running_campaign = True
    accounts = read_json(ACCOUNTS_FILE, [])
    campaign = read_json(CAMPAIGN_FILE, {})
    try:
        active_accounts = [a for a in accounts if not a.get("status", "").startswith("Checkpoint")]
        if not active_accounts:
            add_log("[!] Cảnh báo: Không có nick nào khả dụng!")
            if telegram_notifier.chat_id:
                telegram_notifier.send_message("⚠️ <b>Không thể chạy:</b> Toàn bộ nick trong danh sách đang bị Checkpoint!")
            return
        worker.run_campaign(active_accounts, campaign)
    finally:
        is_running_campaign = False

@app.post("/api/campaign/start")
def start_campaign(background_tasks: BackgroundTasks):
    global is_running_campaign
    if is_running_campaign:
        return JSONResponse({"status": "error", "message": "Chiến dịch đang hoạt động!"}, status_code=400)
    
    accounts = read_json(ACCOUNTS_FILE, [])
    if not accounts:
        return JSONResponse({"status": "error", "message": "Chưa có tài khoản nào!"}, status_code=400)

    threading.Thread(target=background_run, daemon=True).start()
    return {"status": "success", "message": "Chiến dịch đã được khởi chạy!"}

@app.post("/api/campaign/stop")
def stop_campaign():
    global is_running_campaign
    worker.is_running = False
    is_running_campaign = False
    add_log("[!] Đã gửi lệnh DỪNG chiến dịch!")
    return {"status": "success"}

@app.get("/api/logs")
def get_logs():
    return {"is_running": is_running_campaign, "logs": logs_buffer}

@app.get("/", response_class=HTMLResponse)
def index():
    html_file = os.path.join(os.path.dirname(__file__), "web", "index.html")
    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()
