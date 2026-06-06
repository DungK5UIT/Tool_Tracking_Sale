import sqlite3

DB_NAME = "tracker.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('PRAGMA journal_mode=WAL;')
    # Bảng tracks (sản phẩm theo dõi)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            url TEXT NOT NULL,
            last_status TEXT DEFAULT 'unknown',
            UNIQUE(chat_id, url)
        )
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_chat_id ON tracks(chat_id)
    ''')
    # Bảng user_profiles (thông tin người dùng + slot)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            chat_id      TEXT PRIMARY KEY,
            display_name TEXT DEFAULT '',
            max_tracks   INTEGER DEFAULT 2,
            credits      INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# ============================
# USER PROFILE
# ============================

def get_or_create_user(chat_id):
    """Lấy profile user, tạo mới nếu chưa có. Luôn trả về row."""
    conn = get_db_connection()
    conn.execute(
        "INSERT OR IGNORE INTO user_profiles (chat_id) VALUES (?)",
        (chat_id,)
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM user_profiles WHERE chat_id = ?", (chat_id,)
    ).fetchone()
    conn.close()
    return row

def set_display_name(chat_id, name):
    """Cập nhật tên hiển thị cho user."""
    conn = get_db_connection()
    conn.execute(
        "INSERT OR IGNORE INTO user_profiles (chat_id) VALUES (?)", (chat_id,)
    )
    conn.execute(
        "UPDATE user_profiles SET display_name = ? WHERE chat_id = ?",
        (name.strip(), chat_id)
    )
    conn.commit()
    conn.close()

def get_max_tracks(chat_id):
    """Lấy số slot tối đa của user (mặc định 2)."""
    conn = get_db_connection()
    row = conn.execute(
        "SELECT max_tracks FROM user_profiles WHERE chat_id = ?", (chat_id,)
    ).fetchone()
    conn.close()
    return row['max_tracks'] if row else 2

def add_credits(chat_id, amount_vnd):
    """
    Nạp credits cho user.
    10.000đ = +1 slot. Trả về số slot mới.
    """
    conn = get_db_connection()
    conn.execute(
        "INSERT OR IGNORE INTO user_profiles (chat_id) VALUES (?)", (chat_id,)
    )
    # Cộng credits và tính thêm slot: mỗi 10.000đ = 1 slot
    slots_to_add = amount_vnd // 10000
    conn.execute(
        """UPDATE user_profiles 
           SET credits = credits + ?,
               max_tracks = max_tracks + ?
           WHERE chat_id = ?""",
        (amount_vnd, slots_to_add, chat_id)
    )
    conn.commit()
    row = conn.execute(
        "SELECT max_tracks, credits FROM user_profiles WHERE chat_id = ?",
        (chat_id,)
    ).fetchone()
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
    rows = conn.execute('''
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
    ''').fetchall()
    # Cũng lấy những user có track nhưng chưa có profile (dùng Telegram chưa qua web)
    orphans = conn.execute('''
        SELECT
            t.chat_id,
            '' as display_name,
            2 as max_tracks,
            0 as credits,
            COUNT(t.id) as track_count
        FROM tracks t
        WHERE t.chat_id NOT IN (SELECT chat_id FROM user_profiles)
        GROUP BY t.chat_id
    ''').fetchall()
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
    try:
        conn.execute(
            "INSERT INTO tracks (chat_id, url) VALUES (?, ?)",
            (chat_id, url)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remove_track(track_id, chat_id):
    """Xóa track theo ID + chat_id (user chỉ xóa được của mình)."""
    conn = get_db_connection()
    cursor = conn.execute(
        "DELETE FROM tracks WHERE id = ? AND chat_id = ?",
        (track_id, chat_id)
    )
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted > 0

def get_all_tracks():
    conn = get_db_connection()
    tracks = conn.execute("SELECT * FROM tracks").fetchall()
    conn.close()
    return tracks

def get_tracks_by_chat(chat_id):
    """Lấy danh sách track của một user."""
    conn = get_db_connection()
    tracks = conn.execute(
        "SELECT * FROM tracks WHERE chat_id = ?", (chat_id,)
    ).fetchall()
    conn.close()
    return tracks

def update_status(track_id, new_status):
    conn = get_db_connection()
    conn.execute("UPDATE tracks SET last_status = ? WHERE id = ?", (new_status, track_id))
    conn.commit()
    conn.close()

def get_all_users():
    """Lấy danh sách tất cả user (chat_id) kèm số lượng track (legacy)."""
    conn = get_db_connection()
    users = conn.execute('''
        SELECT chat_id, COUNT(*) as track_count
        FROM tracks
        GROUP BY chat_id
        ORDER BY track_count DESC
    ''').fetchall()
    conn.close()
    return users
    return users

def remove_all_tracks_by_chat(chat_id):
    """Xóa TẤT CẢ sản phẩm của một user. Dùng cho admin."""
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM tracks WHERE chat_id = ?", (chat_id,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted

def remove_tracks_by_status(status):
    """Xóa tất cả track có trạng thái cụ thể. Dùng cho admin."""
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM tracks WHERE last_status = ?", (status,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted