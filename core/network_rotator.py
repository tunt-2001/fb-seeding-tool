import time
import requests

class NetworkRotator:
    """
    Quản lý xoay IP:
    1. Đổi IP qua URL API của các dịch vụ Proxy Xoay (TMProxy, Tinsoft, ProxyXoay...)
    2. Đổi IP qua Dcom 4G (Huawei Hilink API hoặc lệnh ngắt/kết nối)
    """

    @staticmethod
    def rotate_via_api(rotate_url: str, timeout: int = 15) -> bool:
        if not rotate_url:
            return False
        try:
            print(f"[*] Đang gửi yêu cầu đổi IP qua API: {rotate_url}")
            res = requests.get(rotate_url, timeout=timeout)
            if res.status_code == 200:
                print(f"[✓] Yêu cầu đổi IP thành công: {res.text[:100]}")
                time.sleep(5)  # Chờ 5 giây để IP mới kích hoạt
                return True
        except Exception as e:
            print(f"[!] Lỗi khi gọi API đổi IP: {e}")
        return False

    @staticmethod
    def rotate_dcom_hilink(gateway_ip: str = "192.168.8.1") -> bool:
        """
        Gửi lệnh ngắt và kết nối lại cho Dcom 4G chuẩn Huawei HiLink để đổi IP mới.
        """
        try:
            print(f"[*] Đang thực hiện ngắt kết nối Dcom 4G ({gateway_ip})...")
            # Ngắt kết nối
            disconnect_payload = "<request><dataswitch>0</dataswitch></request>"
            requests.post(f"http://{gateway_ip}/api/dialup/mobile-dataswitch", data=disconnect_payload, timeout=5)
            time.sleep(3)

            # Kết nối lại
            print(f"[*] Đang kết nối lại Dcom 4G để nhận IP mới...")
            connect_payload = "<request><dataswitch>1</dataswitch></request>"
            requests.post(f"http://{gateway_ip}/api/dialup/mobile-dataswitch", data=connect_payload, timeout=5)
            time.sleep(5)
            print("[✓] Đổi IP Dcom 4G hoàn tất!")
            return True
        except Exception as e:
            print(f"[!] Không thể đổi IP qua Dcom HiLink: {e}")
            return False
