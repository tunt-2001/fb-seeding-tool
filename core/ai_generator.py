import os
import random

class AICommentGenerator:
    """
    Sinh nội dung comment tự nhiên theo bối cảnh bài viết bằng Gemini API.
    Nếu chưa có API Key, sẽ tự động lấy ngẫu nhiên từ danh sách dự phòng.
    """
    def __init__(self, api_key: str = None, fallback_comments: list = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.fallback_comments = fallback_comments or [
            "Shop cho mình xin thêm thông tin sản phẩm với ạ",
            "Mẫu này còn hàng sẵn không bạn ơi?",
            "Tư vấn giúp mình nhé shop",
            "Sản phẩm dùng rất thích, cảm ơn shop nhiều nhé!",
            "Chất lượng ổn áp so với tầm giá, mn nên thử nha"
        ]
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[AI Warning] Không thể khởi tạo Gemini Client: {e}")

    def generate(self, post_text: str = "", persona: str = "khách mua hàng tò mò") -> str:
        if not self.client or not post_text:
            return random.choice(self.fallback_comments)

        prompt = (
            f"Bạn là một người dùng Facebook bình thường tại Việt Nam ({persona}). "
            f"Dưới đây là nội dung bài viết bán hàng:\n'{post_text}'\n\n"
            f"Hãy viết 1 câu bình luận ngắn gọn (dưới 20 từ) thật tự nhiên, chân thật, "
            f"không dùng từ ngữ quảng cáo thô thiển, thỉnh thoảng có thể viết tắt nhẹ (e.g. ko, mk, ship). "
            f"Chỉ trả về duy nhất nội dung bình luận, không giải thích gì thêm."
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            comment = response.text.strip().replace('"', '')
            return comment if comment else random.choice(self.fallback_comments)
        except Exception as e:
            print(f"[AI Warning] Lỗi khi gọi Gemini ({e}), dùng comment dự phòng.")
            return random.choice(self.fallback_comments)
