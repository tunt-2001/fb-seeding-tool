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
        Kiểm tra trạng thái tài khoản: Live / Checkpoint 282 / Checkpoint 956 / Wrong Pass
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
            if page.locator("div:has-text('Mật khẩu bạn đã nhập không chính xác'), div:has-text('The password you’ve entered is incorrect'), div:has-text('Wrong Credentials')").first.is_visible(timeout=2000):
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
        Tự động đăng nhập linh hoạt, hỗ trợ mọi giao diện của Facebook.
        """
        try:
            page.goto("https://www.facebook.com/login", timeout=45000)
            HumanBehavior.sleep_random(2.0, 3.0)

            # 1. Điền Email/UID
            email_input = page.locator("input#email, input[name='email'], input[aria-label='Email address or phone number'], input[aria-label='Email hoặc số điện thoại']").first
            if not email_input.is_visible(timeout=5000):
                page.goto("https://www.facebook.com", timeout=30000)
                HumanBehavior.sleep_random(2.0, 3.0)
                email_input = page.locator("input#email, input[name='email']").first

            email_input.click()
            email_input.fill("")
            email_input.press_sequentially(uid, delay=50)
            HumanBehavior.sleep_random(0.5, 1.0)

            # 2. Điền mật khẩu
            pass_input = page.locator("input#pass, input[name='pass'], input[aria-label='Password'], input[aria-label='Mật khẩu']").first
            pass_input.click()
            pass_input.fill("")
            pass_input.press_sequentially(password, delay=50)
            HumanBehavior.sleep_random(0.8, 1.2)

            # 3. Thực hiện submit: Tìm nút Đăng nhập hoặc nhấn Enter
            submitted = False
            login_buttons = [
                "button#loginbutton",
                "button[name='login']",
                "button[data-testid='royal_login_button']",
                "button[type='submit']",
                "div[aria-label='Đăng nhập'][role='button']",
                "div[aria-label='Log In'][role='button']"
            ]

            for selector in login_buttons:
                btn = page.locator(selector).first
                try:
                    if btn.is_visible(timeout=1500):
                        btn.click()
                        submitted = True
                        break
                except Exception:
                    continue

            # Fallback nếu không bấm được nút: Nhấn phím Enter trên ô mật khẩu
            if not submitted:
                pass_input.press("Enter")

            HumanBehavior.sleep_random(4.0, 6.0)

            # 4. Kiểm tra Checkpoint hoặc sai pass ngay sau khi submit
            status = FacebookAuth.check_account_health(page)
            if "Checkpoint" in status or status == "Wrong Password":
                return False, status

            # 5. Xử lý màn hình 2FA (nếu có)
            two_fa_input = page.locator("input#approvals_code, input[name='approvals_code'], input[type='number']").first
            try:
                if two_fa and two_fa_input.is_visible(timeout=4000):
                    otp_code = FacebookAuth.get_totp_code(two_fa)
                    two_fa_input.click()
                    two_fa_input.fill(otp_code)
                    HumanBehavior.sleep_random(1.0, 1.5)
                    
                    # Bấm xác nhận OTP hoặc Enter
                    submit_2fa = page.locator("button#checkpointSubmitButton, button[type='submit'], button:has-text('Tiếp tục'), button:has-text('Continue')").first
                    if submit_2fa.is_visible(timeout=2000):
                        submit_2fa.click()
                    else:
                        two_fa_input.press("Enter")

                    HumanBehavior.sleep_random(4.0, 6.0)

                    # Bấm Lưu trình duyệt nếu được hỏi
                    save_btn = page.locator("button#checkpointSubmitButton, button[type='submit'], button:has-text('Tiếp tục'), button:has-text('Continue')").first
                    if save_btn.is_visible(timeout=3000):
                        save_btn.click()
                        HumanBehavior.sleep_random(3.0, 5.0)
            except Exception:
                pass

            # 6. Kiểm tra lại kết quả cuối cùng
            final_status = FacebookAuth.check_account_health(page)
            if final_status == "Live":
                return True, "Live"
            return False, final_status

        except Exception as e:
            return False, f"Error: {e}"
