# FB SEEDING PRO (v2.0 Industrial)

Hệ thống Seeding & Nuôi Nick Facebook tự động hóa toàn diện, chuyên dụng cho doanh nghiệp/team bán hàng nội bộ.

---

## 🚀 Các Tính Năng Nổi Bật (v2.0)

1. **Anti-detect Browser & Persistent Profiles:**
   * Mỗi nick sở hữu một thư mục Profile riêng biệt (`profiles/profile_{UID}`), lưu Cookie/Session vĩnh viễn, không lo bị đăng xuất.
   * Che giấu cờ `navigator.webdriver` và giả mạo vân tay trình duyệt.

2. **Auto 2FA Login:**
   * Tự động giải mã OTP từ mã bí mật 2FA (`TOTP`) và điền form đăng nhập Facebook mà không cần thao tác tay.

3. **Cơ Chế Xoay IP Đa Dạng (Chống Trảm Cụm Nick):**
   * Hỗ trợ đổi IP qua **Dcom 4G (Huawei HiLink 192.168.8.1)**.
   * Hỗ trợ đổi IP qua **Link API của các dịch vụ Proxy Xoay** (TMProxy, Tinsoft, ProxyFb...).
   * Hỗ trợ gắn Proxy tĩnh cố định cho từng tài khoản.

4. **3 Chế Độ Hoạt Động Chuyên Sâu:**
   * **Chế độ 1: Seeding Thường:** Cuộn trang, thả cảm xúc Like, gõ comment người thật.
   * **Chế độ 2: Seeding Lồng Nhau (Thread Reply):** Chạy theo từng cặp tài khoản: Nick 1 hỏi mồi $\rightarrow$ Nick 2 tự động tìm đúng comment của Nick 1 để bấm Trả Lời (Reply).
   * **Chế độ 3: Nuôi Nick (Farm Mode):** Tự động lướt Newsfeed 2–5 phút, xem video Reels/Watch, like dạo bài viết bạn bè để tăng độ Trust cho nick mới mua.

5. **Giám Sát Sức Khỏe & Nhận Diện Checkpoint:**
   * Tự động phát hiện các dạng Checkpoint phổ biến: `Checkpoint 282` (quét mặt), `Checkpoint 956` (két sắt), `Sai Pass`.
   * Hiển thị Badge trạng thái trực quan trên Dashboard và tự động bỏ qua nick lỗi để không làm nghẽn chiến dịch.

---

## 🛠️ Hướng Dẫn Sử Dụng

1. Bấm đúp chuột vào file **`run.bat`**.
2. Trình duyệt sẽ tự động mở trang điều khiển tại: `http://127.0.0.1:8000`.
3. Dán danh sách Via theo định dạng: `UID|Pass|2FA|Cookie|Proxy` vào ô và bấm **Nạp thêm tài khoản**.
4. Chọn chế độ mong muốn (Seeding, Thread Reply, hoặc Nuôi Nick) $\rightarrow$ Bấm **BẮT ĐẦU**.
