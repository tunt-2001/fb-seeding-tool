import os
import sys
import json
import random
from core.browser_manager import BrowserManager
from core.human_behavior import HumanBehavior
from core.ai_generator import AICommentGenerator

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def setup_login_profile(profile_id: str, proxy: dict = None):
    """
    Mở trình duyệt lên để người dùng đăng nhập Facebook lần đầu cho Profile này.
    Sau khi đăng nhập xong, dữ liệu sẽ được lưu vĩnh viễn trong thư mục profiles/.
    """
    print(f"\n==================================================")
    print(f"[!] Đang mở trình duyệt cho Profile: {profile_id}")
    print(f"[!] Hãy đăng nhập Facebook trên cửa sổ vừa mở.")
    print(f"[!] Khi đăng nhập xong và Facebook đã vào Newsfeed, quay lại đây nhấn ENTER để lưu session.")
    print(f"==================================================")

    manager = BrowserManager()
    try:
        page = manager.start_profile(profile_id=profile_id, proxy=proxy, headless=False)
        page.goto("https://www.facebook.com", timeout=60000)
        input("\n[>>] Nhấn phím ENTER sau khi bạn đã đăng nhập thành công... ")
        print(f"[+] Đã lưu thông tin đăng nhập cho {profile_id} thành công!")
    finally:
        manager.close()

def run_seeding(target_url: str, post_description: str = ""):
    """
    Chạy kịch bản Seeding tự động cho các Profile đã cấu hình.
    """
    config = load_config()
    settings = config.get("settings", {})
    profiles = config.get("profiles", [])
    
    ai_gen = AICommentGenerator(
        api_key=settings.get("gemini_api_key"),
        fallback_comments=config.get("sample_comments", [])
    )

    print(f"\n[+] BẮT ĐẦU CHIẾN DỊCH SEEDING")
    print(f"[+] Link bài viết: {target_url}")
    print(f"[+] Tổng số Profile tham gia: {len(profiles)}\n")

    for index, prof in enumerate(profiles, start=1):
        prof_id = prof["id"]
        prof_name = prof.get("name", prof_id)
        proxy = prof.get("proxy")

        print(f"--------------------------------------------------")
        print(f"[{index}/{len(profiles)}] Đang chạy: {prof_name} ({prof_id})")

        # 1. Sinh nội dung comment qua AI hoặc lấy mẫu
        persona = "khách hỏi mua hàng tò mò" if index % 2 != 0 else "khách review khen ngợi"
        comment_content = ai_gen.generate(post_text=post_description, persona=persona)
        print(f"[*] Nội dung comment dự kiến: \"{comment_content}\"")

        manager = BrowserManager()
        try:
            page = manager.start_profile(
                profile_id=prof_id,
                proxy=proxy,
                headless=settings.get("headless", False)
            )

            print(f"[*] Đang truy cập bài viết...")
            page.goto(target_url, timeout=60000)
            HumanBehavior.sleep_random(3.0, 5.0)

            # 2. Bước làm ấm phiên (Warm-up)
            print(f"[*] Đang mô phỏng lướt xem bài viết (Warm-up)...")
            HumanBehavior.natural_scroll(page, times=random.randint(2, 4))

            # 3. Thả Like bài viết (nếu tìm thấy nút Thích)
            try:
                like_btn = page.locator("div[aria-label='Thích'], div[aria-label='Like']").first
                if like_btn.is_visible(timeout=3000):
                    like_btn.click()
                    print(f"[+] Đã bấm Thích bài viết.")
                    HumanBehavior.sleep_random(1.5, 3.0)
            except Exception:
                print(f"[-] Bỏ qua bước like (chưa tìm thấy nút hoặc bài đã like).")

            # 4. Gõ comment tự nhiên
            print(f"[*] Đang định vị ô bình luận...")
            comment_box = page.locator("div[aria-label='Viết bình luận'], div[aria-label='Write a comment'], div[role='textbox']").first
            
            if comment_box.is_visible(timeout=5000):
                comment_box.click()
                HumanBehavior.sleep_random(1.0, 2.0)
                
                # Gõ phím kiểu người thật
                min_t, max_t = settings.get("typing_delay_ms", [60, 180])
                for char in comment_content:
                    comment_box.press_sequentially(char, delay=random.randint(min_t, max_t))
                
                HumanBehavior.sleep_random(1.0, 2.0)
                comment_box.press("Enter")
                print(f"[✓] Đã gửi bình luận thành công!")
                
                # Ngắm lại bài một chút trước khi thoát
                HumanBehavior.sleep_random(5.0, 8.0)
            else:
                print(f"[!] Không tìm thấy ô comment (Có thể chưa đăng nhập hoặc bài viết khóa cmt).")

        except Exception as e:
            print(f"[!] Lỗi khi chạy {prof_id}: {e}")
        finally:
            manager.close()

        # Nghỉ giữa 2 profile để tránh Facebook quét bất thường
        if index < len(profiles):
            min_d, max_d = settings.get("default_delay_between_profiles_seconds", [15, 30])
            delay = random.uniform(min_d, max_d)
            print(f"[~] Đang nghỉ {delay:.1f}s trước khi chuyển sang Profile tiếp theo...")
            HumanBehavior.sleep_random(delay, delay + 2)

    print(f"\n[✓] HOÀN TẤT CHIẾN DỊCH SEEDING!")

def main():
    while True:
        print("\n" + "="*50)
        print("     HỆ THỐNG SEEDING FACEBOOK NỘI BỘ (ANTI-DETECT)")
        print("="*50)
        print("1. Đăng nhập / Khởi tạo Profile Nick mới (Lưu Cookie/Session)")
        print("2. Chạy Seeding bài viết (Fanpage / Group)")
        print("3. Thoát")
        
        choice = input("\nChọn chức năng (1-3): ").strip()
        
        if choice == "1":
            prof_id = input("Nhập mã Profile (ví dụ: profile_01, nick_dung, ...): ").strip()
            if not prof_id:
                prof_id = "profile_01"
            setup_login_profile(prof_id)
            
        elif choice == "2":
            url = input("Dán link bài viết Facebook cần seeding: ").strip()
            if not url:
                print("[!] Link không được để trống!")
                continue
            desc = input("Nhập tóm tắt sản phẩm (để AI sinh cmt phù hợp, hoặc bấm Enter để dùng cmt mẫu): ").strip()
            run_seeding(url, desc)
            
        elif choice == "3":
            print("Tạm biệt!")
            break
        else:
            print("[!] Lựa chọn không hợp lệ, vui lòng chọn lại.")

if __name__ == "__main__":
    main()
