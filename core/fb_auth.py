import re
import pyotp
import time
from playwright.sync_api import Page
from core.human_behavior import HumanBehavior

class FacebookAuth:
    """
    Xử lý kiểm tra trạng thái đăng nhập và tự động đăng nhập Facebook bằng UID, Pass và 2FA Secret.
    """
    @staticmethod
    def get_totp_code(secret_key: str) -> str:
        """
        Tự động tính mã 6 số OTP từ mã 2FA Secret của Facebook.
        """
        clean_secret = secret_key.replace(" ", "").strip()
        totp = pyotp.TOTP(clean_secret)
        return totp.now()

    @staticmethod
    def is_logged_in(page: Page) -> bool:
        """
        Kiểm tra xem trang hiện tại đã có phiên đăng nhập Facebook hay chưa.
        """
        try:
            page.goto("https://www.facebook.com", timeout=30000)
            HumanBehavior.sleep_random(2, 3)
            # Nếu thấy thanh tìm kiếm Facebook hoặc avatar -> Đã đăng nhập
            if page.locator("input[aria-label='Tìm kiếm trên Facebook'], input[aria-label='Search Facebook'], div[aria-label='Tài khoản của bạn'], div[aria-label='Your profile']").first.is_visible(timeout=5000):
                return True
            # Nếu thấy form login -> Chưa đăng nhập
            if page.locator("input#email, input[name='email']").first.is_visible(timeout=3000):
                return False
        except Exception:
            pass
        return False

    @staticmethod
    def auto_login(page: Page, uid: str, password: str, two_fa: str = "") -> bool:
        """
        Tự động điền UID, Mật khẩu và mã 2FA để đăng nhập vào Facebook.
        """
        try:
            page.goto("https://www.facebook.com/login", timeout=40000)
            HumanBehavior.sleep_random(1.5, 2.5)

            # Điền tài khoản
            email_input = page.locator("input#email, input[name='email']").first
            email_input.click()
            email_input.fill(uid)
            HumanBehavior.sleep_random(0.5, 1.0)

            # Điền mật khẩu
            pass_input = page.locator("input#pass, input[name='pass']").first
            pass_input.click()
            pass_input.fill(password)
            HumanBehavior.sleep_random(0.8, 1.5)

            # Bấm nút Đăng nhập
            login_btn = page.locator("button#loginbutton, button[name='login']").first
            login_btn.click()
            HumanBehavior.sleep_random(3.0, 5.0)

            # Kiểm tra nếu có màn hình yêu cầu 2FA
            if two_fa and page.locator("input#approvals_code, input[name='approvals_code']").first.is_visible(timeout=5000):
                otp_code = FacebookAuth.get_totp_code(two_fa)
                otp_input = page.locator("input#approvals_code, input[name='approvals_code']").first
                otp_input.click()
                otp_input.fill(otp_code)
                HumanBehavior.sleep_random(1.0, 2.0)
                
                # Bấm xác nhận 2FA
                submit_btn = page.locator("button#checkpointSubmitButton, button[type='submit']").first
                submit_btn.click()
                HumanBehavior.sleep_random(4.0, 6.0)

                # Nếu có hỏi "Lưu trình duyệt này" -> Bấm Tiếp tục/Lưu
                if page.locator("input[value='dont_save'], input[value='save_device']").first.is_visible(timeout=3000):
                    save_btn = page.locator("button#checkpointSubmitButton, button[type='submit']").first
                    save_btn.click()
                    HumanBehavior.sleep_random(3.0, 5.0)

            # Kiểm tra lại xem đã vào được Facebook chưa
            return FacebookAuth.is_logged_in(page)
        except Exception as e:
            print(f"[Login Error] {e}")
            return False
