import time
import random
from concurrent.futures import ThreadPoolExecutor
from core.browser_manager import BrowserManager
from core.human_behavior import HumanBehavior
from core.fb_auth import FacebookAuth
from core.network_rotator import NetworkRotator

class SeedingWorker:
    def __init__(self, logger_callback=None, account_update_callback=None):
        self.logger = logger_callback or print
        self.update_account_status = account_update_callback or (lambda uid, status: None)
        self.is_running = False

    def log(self, message: str):
        self.logger(message)

    def farm_account(self, page, uid: str, duration_minutes: int = 3):
        """
        KỊCH BẢN NUÔI NICK (FARM MODE):
        Lướt Newsfeed, xem video Reels, like dạo bạn bè để tăng trust cho tài khoản.
        """
        self.log(f"[{uid}] [Farm Mode] Bắt đầu hoạt động lướt dạo tăng tương tác ({duration_minutes} phút)...")
        page.goto("https://www.facebook.com", timeout=45000)
        HumanBehavior.sleep_random(3, 5)

        end_time = time.time() + (duration_minutes * 60)
        while time.time() < end_time and self.is_running:
            # Cuộn lướt xem bài
            HumanBehavior.natural_scroll(page, times=random.randint(2, 4))
            HumanBehavior.sleep_random(4, 8)

            # Thỉnh thoảng like dạo 1 bài ngẫu nhiên trên Newsfeed
            if random.random() < 0.35:
                try:
                    like_btns = page.locator("div[aria-label='Thích'], div[aria-label='Like']").all()
                    if like_btns:
                        target_btn = random.choice(like_btns[:3])
                        target_btn.click()
                        self.log(f"[{uid}] [Farm Mode] Đã like dạo 1 bài viết trên Newsfeed.")
                        HumanBehavior.sleep_random(3, 6)
                except Exception:
                    pass

            # Thỉnh thoảng mở tab Video/Reels lướt xem
            if random.random() < 0.2:
                try:
                    self.log(f"[{uid}] [Farm Mode] Mở xem video Reels...")
                    page.goto("https://www.facebook.com/watch", timeout=30000)
                    HumanBehavior.sleep_random(15, 25) # Xem video 15-25 giây
                    page.goto("https://www.facebook.com", timeout=30000)
                except Exception:
                    pass

        self.log(f"[{uid}] [Farm Mode] Hoàn tất phiên nuôi nick!")

    def process_single_account(self, account: dict, campaign: dict, thread_reply_target: str = None) -> tuple[bool, str]:
        """
        Thực hiện toàn bộ quy trình cho 1 tài khoản
        """
        uid = account.get("uid", "")
        password = account.get("password", "")
        two_fa = account.get("two_fa", "")
        proxy_str = account.get("proxy", "")
        mode = campaign.get("mode", "seeding") # "seeding", "farm", "thread_reply"
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

        self.log(f"[{uid}] Bắt đầu phiên làm việc (Chế độ: {mode.upper()})...")

        manager = BrowserManager()
        posted_comment_text = ""
        try:
            page = manager.start_profile(
                profile_id=profile_id,
                proxy=proxy_dict,
                headless=campaign.get("headless", False)
            )

            # 1. Kiểm tra trạng thái đăng nhập và Checkpoint
            self.log(f"[{uid}] Đang kiểm tra trạng thái nick...")
            page.goto("https://www.facebook.com", timeout=30000)
            status = FacebookAuth.check_account_health(page)

            if status != "Live":
                self.log(f"[{uid}] Chưa có phiên đăng nhập -> Tự động login UID/2FA...")
                success, login_status = FacebookAuth.auto_login(page, uid, password, two_fa)
                self.update_account_status(uid, login_status)
                if not success:
                    self.log(f"[{uid}] [!] Không thể đăng nhập. Trạng thái: {login_status}")
                    return False, ""
                self.log(f"[{uid}] [✓] Đăng nhập thành công, đã lưu phiên!")
            else:
                self.update_account_status(uid, "Live")
                self.log(f"[{uid}] [✓] Trạng thái tài khoản: LIVE")

            # 2. XỬ LÝ THEO CHẾ ĐỘ
            if mode == "farm":
                # Chế độ nuôi nick
                farm_mins = int(campaign.get("farm_duration_minutes", 3))
                self.farm_account(page, uid, duration_minutes=farm_mins)
                return True, ""

            # CHẾ ĐỘ SEEDING HOẶC SEEDING LỒNG NHAU (THREAD REPLY)
            target_url = campaign.get("target_url")
            self.log(f"[{uid}] Truy cập bài viết: {target_url}")
            page.goto(target_url, timeout=60000)
            HumanBehavior.sleep_random(3.0, 5.0)

            # Cuộn trang warm-up
            self.log(f"[{uid}] Cuộn trang xem nội dung bài viết...")
            HumanBehavior.natural_scroll(page, times=random.randint(2, 4))

            # Thả Like nếu có bật
            if campaign.get("enable_reaction", True):
                try:
                    like_btn = page.locator("div[aria-label='Thích'], div[aria-label='Like']").first
                    if like_btn.is_visible(timeout=3000):
                        like_btn.click()
                        self.log(f"[{uid}] [✓] Đã thả cảm xúc Thích bài viết.")
                        HumanBehavior.sleep_random(1.5, 3.0)
                except Exception:
                    pass

            # Lấy nội dung comment
            comments_pool = campaign.get("comments", [])
            comment_text = random.choice(comments_pool) if comments_pool else "Sản phẩm còn hàng sẵn không shop ơi?"
            posted_comment_text = comment_text

            # Nếu là chế độ Thread Reply và có comment mục tiêu cần trả lời
            if mode == "thread_reply" and thread_reply_target:
                self.log(f"[{uid}] [Thread Mode] Đang tìm comment mồi: \"{thread_reply_target[:30]}...\" để Reply")
                try:
                    # Tìm khối comment chứa nội dung của nick mồi
                    cmt_locator = page.locator(f"div[role='article']:has-text('{thread_reply_target[:20]}')").first
                    if cmt_locator.is_visible(timeout=5000):
                        reply_btn = cmt_locator.locator("div[role='button']:has-text('Trả lời'), div[role='button']:has-text('Reply')").first
                        if reply_btn.is_visible(timeout=3000):
                            reply_btn.click()
                            HumanBehavior.sleep_random(1.5, 2.5)
                            self.log(f"[{uid}] [✓] Đã bấm nút Trả lời của comment mục tiêu!")
                except Exception as e:
                    self.log(f"[{uid}] Không tìm thấy comment mục tiêu để Reply, sẽ comment trực tiếp vào bài ({e})")

            # Gõ comment
            self.log(f"[{uid}] Đang nhập bình luận: \"{comment_text}\"")
            comment_box = page.locator("div[aria-label='Viết bình luận'], div[aria-label='Write a comment'], div[aria-label='Viết câu trả lời...'], div[role='textbox']").first
            
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
                HumanBehavior.sleep_random(4.0, 7.0)
            else:
                self.log(f"[{uid}] [!] Không tìm thấy ô bình luận.")

            return True, posted_comment_text
        except Exception as e:
            self.log(f"[{uid}] [!] Lỗi: {e}")
            return False, ""
        finally:
            manager.close()
            self.log(f"[{uid}] Đã đóng trình duyệt.")

    def run_campaign(self, accounts: list, campaign: dict):
        """
        Điều phối chạy chiến dịch có tích hợp Xoay IP và Chế độ Hội thoại Lồng nhau
        """
        self.is_running = True
        mode = campaign.get("mode", "seeding")
        max_threads = int(campaign.get("threads", 1))
        rotate_api_url = campaign.get("rotate_proxy_api", "")
        use_dcom = campaign.get("use_dcom_hilink", False)

        self.log(f"=== BẮT ĐẦU CHIẾN DỊCH (CHẾ ĐỘ: {mode.upper()} - {len(accounts)} NICK - {max_threads} LUỒNG) ===")

        if mode == "thread_reply" and len(accounts) >= 2:
            # KỊCH BẢN SEEDING LỒNG NHAU THEO CẶP (PAIR CONVERSATION)
            self.log("[Thread Mode] Chạy theo cặp: Nick 1 hỏi mồi -> Nick 2 vào trả lời mồi...")
            for i in range(0, len(accounts), 2):
                if not self.is_running:
                    break
                acc1 = accounts[i]
                acc2 = accounts[i+1] if i+1 < len(accounts) else None

                # Nick 1 comment hỏi
                self.log(f">> [Cặp {i//2 + 1}] Bắt đầu Nick mồi ({acc1.get('uid')})...")
                ok1, cmt_text = self.process_single_account(acc1, campaign)

                if use_dcom:
                    NetworkRotator.rotate_dcom_hilink()
                elif rotate_api_url:
                    NetworkRotator.rotate_via_api(rotate_api_url)

                if ok1 and cmt_text and acc2:
                    wait_reply = random.randint(15, 30)
                    self.log(f">> [Cặp {i//2 + 1}] Nghỉ {wait_reply}s rồi cho Nick 2 ({acc2.get('uid')}) vào Reply...")
                    time.sleep(wait_reply)
                    self.process_single_account(acc2, campaign, thread_reply_target=cmt_text)

                    if use_dcom:
                        NetworkRotator.rotate_dcom_hilink()
                    elif rotate_api_url:
                        NetworkRotator.rotate_via_api(rotate_api_url)

        else:
            # CHẾ ĐỘ THƯỜNG HOẶC FARM
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = []
                for acc in accounts:
                    if not self.is_running:
                        break
                    futures.append(executor.submit(self.process_single_account, acc, campaign))
                    # Xoay IP giữa các nick nếu chạy đơn luồng
                    if max_threads == 1:
                        if use_dcom:
                            NetworkRotator.rotate_dcom_hilink()
                        elif rotate_api_url:
                            NetworkRotator.rotate_via_api(rotate_api_url)

                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        self.log(f"[Error] {e}")

        self.is_running = False
        self.log("=== HOÀN TẤT CHIẾN DỊCH! ===")
