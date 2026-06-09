import telebot
from telebot.apihelper import ApiTelegramException
import threading
import time
import os
import re
import logging
import concurrent.futures
from collections import defaultdict
from dotenv import load_dotenv

import database as db
import scraper
from api import app as flask_app

# Tải biến môi trường từ file .env
load_dotenv()

# --- CẤU HÌNH TOKEN ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ LỖI: Chưa cấu hình TELEGRAM_TOKEN trong file .env!")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

db.init_db()

from flask import request, abort

@flask_app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

# Cấu hình chu kỳ check ngầm (giây)
CHECK_INTERVAL = 120

def is_valid_url(url):
    """Kiểm tra định dạng URL cơ bản"""
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def safe_reply(message_or_chat_id, text, **kwargs):
    """Try reply_to when possible, fallback to send_message with Rate Limit handling."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if hasattr(message_or_chat_id, 'chat') and hasattr(message_or_chat_id, 'message_id'):
                try:
                    return bot.reply_to(message_or_chat_id, text, **kwargs)
                except Exception:
                    return bot.send_message(str(message_or_chat_id.chat.id), text, **kwargs)

            return bot.send_message(str(message_or_chat_id), text, **kwargs)
            
        except ApiTelegramException as e:
            if e.error_code == 429:
                retry_after = e.result_json.get('parameters', {}).get('retry_after', 1)
                print(f"[RateLimit] Bị Telegram block, chờ {retry_after}s rồi thử lại...")
                time.sleep(retry_after + 0.5)
                continue
            else:
                print(f"[safe_reply] Telegram Error: {e}")
                break
        except Exception as e:
            print(f"[safe_reply] Failed to send message: {e}")
            break
            
    # Nghỉ 0.05s sau mỗi tin nhắn để tránh dồn dập (tối đa 20 tin/giây)
    time.sleep(0.05)
    return None

# --- XỬ LÝ LỆNH BOT ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    user_name = message.from_user.first_name or "Bạn"
    # Đảm bảo lưu profile vào DB khi user /start (auto-register)
    try:
        db.get_or_create_user(chat_id)
        # Cập nhật tên hiển thị nếu có
        if user_name:
            db.set_display_name(chat_id, user_name)
    except Exception:
        pass

    # Gửi ID dưới dạng plain text trước (tránh lỗi Markdown khiến ID không hiển thị)
    try:
        safe_reply(message, f"📱 Telegram ID của bạn: {chat_id}")
    except Exception:
        pass

    DASHBOARD_URL = os.environ.get('DASHBOARD_URL', 'http://localhost:8080')
    dashboard_link = f"{DASHBOARD_URL}/?chat_id={chat_id}"

    # Gửi link dashboard rõ ràng dưới dạng plain text để Telegram không làm mất query param
    try:
        safe_reply(message, f"🔗 Mở dashboard nhanh: {dashboard_link}")
    except Exception:
        pass

    text = (
        f"👋 Chào mừng {user_name}! Đây là Bot Săn Sale Thông Minh.\n\n"
        f"📱 **Telegram ID của bạn:** `{chat_id}`\n"
        f"_(ID này đã được lưu tự động — bạn không cần copy/paste)_\n\n"
        f"🔗 Mở dashboard nhanh: {dashboard_link}\n\n"
        f"🎯 **LỆNH CƠ BẢN:**\n"
        f"`/track [URL]` - Thêm sản phẩm vào theo dõi\n"
        f"`/list` - Xem danh sách sản phẩm đang theo dõi\n"
        f"`/untrack [ID]` - Ngừng theo dõi sản phẩm\n"
        f"`/balance` - Kiểm tra số slot còn lại\n"
        f"`/upgrade` - Mua thêm slot\n"
        f"`/help` - Xem hướng dẫn này lại\n\n"
        f"💡 **HƯỚNG DẪN NHANH:**\n"
        f"1. Bấm link dashboard để mở trang đã tự động nhận ID của bạn\n"
        f"2. Dán link sản phẩm vào ô, bấm 'Theo dõi' — xong!\n"
        f"3. Mỗi tài khoản được 2 link miễn phí\n"
        f"4. Mua thêm: 10.000đ = +1 link\n\n"
        f"📖 Gõ `/guide` để xem hướng dẫn chi tiết"
    )
    safe_reply(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['track'])
def handle_track(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        safe_reply(message, "❌ Vui lòng nhập đúng: `/track [Đường_link]`")
        return
    
    url = parts[1].strip()
    
    # Bổ sung validate URL
    if not is_valid_url(url):
        safe_reply(message, "❌ Lỗi: Đường link không hợp lệ. Vui lòng gửi link có http:// hoặc https://")
        return
        
    chat_id = str(message.chat.id)
    
    # ✅ FIX: Kiểm tra xem user đã đạt giới hạn slot chưa
    current_tracks = len(db.get_tracks_by_chat(chat_id))
    max_tracks = db.get_max_tracks(chat_id)
    
    if current_tracks >= max_tracks:
        slots_needed = current_tracks - max_tracks + 1
        cost = slots_needed * 10000  # 10k per slot
        safe_reply(
            message,
            f"⚠️ Bạn đã đạt giới hạn {max_tracks} link! 🔐\n\n"
            f"Để thêm {slots_needed} link nữa, bạn cần nạp:\n"
            f"💰 {cost:,}đ → +{slots_needed} slot\n\n"
            f"Gõ `/upgrade` để mua thêm slot!",
        )
        return
    
    # Kiểm tra thêm thành công hay bị duplicate
    success = db.add_track(chat_id, url)
    if success:
        safe_reply(message, f"🎯 Đã thêm vào danh sách theo dõi!\n🔗 Bot đang quét ngầm link này...")
    else:
        safe_reply(message, "⚠️ Bạn đã theo dõi đường link này rồi!")

@bot.message_handler(commands=['untrack'])
def handle_untrack(message):
    parts = message.text.split()
    if len(parts) < 2:
        safe_reply(message, "❌ Vui lòng nhập đúng: `/untrack [ID_Sản_Phẩm]`\n(Gõ /list để xem ID)")
        return
        
    try:
        track_id = int(parts[1])
        chat_id = str(message.chat.id)
        
        success = db.remove_track(track_id, chat_id)
        if success:
            safe_reply(message, f"✅ Đã ngừng theo dõi sản phẩm ID: {track_id}")
        else:
            safe_reply(message, f"❌ Không tìm thấy sản phẩm ID: {track_id} trong danh sách của bạn.")
    except ValueError:
        safe_reply(message, "❌ Lỗi: ID sản phẩm phải là một con số.")

@bot.message_handler(commands=['list'])
def handle_list(message):
    # Dùng hàm get_tracks_by_chat thay vì get_all rồi filter
    user_tracks = db.get_tracks_by_chat(str(message.chat.id))
    
    if not user_tracks:
        safe_reply(message, "Bạn chưa theo dõi sản phẩm nào.")
        return
        
    text = "📋 DANH SÁCH ĐANG THEO DÕI:\n\n"
    for t in user_tracks:
        full_url = t['url']
        
        # Format status đẹp hơn
        status_emoji = "⏳"
        if t['last_status'] == "available": status_emoji = "✅"
        elif t['last_status'] == "soldout": status_emoji = "❌"
        elif t['last_status'] == "error": status_emoji = "⚠️"
        
        text += f"🔹 ID: `{t['id']}`\n🔗 Link: {full_url}\n{status_emoji} Trạng thái: *{t['last_status']}*\n\n"
    safe_reply(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['balance'])
def handle_balance(message):
    """Kiểm tra số dư và slot còn lại"""
    chat_id = str(message.chat.id)
    profile = db.get_or_create_user(chat_id)
    current_tracks = len(db.get_tracks_by_chat(chat_id))
    max_tracks = profile['max_tracks']
    
    text = (
        f"👤 Thông tin tài khoản:\n\n"
        f"📊 Slot sử dụng: {current_tracks}/{max_tracks}\n"
        f"💰 Credits nạp: {profile['credits']:,}đ\n"
        f"📱 Telegram ID: `{chat_id}`\n\n"
        f"💡 Mỗi slot = 1 link theo dõi\n"
        f"💳 Mỗi 10.000đ = +1 slot\n\n"
        f"Gõ `/upgrade` để mua thêm slot!"
    )
    safe_reply(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['upgrade'])
def handle_upgrade(message):
    """Hướng dẫn nạp tiền"""
    chat_id = str(message.chat.id)
    PAYMENT_URL = os.environ.get("PAYMENT_URL", "http://localhost:8080/payment")
    # Use plain text to avoid Markdown entity parsing issues
    text = (
        f"💳 NẠPSLOT THÊM - HƯỚNG DẪN:\n\n"
        f"1️⃣ Bấm vào link để mua slot:\n"
        f"👉 {PAYMENT_URL}?chat_id={chat_id}\n\n"
        f"2️⃣ Chọn số lượng slot cần mua\n"
        f"3️⃣ Thanh toán (QR, Transfer)\n"
        f"4️⃣ Sau 5s, slot sẽ tự cộng vào tài khoản\n\n"
        f"❓ Gõ /balance để kiểm tra số slot hiện tại"
    )
    safe_reply(message, text)

@bot.message_handler(commands=['guide'])
def handle_guide(message):
    """Hướng dẫn sử dụng chi tiết"""
    chat_id = str(message.chat.id)
    
    guide_text = (
        "📚 **HƯỚNG DẪN SỬ DỤNG CHI TIẾT**\n\n"
        "═══════════════════════════════════\n"
        "🎯 **1. THÊM SẢN PHẨM VÀO THEO DÕI**\n"
        "═══════════════════════════════════\n\n"
        "*Lệnh:* `/track [URL]`\n\n"
        "*Ví dụ:*\n"
        "`/track https://shopee.vn/product-name`\n"
        "`/track https://lazada.vn/product-name`\n\n"
        "*Kết quả:* Bot bắt đầu theo dõi sản phẩm mỗi 2 phút\n"
        "*Thông báo:* Khi có hàng, bot sẽ gửi tin nhắn ngay\n\n"
        "═══════════════════════════════════\n"
        "📋 **2. XEM DANH SÁCH SẢN PHẨM**\n"
        "═══════════════════════════════════\n\n"
        "*Lệnh:* `/list`\n\n"
        "*Hiển thị:*\n"
        "🔹 ID - số hiệu để xóa\n"
        "🔗 Link - đường link sản phẩm\n"
        "✅/❌/⏳ - Trạng thái (có hàng/hết hàng/đang check)\n\n"
        "═══════════════════════════════════\n"
        "🗑️ **3. NGỪNG THEO DÕI SẢN PHẨM**\n"
        "═══════════════════════════════════\n\n"
        "*Lệnh:* `/untrack [ID]`\n\n"
        "*Ví dụ:* `/untrack 5`\n"
        "_(ID lấy từ lệnh /list)_\n\n"
        "═══════════════════════════════════\n"
        "💰 **4. KIỂM TRA SỐ SLOT**\n"
        "═══════════════════════════════════\n\n"
        "*Lệnh:* `/balance`\n\n"
        "*Hiển thị:*\n"
        "📊 Số slot sử dụng (vd: 2/5)\n"
        "💳 Tổng credits đã nạp\n"
        "📱 Telegram ID của bạn\n\n"
        "═══════════════════════════════════\n"
        "💳 **5. MUA THÊM SLOT**\n"
        "═══════════════════════════════════\n\n"
        "*Bảng giá:*\n"
        "• +1 slot: 10.000đ\n"
        "• +5 slots: 45.000đ (tiết kiệm 5k)\n"
        "• +10 slots: 80.000đ (tiết kiệm 20k)\n"
        "• +20 slots: 150.000đ (tiết kiệm 50k)\n\n"
        "*Lệnh:* `/upgrade`\n\n"
        "*Quy trình:*\n"
        "1. Gõ `/upgrade`\n"
        "2. Bấm link thanh toán\n"
        "3. Chọn gói nạp\n"
        "4. Thanh toán (QR hoặc chuyển khoản)\n"
        "5. Slot tự cộng trong vòng 5 phút\n\n"
        "═══════════════════════════════════\n"
        "❓ **GIẢI THÍCH ID TELEGRAM**\n"
        "═══════════════════════════════════\n\n"
        "ID của bạn là: `{chat_id}`\n\n"
        "*ID này là gì?*\n"
        "• Mã định danh duy nhất của tài khoản Telegram\n"
        "• Mỗi người dùng bot sẽ có 1 ID khác nhau\n"
        "• Không thay đổi khi bạn start bot lại\n\n"
        "*Dùng để làm gì?*\n"
        "• Login vào web dashboard\n"
        "• Thanh toán/nạp tiền\n"
        "• Admin quản lý tài khoản\n\n"
        "*Làm sao biết ID của mình?*\n"
        "Cách 1: Gõ `/start` (ID sẽ hiển thị)\n"
        "Cách 2: Gõ `/balance` (ID sẽ hiển thị)\n"
        "Cách 3: Truy cập web → nhập ID\n\n"
        "═══════════════════════════════════\n"
        "🌐 **WEB DASHBOARD**\n"
        "═══════════════════════════════════\n\n"
        "Truy cập: http://localhost:8080\n"
        "Nhập ID: {chat_id}\n\n"
        "*Tính năng:*\n"
        "📊 Xem danh sách sản phẩm\n"
        "🔍 Tìm kiếm nhanh\n"
        "🗑️ Xóa sản phẩm\n"
        "💳 Nạp tiền\n\n"
        "═══════════════════════════════════\n"
        "❓ **FAQ**\n"
        "═══════════════════════════════════\n\n"
        "*Q: Bot lâu lâu mới thông báo?*\n"
        "A: Bot check mỗi 2 phút. Nếu chậm, website tải lâu.\n\n"
        "*Q: Có phí gì?*\n"
        "A: Miễn phí 2 link. Thêm vào: 10.000đ/link.\n\n"
        "*Q: Slot mua được bao lâu?*\n"
        "A: Vĩnh viễn! Không hết hạn.\n\n"
        "*Q: Hoàn lại tiền được không?*\n"
        "A: Không hỗ trợ hoàn, nhưng slot lưu vĩnh viễn.\n\n"
        "Xem thêm: http://localhost:8080 → Help"
    )
    
    # Send guide as plain text chunks to avoid Markdown parsing errors and length limits
    full = guide_text.format(chat_id=chat_id)
    try:
        chunk_size = 3800
        for i in range(0, len(full), chunk_size):
            part = full[i:i+chunk_size]
            safe_reply(chat_id, part)
    except Exception:
        # Fallback to a single plain message
        try:
            safe_reply(chat_id, full)
        except Exception:
            pass

# --- VÒNG LẶP QUÉT NGẦM ---
def background_checker():
    print("🕵️ Trình theo dõi đã khởi động (Chế độ đa luồng & tối ưu URL)...")
    while True:
        tracks = db.get_all_tracks()
        if not tracks:
            time.sleep(CHECK_INTERVAL)
            continue
            
        # 1. Gom nhóm URL (Deduplication) để tránh cào trùng 1 link
        url_to_tracks = defaultdict(list)
        for track in tracks:
            url_to_tracks[track['url']].append(track)
            
        unique_urls = list(url_to_tracks.keys())
        print(f"🔄 Đang check {len(unique_urls)} URL duy nhất (từ {len(tracks)} yêu cầu)...")
        
        # 2. Quét song song bằng ThreadPoolExecutor
        url_results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            # Gửi toàn bộ URL vào pool
            future_to_url = {executor.submit(scraper.check_url_only, url): url for url in unique_urls}
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    status = future.result()
                    url_results[url] = status
                except Exception as e:
                    print(f"Lỗi khi check {url}: {e}")
                    url_results[url] = "error"
                    
        # 3. Phân phát kết quả về cho từng User & Update DB tuần tự để tránh khoá SQLite
        for url, current_status in url_results.items():
            for track in url_to_tracks[url]:
                # Gửi thông báo nếu có sự thay đổi từ Hết hàng -> Có hàng
                if current_status == "available" and track['last_status'] != "available":
                    msg = f"🎉 TIN VUI SĂN SALE:\nSản phẩm bạn theo dõi hiện ĐÃ CÓ HÀNG!\n👉 Vào mua ngay: {track['url']}"
                    try:
                        safe_reply(track['chat_id'], msg)
                    except Exception as e:
                        print(f"Lỗi gửi tin cho {track['chat_id']}: {e}")
                
                # Cập nhật DB
                if current_status != track['last_status']:
                    db.update_status(track['id'], current_status)
                    
        print(f"✅ Hoàn thành lượt check. Chờ {CHECK_INTERVAL}s...")
        time.sleep(CHECK_INTERVAL)

# --- WEB DASHBOARD SERVER (Flask) ---
def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Dashboard đang chạy tại: http://localhost:{port} (Waitress WSGI)")
    try:
        from waitress import serve
        serve(flask_app, host="0.0.0.0", port=port, threads=8)
    except ImportError:
        print("⚠️ Không tìm thấy waitress, fallback về Flask dev server...")
        flask_app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    threading.Thread(target=background_checker, daemon=True).start()
    print("🚀 Bot Telegram đã sẵn sàng!")
    
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        print("🌍 Chạy trên Render: Đang thiết lập Webhook...")
        bot.remove_webhook()
        time.sleep(1)
        webhook_url = f"{render_url}/{TELEGRAM_TOKEN}"
        bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook đã được thiết lập tại {webhook_url}")
        
        # Waitress and Background Checker run in threads, 
        # so we need to keep the main thread alive
        while True:
            time.sleep(100)
    else:
        print("💻 Chạy ở Local: Đang dùng chế độ Polling...")
        bot.remove_webhook()
        time.sleep(1)
        bot.infinity_polling()