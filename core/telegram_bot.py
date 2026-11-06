import time
import requests
import threading

class TelegramNotifier:
    """
    Quản lý thông báo và nhận lệnh điều khiển từ xa qua Telegram Bot (Hỗ trợ Chat 1-1 và Group).
    """
    def __init__(self, bot_token: str = "", chat_id: str = "", command_dispatcher=None):
        self.bot_token = bot_token.strip()
        self.chat_id = chat_id.strip()
        self.command_dispatcher = command_dispatcher
        self.is_polling = False
        self.last_update_id = 0

    def send_message(self, text: str):
        if not self.bot_token or not self.chat_id:
            return
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"[Telegram Error] Gửi tin nhắn thất bại: {e}")

    def send_photo(self, photo_path: str, caption: str = ""):
        if not self.bot_token or not self.chat_id:
            return
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
            with open(photo_path, "rb") as photo:
                files = {"photo": photo}
                data = {"chat_id": self.chat_id, "caption": caption, "parse_mode": "HTML"}
                requests.post(url, data=data, files=files, timeout=20)
        except Exception as e:
            print(f"[Telegram Error] Gửi ảnh thất bại: {e}")

    def start_polling(self):
        if not self.bot_token or not self.chat_id:
            return
        self.is_polling = True
        threading.Thread(target=self._polling_loop, daemon=True).start()

    def stop_polling(self):
        self.is_polling = False

    def _polling_loop(self):
        print("[Telegram Bot] Đang lắng nghe lệnh từ xa (Hỗ trợ Nhóm)...")
        while self.is_polling:
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates?offset={self.last_update_id + 1}&timeout=15"
                res = requests.get(url, timeout=20).json()
                if res.get("ok"):
                    for item in res.get("result", []):
                        self.last_update_id = item["update_id"]
                        msg = item.get("message", {})
                        from_chat_id = str(msg.get("chat", {}).get("id", ""))
                        text = msg.get("text", "").strip()

                        # Kiểm tra tin nhắn đến từ đúng Nhóm hoặc User đã cấu hình
                        if from_chat_id == self.chat_id and text.startswith("/"):
                            self._handle_command(text)
            except Exception:
                time.sleep(3)
            time.sleep(1)

    def _handle_command(self, cmd_text: str):
        parts = cmd_text.split()
        raw_cmd = parts[0].lower()
        # Cắt bỏ đuôi @tenbot nếu người dùng gõ trong nhóm (ví dụ /seed@my_bot -> /seed)
        cmd = raw_cmd.split("@")[0]

        if cmd == "/help" or cmd == "/start":
            reply = (
                "🤖 <b>FB SEEDING PRO - ĐIỀU KHIỂN TRONG NHÓM</b>\n\n"
                "📌 <b>Bất kỳ ai trong nhóm có thể dùng các lệnh:</b>\n"
                "• <code>/status</code>: Kiểm tra trạng thái máy & dàn nick\n"
                "• <code>/seed &lt;link_fb&gt;</code>: Chạy seeding vào bài viết\n"
                "• <code>/farm</code>: Kích hoạt chế độ nuôi nick\n"
                "• <code>/stop</code>: Dừng khẩn cấp toàn bộ hệ thống\n"
                "• <code>/help</code>: Xem bảng hướng dẫn này"
            )
            self.send_message(reply)

        elif self.command_dispatcher:
            self.command_dispatcher(cmd, parts[1:] if len(parts) > 1 else [])
