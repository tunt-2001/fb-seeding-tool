import re
import pyotp
import time
from playwright.sync_api import Page
from core.human_behavior import HumanBehavior

class FacebookAuth:
    """
    Xử lý kiểm tra trạng thái đăng nhập, phát hiện Checkpoint và tự động đăng nhập 2FA.
    """
    @staticmethod
    def get_totp_code(secret_key: str) -> str:
        clean_secret = secret_key.replace(" ", "").strip()
        totp = pyotp.TOTP(clean_secret)
        return totp.now()

    @staticmethod
    def check_account_health(page: Page) -> str:
        """
        Kiểm tra trạng thái tài khoản:
        - "Live": Bình thường, đã đăng nhập
        - "Not_Logged_In": Chưa đăng nhập
        - "Checkpoint_956": Két sắt xác minh
        - "Checkpoint_282": Bắt up ảnh khuôn mặt
        - "Checkpoint_General": Các dạng xác minh khác
        - "Wrong_Password": Sai mật khẩu
        """
        current_url = page.url.lower()

        if "checkpoint" in current_url:
            content = page.content().lower()
            if "282" in current_url or "tải lên hình ảnh" in content or "upload your id" in content:
                return "Checkpoint (282)"
            elif "956" in current_url or "tài khoản của bạn đã bị khóa" in content or "your account has been locked" in content:
                return "Checkpoint (956)"
            return "Checkpoint"

        try:
            # Nếu thấy thanh tìm kiếm Facebook hoặc avatar -> Live
            if page.locator("input[aria-label='Tìm kiếm trên Facebook'], input[aria-label='Search Facebook'], div[aria-label='Tài khoản của bạn'], div[aria-label='Your profile']").first.is_visible(timeout=3000):
                return "Live"

            # Nếu có thông báo sai mật khẩu
            if page.locator("div:has-text('Mật khẩu bạn đã nhập không chính xác'), div:has-text('The password you’ve entered is incorrect')").first.is_visible(timeout=2000):
                return "Wrong Password"

            # Nếu ở trang login
            if page.locator("input#email, input[name='email']").first.is_visible(timeout=2000):
                return "Not Logged In"
        except Exception:
            pass

        return "Unknown"

    @staticmethod
    def auto_login(page: Page, uid: str, password: str, two_fa: str = "") -> tuple[bool, str]:
        """
        Tự động đăng nhập và trả về (Thành công, Trạng thái chi tiết)
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

            # Kiểm tra Checkpoint hoặc sai pass ngay sau khi bấm nút login
            status = FacebookAuth.check_account_health(page)
            if "Checkpoint" in status or status == "Wrong Password":
                return False, status

            # Xử lý 2FA nếu có
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

                # Lưu trình duyệt này nếu được hỏi
                if page.locator("input[value='dont_save'], input[value='save_device']").first.is_visible(timeout=3000):
                    save_btn = page.locator("button#checkpointSubmitButton, button[type='submit']").first
                    save_btn.click()
                    HumanBehavior.sleep_random(3.0, 5.0)

            # Kiểm tra trạng thái cuối cùng
            final_status = FacebookAuth.check_account_health(page)
            if final_status == "Live":
                return True, "Live"
            return False, final_status
        except Exception as e:
            return False, f"Error: {e}"
