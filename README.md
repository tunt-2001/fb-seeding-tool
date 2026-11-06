# FB SEEDING PRO (v3.0 Telegram Remote Control)

Hệ thống Seeding & Nuôi Nick Facebook tự động hóa toàn diện, chuyên dụng cho doanh nghiệp/team bán hàng nội bộ. Hỗ trợ điều khiển và nhận báo cáo từ xa qua Telegram.

---

## 🚀 Các Tính Năng Đỉnh Cao (v3.0)

1. **Điều Khiển Từ Xa Qua Telegram Bot:**
   * Cắm máy ở nhà/văn phòng, đi ra ngoài mở điện thoại nhắn tin Telegram để điều khiển:
     * `/status`: Kiểm tra máy tính có online không, dàn nick có bao nhiêu con Live / Checkpoint.
     * `/seed <link_bai_viet>`: Tự động chạy seeding vào bài viết.
     * `/farm`: Kích hoạt chế độ nuôi nick (lướt Newsfeed, Reels).
     * `/stop`: Dừng khẩn cấp toàn bộ hệ thống.
   * **Báo cáo bằng chứng thực tế:** Tự động **chụp ảnh màn hình (Screenshot)** bài viết sau khi comment thành công và gửi thẳng về Telegram của bạn.
   * **Cảnh báo Checkpoint:** Tự động báo động đỏ ngay khi nick dính Checkpoint (282, 956).

2. **Smart 1-Click Installer (`run.bat`):**
   * Người nhận tool không cần biết cài Python hay thư viện. Chỉ cần click đúp `run.bat`, hệ thống tự phát hiện và tự động tải cài đặt 100%.

3. **Cơ Chế Xoay IP Đa Dạng (Chống Trảm Cụm Nick):**
   * Tự động đổi IP qua **Dcom 4G (Huawei HiLink 192.168.8.1)** hoặc **Link API Proxy Xoay** (TMProxy, Tinsoft...).

4. **3 Chế Độ Hoạt Động:**
   * **Seeding Thường:** Cuộn trang, thả cảm xúc Like, gõ comment người thật.
   * **Seeding Lồng Nhau (Thread Reply):** Nick 1 hỏi mồi $\rightarrow$ Nick 2 tự động tìm comment của Nick 1 để Reply.
   * **Nuôi Nick (Farm Mode):** Lướt Newsfeed 2–5 phút, xem video Reels/Watch, like dạo bài viết bạn bè.

---

## 📱 Cách Lấy Telegram Bot Token & Chat ID (1 Phút)

1. **Lấy Bot Token:**
   * Mở Telegram, tìm kiếm **`@BotFather`** $\rightarrow$ bấm Start $\rightarrow$ gõ lệnh `/newbot`.
   * Đặt tên cho bot $\rightarrow$ BotFather sẽ gửi cho bạn một chuỗi **HTTP API Token** (dạng `7123456789:AAH...`).
2. **Lấy Chat ID của bạn:**
   * Tìm kiếm **`@userinfobot`** trên Telegram $\rightarrow$ bấm Start $\rightarrow$ Nó sẽ hiện ra dòng **`Id: 123456789`**.
3. **Cấu hình:**
   * Dán Token và Chat ID vào khung **Điều Khiển Từ Xa (Telegram)** trên Dashboard $\rightarrow$ bấm **Test Gửi** là xong!
