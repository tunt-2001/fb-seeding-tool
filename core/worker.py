import time
import random
from concurrent.futures import ThreadPoolExecutor
from core.browser_manager import BrowserManager
from core.human_behavior import HumanBehavior
from core.fb_auth import FacebookAuth
from core.ai_generator import AICommentGenerator

class SeedingWorker:
    def __init__(self, logger_callback=None):
        self.logger = logger_callback or print
        self.is_running = False

    def log(self, message: str):
        self.logger(message)

    def process_single_account(self, account: dict, campaign: dict):
        """
        Thực hiện toàn bộ quy trình cho 1 tài khoản (1 luồng độc lập)
        """
        uid = account.get("uid", "")
        password = account.get("password", "")
        two_fa = account.get("two_fa", "")
        proxy_str = account.get("proxy", "")
        profile_id = f"profile_{uid}" if uid else f"profile_{random.randint(1000, 9999)}"

        proxy_dict = None
        if proxy_str and ":" in proxy_str:
            parts = proxy_str.strip().split(":")
            if len(parts) == 2:
                proxy_dict = {"server": f"http://{parts[0]}:{parts[1]}"}
            elif len(parts) >= 4:
                proxy_dict = {
                    "server": f"http://{parts[0]}:{parts[1]}",
                    "username": parts[2],
                    "password": parts[3]
                }

        self.log(f"[{uid}] Bắt đầu phiên làm việc...")

        manager = BrowserManager()
        try:
            page = manager.start_profile(
                profile_id=profile_id,
                proxy=proxy_dict,
                headless=campaign.get("headless", False)
            )

            # 1. Kiểm tra trạng thái đăng nhập
            self.log(f"[{uid}] Đang kiểm tra phiên đăng nhập...")
            if not FacebookAuth.is_logged_in(page):
                self.log(f"[{uid}] Chưa đăng nhập -> Tự động đăng nhập qua UID + 2FA...")
                login_success = FacebookAuth.auto_login(page, uid, password, two_fa)
                if not login_success:
                    self.log(f"[{uid}] [!] Đăng nhập thất bại hoặc bị Checkpoint.")
                    return False
                self.log(f"[{uid}] [✓] Đăng nhập thành công, đã lưu phiên!")
            else:
                self.log(f"[{uid}] [✓] Đã có phiên đăng nhập sẵn (Cookie hợp lệ)!")

            # 2. Điều hướng tới link bài viết
            target_url = campaign.get("target_url")
            self.log(f"[{uid}] Đang truy cập bài viết: {target_url}")
            page.goto(target_url, timeout=60000)
            HumanBehavior.sleep_random(3.0, 5.0)

            # 3. Cuộn trang giả lập (Warm-up)
            self.log(f"[{uid}] Cuộn trang xem nội dung bài viết...")
            HumanBehavior.natural_scroll(page, times=random.randint(2, 4))

            # 4. Thả cảm xúc (Reaction)
            if campaign.get("enable_reaction", True):
                try:
                    like_btn = page.locator("div[aria-label='Thích'], div[aria-label='Like']").first
                    if like_btn.is_visible(timeout=4000):
                        like_btn.click()
                        self.log(f"[{uid}] [✓] Đã thả cảm xúc Thích bài viết.")
                        HumanBehavior.sleep_random(1.5, 3.0)
                except Exception:
                    pass

            # 5. Lấy nội dung comment (từ kịch bản hoặc AI)
            comments_pool = campaign.get("comments", [])
            comment_text = ""
            if comments_pool:
                comment_text = random.choice(comments_pool)
            else:
                comment_text = "Sản phẩm tốt quá shop ơi, tư vấn cho mình với nhé!"

            # 6. Gõ bình luận tự nhiên
            self.log(f"[{uid}] Đang nhập bình luận: \"{comment_text}\"")
            comment_box = page.locator("div[aria-label='Viết bình luận'], div[aria-label='Write a comment'], div[role='textbox']").first
            
            if comment_box.is_visible(timeout=6000):
                comment_box.click()
                HumanBehavior.sleep_random(1.0, 2.0)
                
                min_t = campaign.get("min_typing_delay", 60)
                max_t = campaign.get("max_typing_delay", 150)
                for char in comment_text:
                    comment_box.press_sequentially(char, delay=random.randint(min_t, max_t))
                
                HumanBehavior.sleep_random(1.0, 2.0)
                comment_box.press("Enter")
                self.log(f"[{uid}] [✓] Đã gửi bình luận thành công!")
                HumanBehavior.sleep_random(5.0, 8.0)
            else:
                self.log(f"[{uid}] [!] Không tìm thấy ô bình luận.")

            return True
        except Exception as e:
            self.log(f"[{uid}] [!] Lỗi trong quá trình chạy: {e}")
            return False
        finally:
            manager.close()
            self.log(f"[{uid}] Đã đóng trình duyệt.")

    def run_campaign(self, accounts: list, campaign: dict):
        """
        Chạy đa luồng song song theo số luồng cấu hình (max_workers)
        """
        self.is_running = True
        max_threads = int(campaign.get("threads", 1))
        self.log(f"=== BẮT ĐẦU CHIẾN DỊCH ({len(accounts)} NICK, {max_threads} LUỒNG ĐỒNG THỜI) ===")

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(self.process_single_account, acc, campaign) for acc in accounts]
            for future in futures:
                if not self.is_running:
                    break
                try:
                    future.result()
                except Exception as e:
                    self.log(f"[ThreadPool Error] {e}")

        self.is_running = False
        self.log("=== HOÀN TẤT TOÀN BỘ CHIẾN DỊCH! ===")
