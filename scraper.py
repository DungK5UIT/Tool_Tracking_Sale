import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
import json
import re
import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# --- CẤU HÌNH SDK GEMINI ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    print("⚠️ CẢNH BÁO: Chưa cấu hình GEMINI_API_KEY trong file .env!")

def check_html_fallback(soup):
    """
    CÁCH 1: Dùng luật cứng (HTML + Regex) để check trước nhằm TIẾT KIỆM TOKEN.
    """
    # 1. Check các thẻ ẩn SEO (Độ chính xác cực cao trên Shopify/Haravan)
    meta_og = soup.find('meta', property='og:availability')
    if meta_og:
        content = meta_og.get('content', '').lower()
        if content in ['out of stock', 'outofstock']:
            return "soldout"
        elif content in ['in stock', 'instock']:
            return "available"
            
    link_schema = soup.find('link', itemprop='availability')
    if link_schema:
        href = link_schema.get('href', '').lower()
        if 'outofstock' in href:
            return "soldout"
        elif 'instock' in href:
            return "available"

    # 2. Check các nút mua hàng dựa trên ID và Class quen thuộc
    cart_buttons = soup.find_all(['button', 'a', 'input'], attrs={'id': re.compile(r'(add-to-cart|buy-now|btn-buy)', re.I)})
    cart_buttons += soup.find_all(['button', 'a', 'input'], class_=re.compile(r'(add-to-cart|addtocart|btn-cart|buy-now)', re.I))

    keywords_soldout = [
        # Tiếng Việt, Tiếng Anh
        r"hết\s+hàng", r"het\s+hang", r"sold\s*out", r"out\s+of\s+stock", r"tạm\s+hết",
        # Tiếng Nhật
        r"品切れ", r"在庫切れ", r"完売", r"売り切れ",
        # Tiếng Hàn
        r"재고없음", r"품절",  
        # Tiếng Trung
        r"已售完", r"已售罄", r"缺货",
        # Tiếng Pháp
        r"épuisé", r"rupture\s+de\s+stock",
        # Tiếng Tây Ban Nha
        r"agotado", r"sin\s+stock",
        # Tiếng Đức
        r"ausverkauft", r"nicht\s+auf\s+lager",
        # Tiếng Ý
        r"esaurito",
        # Tiếng Thái
        r"สินค้าหมด"
    ]
    
    # Từ khóa chỉ định rõ ràng là CÓ HÀNG để chốt luôn, tránh việc có nút giỏ hàng nhưng thật ra không bấm được do JS
    keywords_available = [
        r"thêm\s+vào\s+giỏ", r"mua\s+ngay", r"add\s+to\s+cart", r"buy\s+now",
        # Nhất, Hàn, Trung
        r"カートに入れる", r"장바구니", r"加入购物车", r"立即购买"
    ]

    if cart_buttons:
        for btn in cart_buttons:
            if btn.has_attr('disabled') or 'disabled' in btn.get('class', []):
                return "soldout"
            
            btn_text = re.sub(r'\s+', ' ', btn.get_text().lower().strip())
            
            for kw in keywords_soldout:
                if re.search(kw, btn_text):
                    return "soldout"
                    
            for kw in keywords_available:
                if re.search(kw, btn_text):
                    # Nếu nút hiển thị rõ ràng "Mua ngay" và không bị disabled -> Hàng còn
                    return "available"

    return None


def clean_html_to_text(soup):
    """
    Hàm lọc bỏ bớt rác HTML (script, style) để lấy text sạch
    """
    clean_soup = BeautifulSoup(str(soup), "html.parser")
    for element in clean_soup(["script", "style", "footer", "header", "nav"]):
        element.decompose()
        
    text = clean_soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    clean_text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return clean_text


def ask_gemini_status(web_text):
    """
    Gửi văn bản thô sang Gemini dùng SDK mới (google-genai)
    """
    if not client:
        print("❌ Lỗi: Gemini Client chưa được khởi tạo (thiếu API Key).")
        return "error"
        
    # GIỚI HẠN TEXT TRUYỀN VÀO để tránh lỗi Token Limit Exceeded và tốn phí (Bug #5)
    MAX_CHARS = 10000 
    truncated_text = web_text[:MAX_CHARS]
    
    prompt = f"""
    Bạn là một trợ lý kiểm tra kho hàng tự động. Dưới đây là nội dung văn bản trích xuất từ trang sản phẩm (đã được cắt ngắn).
    Phân tích nội dung trang và xác định xem sản phẩm này hiện tại CÒN HÀNG (available) hay HẾT HÀNG (soldout).
    
    QUY TẮC PHÂN TÍCH:
    1. Nếu sản phẩm HẾT HÀNG HOÀN TOÀN (tất cả size/màu/phiên bản) -> "soldout"
    2. Nếu sản phẩm CÒN ÍT NHẤT 1 SIZE/MÀU/PHIÊN BẢN có thể mua được -> "available"
    3. Chú ý các từ khóa hết hàng có thể bằng NHIỀU NGÔN NGỮ: "sold out", "out of stock", "品切れ" (JP), "재고없음" (KR), "已售完" (CN), v.v.
    4. Các dấu hiệu hết hàng phổ biến: nút mua hàng bị mờ (disabled), giá bị gạch ngang nhưng không có giá mới, form yêu cầu "thông báo khi có hàng" (notify me).
    5. Chỉ trả về duy nhất chuỗi JSON: {{"status": "available"}} hoặc {{"status": "soldout"}} hoặc {{"status": "unknown"}} (nếu không thể xác định).
    
    NỘI DUNG VĂN BẢN TRANG WEB:
    {truncated_text}
    """
    
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            
            result_text = response.text.strip()
            data = json.loads(result_text)
            status = data.get("status", "unknown")
            # Trả về soldout/available, hoặc unknown nếu không chắc chắn
            if status in ["available", "soldout"]:
                return status
            return "unknown"
            
        except Exception as e:
            print(f"❌ Lỗi khi gọi API Gemini (lần thử {attempt + 1}): {e}")
            
    return "error"


def check_url_only(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        print(f"🌐 Đang tải dữ liệu từ trang web...")
        # TĂNG TIMEOUT để tránh lỗi với các trang tải chậm (Bug #7)
        res = requests.get(url, headers=headers, timeout=25) 
        if res.status_code != 200:
            print(f"❌ Lỗi HTTP: {res.status_code}")
            return "error"

        soup = BeautifulSoup(res.text, "html.parser")
        
        # --- BƯỚC 1: KIỂM TRA BẰNG CƠ CHẾ THẺ HTML TRƯỚC ---
        html_result = check_html_fallback(soup)
        if html_result == "soldout":
            print(f"🎯 Khớp luật cứng HTML! Xác định: SOLDOUT (Tiết kiệm lượt gọi AI)")
            return "soldout"
        elif html_result == "available":
            print(f"🎯 Khớp luật cứng HTML! Xác định: AVAILABLE (Tiết kiệm lượt gọi AI)")
            return "available"
            
        # --- BƯỚC 1.5: VÉT MÁNG BẰNG REGEX TRÊN TEXT SẠCH (Tối ưu chặn đứng lỗi 429) ---
        clean_text = clean_html_to_text(soup)
        keywords = [
            r"hết\s+hàng", r"het\s+hang", r"sold\s*out", r"out\s+of\s+stock",
            r"品切れ", r"在庫切れ", r"完売", r"売り切れ",
            r"재고없음", r"품절",
            r"已售完", r"已售罄", r"缺货"
        ]
        for kw in keywords:
            if re.search(kw, clean_text.lower()):
                print(f"🔍 Khớp Regex vét máng trên text! Xác định: SOLDOUT (Tiết kiệm lượt gọi AI)")
                return "soldout"

        # --- BƯỚC 2: CHỈ GỌI AI KHI CẢ HAI BƯỚC TRÊN KHÔNG THỂ XÁC ĐỊNH ---
        print(f"⚠️ Code HTML & Regex đều không chắc chắn. Buộc phải dùng AI...")
        status = ask_gemini_status(clean_text)
        return status
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Lỗi Request tới URL {url}: {e}")
        return "error"
    except Exception as e:
        print(f"💥 Lỗi không xác định khi xử lý URL {url}: {e}")
        return "error"