import os
import re
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect
import database as db

app = Flask(__name__)
# Secret key để mã hóa session cookie — nên set qua .env trong production
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "sale-bot-secret-2024")

# ============================
# ADMIN CONFIG
# ============================
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

# ============================
# HELPERS
# ============================
def is_valid_url(url):
    """Kiểm tra định dạng URL cơ bản."""
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def admin_required(f):
    """Decorator bảo vệ admin endpoint."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'error': 'Chưa đăng nhập admin', 'code': 'UNAUTHORIZED'}), 401
        return f(*args, **kwargs)
    return decorated

# ============================
# DASHBOARD ROUTE
# ============================
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/payment')
def payment():
    """Trang nạp tiền (redirect về dashboard)"""
    chat_id = request.args.get('chat_id', '')
    return redirect(f"/?chat_id={chat_id}&tab=payment")

@app.route('/guide')
def guide():
    """Trang hướng dẫn sử dụng"""
    return render_template('guide.html')

# ============================
# ADMIN AUTH ENDPOINTS
# ============================
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Đăng nhập admin."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Thiếu dữ liệu'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['is_admin'] = True
        session.permanent = False  # Session hết khi đóng trình duyệt
        return jsonify({'message': 'Đăng nhập thành công!'}), 200
    else:
        return jsonify({'error': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Đăng xuất admin."""
    session.pop('is_admin', None)
    return jsonify({'message': 'Đã đăng xuất'}), 200

@app.route('/api/admin/check', methods=['GET'])
def admin_check():
    """Kiểm tra trạng thái đăng nhập admin."""
    return jsonify({'is_admin': bool(session.get('is_admin'))}), 200

# ============================
# ADMIN USER MANAGEMENT
# ============================
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    """Lấy toàn bộ user profiles kèm track count."""
    profiles = db.get_all_user_profiles()
    result = []
    for p in profiles:
        result.append({
            'chat_id': p['chat_id'],
            'display_name': p['display_name'] or '',
            'max_tracks': p['max_tracks'],
            'credits': p['credits'],
            'track_count': p['track_count']
        })
    return jsonify(result)

@app.route('/api/admin/users/<chat_id>/credits', methods=['POST'])
@admin_required
def admin_add_credits(chat_id):
    """
    Nạp tiền cho user.
    Body: {"amount": 10000}  → cộng 10k = +1 slot
    """
    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({'error': 'Thiếu trường amount'}), 400

    try:
        amount = int(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Số tiền phải lớn hơn 0'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Số tiền không hợp lệ'}), 400

    result = db.add_credits(chat_id, amount)
    slots_added = amount // 10000
    return jsonify({
        'message': f'Đã nạp {amount:,}đ (+{slots_added} slot) cho {chat_id}',
        'max_tracks': result['max_tracks'],
        'credits': result['credits']
    }), 200

@app.route('/api/admin/users/<chat_id>/name', methods=['PUT'])
@admin_required
def admin_set_user_name(chat_id):
    """Admin cập nhật tên hiển thị của user."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Thiếu trường name'}), 400

    name = data['name'].strip()[:50]  # Giới hạn 50 ký tự
    db.set_display_name(chat_id, name)
    return jsonify({'message': f'Đã cập nhật tên cho {chat_id}'}), 200

@app.route('/api/admin/users/<chat_id>/tracks', methods=['GET'])
@admin_required
def admin_get_user_tracks_list(chat_id):
    """Lấy danh sách track của một user (admin)."""
    tracks = db.get_tracks_by_chat(chat_id)
    result = []
    for t in tracks:
        result.append({
            'id': t['id'],
            'url': t['url'],
            'last_status': t['last_status']
        })
    return jsonify(result)

@app.route('/api/admin/users/<chat_id>/tracks', methods=['DELETE'])
@admin_required
def admin_remove_user_tracks(chat_id):
    """Xóa tất cả track của một user (admin)."""
    deleted = db.remove_all_tracks_by_chat(chat_id)
    if deleted > 0:
        return jsonify({'message': f'Đã xóa {deleted} sản phẩm của {chat_id}'}), 200
    else:
        return jsonify({'error': 'User không có sản phẩm nào'}), 404

@app.route('/api/admin/tracks/status/<status>', methods=['DELETE'])
@admin_required
def admin_remove_by_status(status):
    """Xóa tất cả track theo trạng thái (admin)."""
    if status not in ['error', 'unknown', 'soldout', 'available']:
        return jsonify({'error': 'Trạng thái không hợp lệ'}), 400
    deleted = db.remove_tracks_by_status(status)
    return jsonify({'message': f'Đã xóa {deleted} sản phẩm có trạng thái "{status}"'}), 200

# ============================
# USER PROFILE ENDPOINTS (PUBLIC)
# ============================
@app.route('/api/me', methods=['GET'])
def api_get_me():
    """
    Lấy thông tin profile của user hiện tại.
    Query param: ?chat_id=xxx
    """
    chat_id = request.args.get('chat_id', '').strip()
    if not chat_id:
        return jsonify({'error': 'Thiếu chat_id'}), 400

    profile = db.get_or_create_user(chat_id)
    current_tracks = len(db.get_tracks_by_chat(chat_id))

    return jsonify({
        'chat_id': profile['chat_id'],
        'display_name': profile['display_name'] or '',
        'max_tracks': profile['max_tracks'],
        'credits': profile['credits'],
        'current_tracks': current_tracks
    }), 200

@app.route('/api/user/info', methods=['POST'])
def api_get_user_info():
    """
    Lấy thông tin user từ chat_id (khi user login web)
    Body: {"chat_id": "123456"}
    """
    data = request.get_json()
    if not data or 'chat_id' not in data:
        return jsonify({'error': 'Thiếu chat_id'}), 400

    chat_id = str(data['chat_id']).strip()
    if not chat_id:
        return jsonify({'error': 'chat_id không hợp lệ'}), 400

    profile = db.get_or_create_user(chat_id)
    current_tracks = len(db.get_tracks_by_chat(chat_id))
    tracks = db.get_tracks_by_chat(chat_id)
    
    tracks_list = [{
        'id': t['id'],
        'url': t['url'],
        'last_status': t['last_status']
    } for t in tracks]

    return jsonify({
        'success': True,
        'user': {
            'chat_id': profile['chat_id'],
            'display_name': profile['display_name'] or 'User ' + chat_id[-4:],
            'max_tracks': profile['max_tracks'],
            'credits': profile['credits'],
            'current_tracks': current_tracks
        },
        'tracks': tracks_list
    }), 200

@app.route('/api/me/name', methods=['POST'])
def api_set_my_name():
    """
    User tự cập nhật tên hiển thị.
    Body: {"chat_id": "xxx", "name": "Tên Mới"}
    """
    data = request.get_json()
    if not data or 'chat_id' not in data or 'name' not in data:
        return jsonify({'error': 'Thiếu chat_id hoặc name'}), 400

    chat_id = data['chat_id'].strip()
    name = data['name'].strip()[:50]

    if not chat_id:
        return jsonify({'error': 'chat_id không hợp lệ'}), 400

    db.set_display_name(chat_id, name)
    return jsonify({'message': f'Đã cập nhật tên thành "{name}"'}), 200

# ============================
# TRACKS (PUBLIC)
# ============================
@app.route('/api/tracks', methods=['GET'])
def api_get_tracks():
    """Lấy tất cả sản phẩm đang theo dõi."""
    tracks = db.get_all_tracks()
    result = [{
        'id': t['id'],
        'chat_id': t['chat_id'],
        'url': t['url'],
        'last_status': t['last_status']
    } for t in tracks]
    return jsonify(result)

@app.route('/api/tracks', methods=['POST'])
def api_add_track():
    """Thêm sản phẩm mới — kiểm tra rate limit trước."""
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({'error': 'Thiếu trường URL'}), 400

    url = data['url'].strip()
    chat_id = data.get('chat_id', 'web').strip() or 'web'

    if not is_valid_url(url):
        return jsonify({'error': 'URL không hợp lệ. Phải bắt đầu bằng http:// hoặc https://'}), 400

    # --- RATE LIMIT CHECK ---
    current_count = len(db.get_tracks_by_chat(chat_id))
    max_allowed = db.get_max_tracks(chat_id)

    if current_count >= max_allowed:
        return jsonify({
            'error': f'Bạn đã dùng hết {max_allowed} slot theo dõi. Nạp 10.000đ để mở thêm 1 slot!',
            'code': 'RATE_LIMIT',
            'current': current_count,
            'max': max_allowed
        }), 429

    success = db.add_track(chat_id, url)
    if success:
        # Đảm bảo user profile tồn tại
        db.get_or_create_user(chat_id)
        return jsonify({
            'message': 'Đã thêm thành công!',
            'current': current_count + 1,
            'max': max_allowed
        }), 201
    else:
        return jsonify({'error': 'URL này đã được theo dõi rồi!'}), 409

@app.route('/api/tracks/<int:track_id>', methods=['DELETE'])
def api_remove_track(track_id):
    """Ngừng theo dõi sản phẩm theo ID."""
    tracks = db.get_all_tracks()
    target = next((t for t in tracks if t['id'] == track_id), None)

    if not target:
        return jsonify({'error': 'Không tìm thấy sản phẩm'}), 404

    success = db.remove_track(track_id, target['chat_id'])
    if success:
        return jsonify({'message': f'Đã ngừng theo dõi sản phẩm ID {track_id}'}), 200
    else:
        return jsonify({'error': 'Lỗi khi xóa'}), 500

# ============================
# PAYMENT / CREDITS (PUBLIC)
# ============================
@app.route('/api/payment/add-credits', methods=['POST'])
def api_add_credits():
    """
    Nạp tiền cho user (API công khai).
    Body: {"chat_id": "xxx", "amount": 10000}
    """
    data = request.get_json()
    if not data or 'chat_id' not in data or 'amount' not in data:
        return jsonify({'error': 'Thiếu chat_id hoặc amount'}), 400

    chat_id = data['chat_id'].strip()
    try:
        amount = int(data['amount'])
        if amount <= 0 or amount % 10000 != 0:
            return jsonify({'error': 'Số tiền phải là bội số của 10.000đ'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Số tiền không hợp lệ'}), 400

    if not chat_id:
        return jsonify({'error': 'chat_id không hợp lệ'}), 400

    result = db.add_credits(chat_id, amount)
    slots_added = amount // 10000
    
    return jsonify({
        'message': f'✅ Đã nạp {amount:,}đ thành công!',
        'chat_id': chat_id,
        'amount': amount,
        'slots_added': slots_added,
        'max_tracks': result['max_tracks'],
        'credits': result['credits']
    }), 200

@app.route('/api/payment/pricing', methods=['GET'])
def api_get_pricing():
    """Lấy bảng giá nạp tiền"""
    pricing = [
        {'slots': 1, 'price': 10000, 'label': '+1 slot'},
        {'slots': 5, 'price': 45000, 'label': '+5 slots (tiết kiệm 5k)'},
        {'slots': 10, 'price': 80000, 'label': '+10 slots (tiết kiệm 20k)'},
        {'slots': 20, 'price': 150000, 'label': '+20 slots (tiết kiệm 50k)'},
    ]
    return jsonify(pricing), 200

@app.route('/api/payment/qr-info', methods=['GET'])
def api_get_qr_info():
    """Lấy thông tin QR chuyển khoản"""
    amount = request.args.get('amount', '0')
    chat_id = request.args.get('chat_id', '')
    
    # Mặc định thông tin ngân hàng (Có thể lấy từ env sau)
    BANK_ID = os.environ.get("BANK_ID", "MB") # Tên viết tắt ngân hàng hoặc BIN
    ACCOUNT_NO = os.environ.get("BANK_ACCOUNT", "0123456789")
    ACCOUNT_NAME = os.environ.get("BANK_ACCOUNT_NAME", "NGUYEN VAN A")
    TEMPLATE = "compact"
    
    add_info = f"Nap slot bot {chat_id}"
    
    qr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-{TEMPLATE}.png?amount={amount}&addInfo={add_info}&accountName={ACCOUNT_NAME}"
    
    return jsonify({
        "qr_url": qr_url,
        "amount": amount,
        "content": add_info
    }), 200

import threading

BOT_USERNAME_CACHE = ""

def fetch_bot_username():
    global BOT_USERNAME_CACHE
    token = os.environ.get("TELEGRAM_TOKEN", "")
    if token:
        try:
            import telebot
            from telebot import apihelper
            apihelper.CONNECT_TIMEOUT = 3
            apihelper.READ_TIMEOUT = 3
            bot = telebot.TeleBot(token)
            me = bot.get_me()
            BOT_USERNAME_CACHE = me.username
        except Exception as e:
            pass

# Run in background to prevent blocking the web server startup and requests
threading.Thread(target=fetch_bot_username, daemon=True).start()

@app.route('/api/bot-info', methods=['GET'])
def api_bot_info():
    """Trả về thông tin bot (username) để làm link trên UI"""
    return jsonify({"username": BOT_USERNAME_CACHE})

# ============================
# HEALTH CHECK
# ============================
@app.route('/health')
def health_check():
    return 'Bot is alive!', 200
