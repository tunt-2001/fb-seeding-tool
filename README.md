# 🚀 HỆ THỐNG FB SEEDING PRO (v3.0 ENTERPRISE)

> **Hệ thống Seeding & Nuôi Nick Facebook Tự Động Hóa Chuyên Nghiệp**  
> Tích hợp Trình duyệt Anti-detect, Tự động giải mã 2FA, Xoay IP Dcom/Proxy, Seeding Lồng Nhau và **Điều Khiển Từ Xa Qua Nhóm Telegram**.

---

## 📑 MỤC LỤC
1. [Tính năng cốt lõi](#-tính-năng-cốt-lõi)
2. [Cài đặt & Khởi động 1-Click](#-cài-đặt--khởi-động-1-click)
3. [Hướng dẫn sử dụng Web Dashboard](#-hướng-dẫn-sử-dụng-web-dashboard)
4. [Hướng dẫn điều khiển qua Nhóm Telegram](#-hướng-dẫn-điều-khiển-qua-nhóm-telegram)
5. [Quy chuẩn định dạng Via & Proxy](#-quy-chuẩn-định-dạng-via--proxy)
6. [Lời khuyên an toàn từ CTO](#-lời-khuyên-an-toàn-từ-cto)

---

## 🌟 TÍNH NĂNG CỐT LÕI

* **Anti-detect Browser & Multi-profile:** Mỗi nick sở hữu một thư mục Profile độc lập (`profiles/profile_{UID}`), lưu Cookie, LocalStorage và phiên đăng nhập vĩnh viễn, không lo bị văng tài khoản.
* **Auto 2FA Login:** Tự động giải mã mã OTP 6 số từ mã bí mật 2FA (`TOTP`) và điền form đăng nhập Facebook.
* **Xoay IP Linh Hoạt (Chống chết chùm nick):**
  * Tự động ngắt/kết nối lại qua **Dcom 4G (Huawei HiLink 192.168.8.1)**.
  * Tự động gọi **API xoay Proxy** (TMProxy, Tinsoft, ProxyFb...).
  * Gắn Proxy riêng cố định cho từng tài khoản.
* **3 Chế Độ Hoạt Động:**
  1. `Seeding Thường`: Cuộn trang làm ấm, thả cảm xúc Like, gõ comment tự nhiên.
  2. `Seeding Lồng Nhau (Thread Reply)`: Chạy theo cặp tài khoản: Nick 1 hỏi mồi $\rightarrow$ Nick 2 tự động tìm comment của Nick 1 và bấm Trả Lời (Reply).
  3. `Nuôi Nick (Farm Mode)`: Lướt Newsfeed 2–5 phút, xem video Reels, like dạo bạn bè để tăng trust cho nick mới mua.
* **Tự Động Bắt Lỗi & Checkpoint:** Phát hiện Checkpoint 282 (quét mặt), 956 (két sắt), sai pass và tự động bỏ qua nick lỗi.
* **Telegram Remote Control:** Điều khiển từ xa qua điện thoại hoặc nhóm Telegram, tự động **chụp ảnh màn hình bằng chứng (Screenshot)** gửi vào nhóm sau khi comment.

---

## ⚡ CÀI ĐẶT & KHỞI ĐỘNG 1-CLICK

Hệ thống được trang bị bộ khởi động thông minh (`Smart Bootstrapper`):

1. **Tải/Clone mã nguồn về máy tính.**
2. Bấm đúp chuột vào file **`run.bat`**:
   * Nếu máy tính **chưa có Python**: Tool sẽ tự động tải Python 3.12 từ `python.org` và tự cài đặt ngầm.
   * Nếu máy tính **chưa có thư viện**: Tool tự động chạy `pip install -r requirements.txt`.
   * Tự động cài đặt trình duyệt Chromium của Playwright.
   * Tự động mở giao diện điều khiển trên trình duyệt tại: **`http://127.0.0.1:8000`**.

---

## 🖥️ HƯỚNG DẪN SỬ DỤNG WEB DASHBOARD

Giao diện Web gồm 3 cột làm việc:

### 1. Quản lý Dàn Nick (Cột Trái):
* Dán danh sách Via theo định dạng: `UID|Pass|2FA|Cookie|Proxy` (mỗi nick 1 dòng).
* Bấm **Nạp thêm tài khoản**.
* Bảng danh sách bên dưới sẽ hiển thị trạng thái của từng nick:
  * 🟢 `Live`: Nick hoạt động tốt, đã đăng nhập.
  * 🔴 `Checkpoint (282 / 956)`: Nick bị xác minh.
  * ⚪ `Ready`: Sẵn sàng cho chiến dịch mới.

### 2. Cấu hình Kịch bản (Cột Giữa):
* **Chế độ hoạt động:** Chọn `Seeding Thường`, `Seeding Lồng Nhau`, hoặc `Nuôi Nick`.
* **Link bài viết:** Dán URL bài viết Facebook (Fanpage hoặc Group).
* **Số luồng (Threads):** Số nick chạy song song cùng lúc (khuyên dùng 1-2 luồng nếu dùng Dcom xoay IP).
* **Nội dung Bình luận:** Nhập danh sách comment (mỗi dòng một câu, hệ thống sẽ random tự nhiên).
* **Điều khiển từ xa (Telegram):**
  * Nhập `Bot Token` và `Your Chat ID`.
  * Bấm nút **Test Gửi** để kiểm tra kết nối tới Telegram.
* Bấm **Lưu Cấu Hình Chiến Dịch** và bấm **BẮT ĐẦU**.

### 3. Nhật Ký Hoạt Động (Cột Phải):
* Hiển thị log chi tiết thời gian thực: tiến trình đăng nhập, lướt trang, like, gõ comment của từng nick.

---

## 📱 HƯỚNG DẪN ĐIỀU KHIỂN QUA NHÓM TELEGRAM

Bạn và cả team có thể để máy tính chạy ở nhà/văn phòng và điều khiển trực tiếp ngay trong **Nhóm Telegram**:

### Bảng Lệnh Điều Khiển:

| Lệnh | Ý nghĩa | Cách thức hoạt động |
| :--- | :--- | :--- |
| **`/status`** | Kiểm tra hệ thống | Bot trả về: Máy có online không, tổng số nick, số nick Live, số nick Checkpoint. |
| **`/seed <link_fb>`** | Chạy Seeding bài viết | Dán link bài viết sau lệnh (Ví dụ: `/seed https://facebook.com/...`). Dàn nick sẽ tự mở lên like, comment và **gửi ảnh chụp màn hình bằng chứng vào nhóm**. |
| **`/farm`** | Nuôi dàn nick | Kích hoạt chế độ lướt Newsfeed và xem video Reels cho toàn bộ dàn nick. |
| **`/stop`** | Dừng khẩn cấp | Dừng ngay lập tức toàn bộ các luồng và đóng trình duyệt. |
| **`/help`** | Hướng dẫn | Hiển thị lại danh sách câu lệnh. |

> **Bằng chứng thực tế:** Sau khi mỗi nick comment thành công, Bot sẽ tự động gửi một bức ảnh chụp màn hình kèm câu comment vào trong Nhóm để cả team cùng theo dõi kết quả.

---

## 📋 QUY CHUẨN ĐỊNH DẠNG VIA & PROXY

* **Định dạng đầy đủ:**
  ```text
  100089283748291|MatKhau123|JBSWY3DPEHPK3PXP||127.0.0.1:8080
  ```
* **Định dạng có Proxy có User/Pass:**
  ```text
  100089283748291|MatKhau123|JBSWY3DPEHPK3PXP||1.2.3.4:8080:username:password
  ```
* **Định dạng không dùng Proxy riêng (dùng Dcom / Mạng chung):**
  ```text
  100089283748291|MatKhau123|JBSWY3DPEHPK3PXP
  ```

---

## 🛡️ LỜI KHUYÊN AN TOÀN TỪ CTO

1. **Đối với Nick Via mới mua về:** Không nên đem đi seeding link bài viết ngay. Hãy bật chế độ `/farm` (Nuôi nick) cho nick lướt Newsfeed và xem video Reels trong 1–2 ngày đầu để Facebook nhận diện thiết bị và tăng điểm tin cậy (Trust Score).
2. **Tần suất Seeding an toàn:** Mỗi nick không nên comment quá 3–5 bài viết/ngày.
3. **Giãn cách thời gian:** Nếu chạy nhiều nick, nên cấu hình thời gian nghỉ giữa 2 nick từ 30s đến 90s và bật chế độ đổi IP Dcom sau mỗi lượt nick.
