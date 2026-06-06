# 🔧 TROUBLESHOOTING - Khắc Phục Sự Cố

Hướng dẫn giải quyết các vấn đề thường gặp khi sử dụng Bot Săn Sale.

---

## 🤖 BOT TELEGRAM

### ❌ Bot không trả lời khi gõ lệnh

**Nguyên nhân:**
- Bot chưa được khởi động
- TELEGRAM_TOKEN không đúng
- Bot bị block/mute

**Giải pháp:**
```bash
# 1. Kiểm tra token
echo $TELEGRAM_TOKEN

# 2. Khởi động lại bot
python bot.py

# 3. Kiểm tra log
# Xem có lỗi gì không

# 4. Thử gõ lại
/start
```

---

### ❌ Bot nói "Chưa cấu hình TELEGRAM_TOKEN"

**Nguyên nhân:**
- File `.env` chưa được tạo
- Biến `TELEGRAM_TOKEN` không được set

**Giải pháp:**
```bash
# 1. Tạo file .env
cp .env.example .env

# 2. Chỉnh sửa .env và thêm token
TELEGRAM_TOKEN=your_real_token_here

# 3. Khởi động lại bot
python bot.py
```

---

### ❌ "Lỗi: Đường link không hợp lệ"

**Nguyên nhân:**
- URL không bắt đầu bằng `http://` hoặc `https://`
- URL bị sai (copy-paste sai)

**Giải pháp:**
```
Sai: /track shopee.vn/product
Đúng: /track https://shopee.vn/product

Sai: /track amazon.com
Đúng: /track https://www.amazon.com/product
```

---

### ❌ "Không tìm thấy sản phẩm ID: X"

**Nguyên nhân:**
- ID không chính xác
- Sản phẩm đã bị xóa

**Giải pháp:**
```bash
# 1. Xem lại danh sách
/list

# 2. Dùng ID chính xác
/untrack 1  (ví dụ: ID = 1)
```

---

### ⏳ Bot lâu lâu mới thông báo

**Nguyên nhân:**
- Bot check mỗi 2 phút
- Website bị chậm
- API bị giới hạn yêu cầu

**Giải pháp:**
- Đợi thêm vài phút
- Kiểm tra xem trang web có hoạt động không
- Liên hệ admin nếu vẫn có vấn đề

---

### 💰 "Bạn đã đạt giới hạn 2 link"

**Nguyên nhân:**
- Bạn đang sử dụng 2 slot miễn phí
- Cần mua thêm để sử dụng thêm link

**Giải pháp:**
```bash
# 1. Mua thêm slot
/upgrade

# 2. Theo dõi link thanh toán
# Chọn gói nạp tiền

# 3. Thanh toán và quay lại bot

# 4. Kiểm tra số slot
/balance
```

---

## 💳 THANH TOÁN

### ❌ Thanh toán không xử lý được

**Nguyên nhân:**
- Kết nối internet bị gián đoạn
- Server bị lỗi
- Phương thức thanh toán không hỗ trợ

**Giải pháp:**
```bash
# 1. Kiểm tra kết nối internet
ping google.com

# 2. Thử làm lại
/upgrade

# 3. Thử phương thức khác (QR → Chuyển khoản)

# 4. Liên hệ admin
@support_bot
```

---

### ❌ "Số tiền phải là bội số của 10.000đ"

**Nguyên nhân:**
- Số tiền không phải là 10k, 20k, 30k, etc.

**Giải pháp:**
- Chỉ chọn từ các gói được offer
- Hoặc nhập số tiền: 10000, 20000, 30000, etc.

---

### ✅ Slot chưa cộng sau thanh toán

**Nguyên nhân:**
- Server chưa xử lý
- Kết nối bị mất

**Giải pháp:**
```bash
# 1. Chờ 5-10 phút

# 2. Kiểm tra lại
/balance

# 3. Nếu vẫn không có
# Liên hệ admin với:
# - Telegram ID
# - Số tiền đã thanh toán
# - Timestamp thanh toán

@support_bot
```

---

## 🌐 WEB DASHBOARD

### ❌ Dashboard không tải được

**Nguyên nhân:**
- Port 8080 bị block
- Flask server không chạy
- Firewall chặn

**Giải pháp:**
```bash
# 1. Kiểm tra server chạy không
ps aux | grep bot.py

# 2. Kiểm tra port
netstat -an | grep 8080

# 3. Khởi động lại
python bot.py

# 4. Thử URL khác
http://localhost:8080 (nếu trên máy)
http://[server_ip]:8080 (nếu trên server)
```

---

### ❌ Admin panel không đăng nhập được

**Nguyên nhân:**
- Username/password sai
- Không có session cookie

**Giải pháp:**
```bash
# 1. Kiểm tra .env
cat .env | grep ADMIN

# 2. Mở incognito/private window

# 3. Thử lại
/admin → login

# 4. Nếu vẫn sai, cập nhật .env
ADMIN_USERNAME=newadmin
ADMIN_PASSWORD=newpassword

# 5. Khởi động lại bot
```

---

### ❌ CSRF Token lỗi

**Nguyên nhân:**
- Session hết hạn
- Cookie bị xóa

**Giải pháp:**
- Làm mới trang (Ctrl+F5 hoặc Cmd+Shift+R)
- Xóa cookie browser
- Đăng nhập lại

---

## 🗄️ DATABASE

### ❌ "Database locked"

**Nguyên nhân:**
- Nhiều process truy cập DB cùng lúc
- DB file bị corrupt

**Giải pháp:**
```bash
# 1. Đóng tất cả bot/app
kill -9 $(pgrep -f bot.py)

# 2. Xóa DB cũ
rm tracker.db

# 3. Khởi động lại
python bot.py

# Cảnh báo: Tất cả dữ liệu sẽ mất!
```

---

### ❌ "Database is read-only"

**Nguyên nhân:**
- File permission sai
- Ổ đĩa đầy

**Giải pháp:**
```bash
# 1. Kiểm tra quyền file
ls -la tracker.db

# 2. Cập nhật quyền
chmod 666 tracker.db

# 3. Kiểm tra dung lượng ổ đĩa
df -h

# 4. Nếu ổ đầy, xóa file cũ
```

---

### ❓ Làm thế nào để backup database?

**Giải pháp:**
```bash
# Sao chép file tracker.db
cp tracker.db tracker.db.backup

# Hoặc export dữ liệu
sqlite3 tracker.db ".dump" > backup.sql

# Restore (nếu cần)
sqlite3 tracker.db < backup.sql
```

---

## 🚀 DOCKER

### ❌ Docker container không chạy

**Nguyên nhân:**
- Docker/Docker Compose chưa cài
- Port 8080 bị chiếm
- `.env` không có

**Giải pháp:**
```bash
# 1. Kiểm tra Docker
docker --version
docker-compose --version

# 2. Kiểm tra port
lsof -i :8080

# 3. Tạo .env
cp .env.example .env

# 4. Khởi động
docker-compose up -d --build

# 5. Xem log
docker-compose logs -f sale-bot
```

---

### ❌ "Port 8080 already in use"

**Giải pháp:**
```bash
# 1. Tìm process chiếm port
lsof -i :8080

# 2. Kill process
kill -9 <PID>

# 3. Hoặc chạy trên port khác
# Sửa docker-compose.yml
ports:
  - "8081:8080"  # Thay 8080 → 8081

# 4. Khởi động lại
docker-compose up -d --build
```

---

### ❌ Container tự động tắt

**Giải pháp:**
```bash
# 1. Xem log
docker-compose logs

# 2. Kiểm tra lỗi
# Tìm error message

# 3. Fix lỗi và rebuild
docker-compose up -d --build

# 4. Nếu vẫn lỗi
# Kiểm tra .env có đầy đủ không
```

---

## 🔌 API

### ❌ API endpoint trả về 404

**Nguyên nhân:**
- Endpoint sai
- Server chưa chạy

**Giải pháp:**
```bash
# 1. Kiểm tra URL đúng không
GET /health  (hãy kiểm tra xem có response không)

# 2. Kiểm tra server
curl http://localhost:8080/health

# 3. Nếu connection refused
# Server chưa chạy, khởi động bot.py
```

---

### ❌ "chat_id is required"

**Nguyên nhân:**
- Body không có `chat_id`

**Giải pháp:**
```bash
# Sai:
curl -X POST http://localhost:8080/api/payment/add-credits \
  -H "Content-Type: application/json" \
  -d '{"amount": 10000}'

# Đúng:
curl -X POST http://localhost:8080/api/payment/add-credits \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123456", "amount": 10000}'
```

---

## 📊 PERFORMANCE

### ⚠️ Bot chạy chậm

**Nguyên nhân:**
- Server có CPU thấp
- RAM không đủ
- Database quá lớn

**Giải pháp:**
```bash
# 1. Xem resource usage
top
htop

# 2. Dọn dẹp database (nếu cần)
# Xóa tracks cũ hoặc user không dùng

# 3. Tăng resources (nếu trên cloud)
# Nâng cấp instance type

# 4. Kiểm tra network
# Có lag từ network không?
```

---

### ⚠️ Website tải lâu

**Nguyên nhân:**
- Dashboard JS quá nặng
- API chậm
- Database query chậm

**Giải pháp:**
```bash
# 1. Kiểm tra browser console
F12 → Console

# 2. Kiểm tra Network tab
F12 → Network

# 3. Xem request nào lâu nhất

# 4. Tối ưu query hoặc add index
```

---

## 🆘 LIÊN HỆ HỖ TRỢ

Nếu vấn đề chưa được giải quyết:

1. **Ghi lại:**
   - Thông báo lỗi chính xác
   - Các bước bạn đã thực hiện
   - Kết quả expected vs actual

2. **Liên hệ:**
   - Telegram: @support_bot
   - GitHub Issues: Tạo issue mới
   - Email: admin@example.com

3. **Cung cấp thông tin:**
   ```
   - Bot version: /start → xem version
   - OS: Windows/Linux/Mac
   - Python version: python --version
   - Error message: copy-paste chính xác
   - Logs: docker-compose logs (nếu dùng Docker)
   ```

---

**Cập nhật lần cuối:** 2026-06-05  
**Phiên bản:** 1.0
