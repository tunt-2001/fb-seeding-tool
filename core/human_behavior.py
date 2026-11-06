import time
import random
from playwright.sync_api import Page

class HumanBehavior:
    """
    Mô phỏng hành vi tự nhiên của con người trên trình duyệt để tránh bị Meta AI gắn cờ Spam.
    """

    @staticmethod
    def sleep_random(min_seconds: float, max_seconds: float):
        duration = random.uniform(min_seconds, max_seconds)
        time.sleep(duration)

    @staticmethod
    def human_type(page: Page, selector: str, text: str, min_delay_ms: int = 60, max_delay_ms: int = 180):
        """
        Gõ từng ký tự với độ trễ ngẫu nhiên giống như tay người thật gõ bàn phím.
        """
        element = page.locator(selector).first
        element.click()
        HumanBehavior.sleep_random(0.5, 1.2)

        for char in text:
            element.press_sequentially(char, delay=random.randint(min_delay_ms, max_delay_ms))
            # 5% xác suất người dùng dừng lại suy nghĩ một nhịp nhỏ
            if random.random() < 0.05:
                HumanBehavior.sleep_random(0.3, 0.8)

    @staticmethod
    def natural_scroll(page: Page, times: int = 3):
        """
        Cuộn trang lên xuống nhẹ nhàng như đang đọc nội dung bài viết.
        """
        for _ in range(times):
            scroll_distance = random.randint(200, 450)
            page.mouse.wheel(0, scroll_distance)
            HumanBehavior.sleep_random(1.2, 2.5)

        # Thỉnh thoảng cuộn ngược lên một chút
        if random.random() < 0.5:
            page.mouse.wheel(0, -random.randint(100, 200))
            HumanBehavior.sleep_random(0.8, 1.5)
