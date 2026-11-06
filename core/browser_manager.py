import os
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

class BrowserManager:
    """
    Quản lý khởi tạo trình duyệt Anti-detect và duy trì Profile độc lập cho từng Nick.
    """
    def __init__(self, base_profile_dir="profiles"):
        self.base_profile_dir = base_profile_dir
        os.makedirs(self.base_profile_dir, exist_ok=True)
        self.playwright = None
        self.context = None

    def start_profile(self, profile_id: str, proxy: dict = None, headless: bool = False):
        user_data_dir = os.path.join(self.base_profile_dir, profile_id)
        os.makedirs(user_data_dir, exist_ok=True)

        self.playwright = sync_playwright().start()

        # Cấu hình tham số khởi chạy chống phát hiện bot
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=IsolateOrigins,site-per-process",
            "--start-maximized"
        ]

        proxy_config = None
        if proxy and proxy.get("server"):
            proxy_config = {
                "server": proxy["server"],
                "username": proxy.get("username", ""),
                "password": proxy.get("password", "")
            }

        # Khởi tạo Persistent Context để lưu session/cookies vĩnh viễn cho Profile này
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            channel="chromium",
            args=launch_args,
            no_viewport=True,
            proxy=proxy_config,
            locale="vi-VN",
            timezone_id="Asia/Ho_Chi_Minh"
        )

        page = self.context.new_page() if not self.context.pages else self.context.pages[0]
        
        # Áp dụng Stealth để qua mặt các bài kiểm tra Bot của Cloudflare, Facebook
        stealth = Stealth()
        stealth.apply_stealth_sync(page)

        return page

    def close(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
