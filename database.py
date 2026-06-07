import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres.ivozwtwaldyqbahhspti:HuuDung_1072005@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"
)

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Bảng tracks (sản phẩm theo dõi)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id SERIAL PRIMARY KEY,
            chat_id TEXT NOT NULL,
            url TEXT NOT NULL,
            last_status TEXT DEFAULT 'unknown',
            UNIQUE(chat_id, url)
        )
    ''')
    cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_chat_id ON tracks(chat_id)
    ''')
    # Bảng user_profiles (thông tin người dùng + slot)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            chat_id      TEXT PRIMARY KEY,
            display_name TEXT DEFAULT '',
            max_tracks   INTEGER DEFAULT 2,
            credits      INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# ============================
# USER PROFILE
# ============================

def get_or_create_user(chat_id):
    """Lấy profile user, tạo mới nếu chưa có. Luôn trả về row."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO user_profiles (chat_id) VALUES (%s) ON CONFLICT (chat_id) DO NOTHING",
        (chat_id,)
    )
    conn.commit()
    cur.execute(
        "SELECT * FROM user_profiles WHERE chat_id = %s", (chat_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def set_display_name(chat_id, name):
    """Cập nhật tên hiển thị cho user."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_profiles (chat_id) VALUES (%s) ON CONFLICT (chat_id) DO NOTHING", (chat_id,)
    )
    cur.execute(
        "UPDATE user_profiles SET display_name = %s WHERE chat_id = %s",
        (name.strip(), chat_id)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_max_tracks(chat_id):
    """Lấy số slot tối đa của user (mặc định 2)."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT max_tracks FROM user_profiles WHERE chat_id = %s", (chat_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row['max_tracks'] if row else 2

def add_credits(chat_id, amount_vnd):
    """
    Nạp credits cho user.
    10.000đ = +1 slot. Trả về số slot mới.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO user_profiles (chat_id) VALUES (%s) ON CONFLICT (chat_id) DO NOTHING", (chat_id,)
    )
    # Cộng credits và tính thêm slot: mỗi 10.000đ = 1 slot
    slots_to_add = amount_vnd // 10000
    cur.execute(
        """UPDATE user_profiles 
           SET credits = credits + %s,
               max_tracks = max_tracks + %s
           WHERE chat_id = %s""",
        (amount_vnd, slots_to_add, chat_id)
    )
    conn.commit()
    cur.execute(
        "SELECT max_tracks, credits FROM user_profiles WHERE chat_id = %s",
        (chat_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return dict(row)
    return {'max_tracks': 2, 'credits': 0}

def get_all_user_profiles():
    """
    Lấy tất cả user profiles kèm số track hiện tại.
    Dùng cho Admin panel.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('''
        SELECT
            p.chat_id,
            p.display_name,
            p.max_tracks,
            p.credits,
            COUNT(t.id) as track_count
        FROM user_profiles p
        LEFT JOIN tracks t ON p.chat_id = t.chat_id
        GROUP BY p.chat_id
        ORDER BY p.credits DESC, track_count DESC
    ''')
    rows = cur.fetchall()
    
    # Cũng lấy những user có track nhưng chưa có profile (dùng Telegram chưa qua web)
    cur.execute('''
        SELECT
            t.chat_id,
            '' as display_name,
            2 as max_tracks,
            0 as credits,
            COUNT(t.id) as track_count
        FROM tracks t
        WHERE t.chat_id NOT IN (SELECT chat_id FROM user_profiles)
        GROUP BY t.chat_id
    ''')
    orphans = cur.fetchall()
    cur.close()
    conn.close()
    return list(rows) + list(orphans)

# ============================
# TRACKS
# ============================

def add_track(chat_id, url):
    """
    Thêm sản phẩm. Trả về True nếu thành công, False nếu duplicate.
    KHÔNG kiểm tra rate limit ở đây — gọi get_max_tracks() trước khi gọi hàm này.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO tracks (chat_id, url) VALUES (%s, %s)",
            (chat_id, url)
        )
        conn.commit()
        success = True
    except psycopg2.IntegrityError:
        conn.rollback()
        success = False
    finally:
        cur.close()
        conn.close()
    return success

def remove_track(track_id, chat_id):
    """Xóa track theo ID + chat_id (user chỉ xóa được của mình)."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM tracks WHERE id = %s AND chat_id = %s",
        (track_id, chat_id)
    )
    conn.commit()
    rows_deleted = cur.rowcount
    cur.close()
    conn.close()
    return rows_deleted > 0

def get_all_tracks():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tracks")
    tracks = cur.fetchall()
    cur.close()
    conn.close()
    return tracks

def get_tracks_by_chat(chat_id):
    """Lấy danh sách track của một user."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT * FROM tracks WHERE chat_id = %s", (chat_id,)
    )
    tracks = cur.fetchall()
    cur.close()
    conn.close()
    return tracks

def update_status(track_id, new_status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tracks SET last_status = %s WHERE id = %s", (new_status, track_id))
    conn.commit()
    cur.close()
    conn.close()

def get_all_users():
    """Lấy danh sách tất cả user (chat_id) kèm số lượng track (legacy)."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('''
        SELECT chat_id, COUNT(*) as track_count
        FROM tracks
        GROUP BY chat_id
        ORDER BY track_count DESC
    ''')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def remove_all_tracks_by_chat(chat_id):
    """Xóa TẤT CẢ sản phẩm của một user. Dùng cho admin."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tracks WHERE chat_id = %s", (chat_id,))
    conn.commit()
    rows_deleted = cur.rowcount
    cur.close()
    conn.close()
    return rows_deleted

def remove_tracks_by_status(status):
    """Xóa tất cả track có trạng thái cụ thể. Dùng cho admin."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tracks WHERE last_status = %s", (status,))
    conn.commit()
    rows_deleted = cur.rowcount
    cur.close()
    conn.close()
    return rows_deleted