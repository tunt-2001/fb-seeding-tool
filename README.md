# HỆ THỐNG SEEDING FACEBOOK NỘI BỘ (ANTI-DETECT & AI)

Tool tự động tương tác, thả Like và Bình luận tự nhiên trên các bài viết Fanpage và Group Facebook, mô phỏng hành vi người thật và lưu session riêng biệt cho từng Profile.

---

## 1. Cấu trúc thư mục

* `main.py`: File chạy chính.
* `run.bat`: Bấm đúp chuột để chạy ngay trên Windows.
* `config.json`: Cấu hình danh sách nick, tốc độ gõ phím, comment mẫu và Gemini API Key.
* `profiles/`: Thư mục tự động tạo, lưu trữ Cookie, LocalStorage và phiên đăng nhập của từng con Nick (không lo bị văng đăng xuất).
* `core/browser_manager.py`: Quản lý trình duyệt Chromium chuẩn Anti-detect (Stealth).
* `core/human_behavior.py`: Giả lập hành vi người thật (Human Typing, cuộn chuột, xem bài).
* `core/ai_generator.py`: Tích hợp Gemini 2.5 Flash để tự động tạo comment tự nhiên theo nội dung bài viết.

---

## 2. Hướng dẫn sử dụng

### Bước 1: Đăng nhập nick lần đầu (Chỉ làm 1 lần cho mỗi nick)
1. Bấm đúp vào file `run.bat` (hoặc mở Terminal gõ `python main.py`).
2. Chọn **Chức năng 1**: `Đăng nhập / Khởi tạo Profile Nick mới`.
3. Nhập ID cho Profile, ví dụ: `profile_01`.
4. Trình duyệt Chromium sẽ tự động bật lên trang Facebook.
5. Bạn tiến hành đăng nhập tài khoản Facebook (nhập mật khẩu, mã 2FA).
6. Sau khi đăng nhập thành công và đã thấy Newsfeed, quay lại cửa sổ dòng lệnh và bấm **ENTER**.
7. *Từ các lần sau, Nick này đã được lưu vĩnh viễn trong `profiles/profile_01`, mở lên là tự động đã đăng nhập sẵn.*

### Bước 2: Cấu hình danh sách Nick chạy seeding
Mở file `config.json` để thêm hoặc sửa danh sách nick bạn muốn chạy trong mục `"profiles"`:
```json
"profiles": [
  { "id": "profile_01", "name": "Nick 1 - Khách hỏi giá", "proxy": null },
  { "id": "profile_02", "name": "Nick 2 - Khách review", "proxy": null }
]
```
*(Nếu dùng Proxy, bạn chỉ cần điền vào mục `"proxy"`: `{"server": "http://ip:port", "username": "...", "password": "..."}`).*

### Bước 3: Chạy chiến dịch Seeding
1. Mở `run.bat`, chọn **Chức năng 2**: `Chạy Seeding bài viết`.
2. Dán link bài viết Facebook (Fanpage hoặc Group).
3. Nhập 1 câu mô tả ngắn về sản phẩm bài viết (hoặc nhấn Enter để dùng comment mẫu).
4. Tool sẽ tuần tự mở từng Profile $\rightarrow$ Lướt đọc bài (Warm-up) $\rightarrow$ Thả Like $\rightarrow$ Gõ comment tự nhiên $\rightarrow$ Nghỉ một chút rồi đóng lại.

---

## 3. Lưu ý an toàn từ CTO:
* Không nên tăng tốc độ gõ phím quá nhanh (giữ mặc định `60ms - 180ms` mỗi ký tự).
* Giữa 2 nick nên có thời gian nghỉ từ `30s - 120s`.
* Mỗi nick không nên comment quá 3 - 5 bài/ngày để giữ độ trust cho tài khoản.
