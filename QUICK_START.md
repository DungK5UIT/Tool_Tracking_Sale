# 🚀 QUICK START - Bot Săn Sale (5 phút)

**Status:** ✅ Version 1.0.0 Ready  
**Time:** ~5 minutes to get running  
**Difficulty:** Easy (Beginner-friendly)

---

## 📦 **STEP 1: Chuẩn Bị (1 phút)**

### Yêu Cầu
- [x] Python 3.8+ đã cài
- [x] Docker (tuỳ chọn - nếu muốn container)
- [x] Telegram account

### Lấy Telegram Bot Token
1. Mở Telegram, tìm: `@BotFather`
2. Gõ: `/newbot`
3. Đặt tên bot: "Bot Săn Sale"
4. Copy token nhận được (dạng: `123456:ABCD...`)

---

## ⚙️ **STEP 2: Setup Projekt (2 phút)**

### Option A: Local (Direct Python)

```bash
# 1. Clone/Download project
cd d:\tool_tracking

# 2. Cài dependencies
pip install -r requirements.txt

# 3. Tạo file .env
cp .env.example .env

# 4. Edit .env, thêm bot token
# Mở .env trong editor, tìm TELEGRAM_TOKEN=
# Thay bằng: TELEGRAM_TOKEN=123456:ABCD...
```

### Option B: Docker

```bash
# 1. Vào project folder
cd d:\tool_tracking

# 2. Build image
docker-compose build

# 3. Edit .env (giống như trên)

# 4. Start container
docker-compose up -d
```

---

## 🎬 **STEP 3: Khởi Động (1 phút)**

### Local (2 Terminal)

**Terminal 1: Flask API**
```bash
cd d:\tool_tracking
python api.py
# Kết quả: "Running on http://127.0.0.1:8080"
```

**Terminal 2: Telegram Bot**
```bash
cd d:\tool_tracking
python bot.py
# Kết quả: "Listening to TelegramBotApiServer"
```

### Docker (1 Command)
```bash
docker-compose up -d
# Kết quả: "tool_tracking-bot-1  Running"
```

---

## ✅ **STEP 4: Test Ngay (1 phút)**

### Telegram Bot Commands

**Open Telegram → Find your bot → Send:**

```
/start
→ Xem Telegram ID của bạn
→ 📱 Telegram ID của bạn: 123456789

/balance
→ Xem slot hiện tại
→ 📊 Slot sử dụng: 0/2

/track https://shopee.vn/product-name
→ Thêm sản phẩm
→ ✅ Đã thêm sản phẩm vào theo dõi

/list
→ Xem danh sách
→ 📋 Danh sách sản phẩm đang theo dõi (1/2)

/guide
→ Xem hướng dẫn
→ 📚 HƯỚNG DẪN SỬ DỤNG CHI TIẾT...
```

### Web Dashboard

**Mở Browser → Truy cập:**
```
http://localhost:8080
```

**Nhập Telegram ID từ `/start`:**
```
Chat ID: 123456789
```

**Xem Dashboard:**
- ✅ Telegram ID hiển thị ở đầu
- ✅ Danh sách sản phẩm
- ✅ Stats (Total, Available, SoldOut, Error)

---

## 💳 **STEP 5: Thử Thanh Toán (Tuỳ Chọn)**

### Mock Payment Test

```bash
# Gõ lệnh này trong Terminal (hoặc dùng Postman):
curl -X POST http://localhost:8080/api/payment/add-credits \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123456789", "amount": 10000}'

# Kết quả:
# {
#   "message": "Credits added successfully",
#   "new_max_tracks": 3,
#   "credits": 10000
# }

# Kiểm tra trên bot:
# /balance → Slot sử dụng: 0/3 (tăng từ 2 lên 3)
```

---

## 📍 **Key Features Quick Demo**

### 1. **Telegram ID Tracking**
```
Gõ /start 
→ 📱 **Telegram ID của bạn:** `123456789`
→ ID này là duy nhất, không bao giờ thay đổi
```

### 2. **Slot Limiting**
```
Gõ /track link1
Gõ /track link2
→ ✅ 2 tracks added (max free = 2)

Gõ /track link3
→ ⚠️ Bạn đã đạt giới hạn 2 link!
→ Để thêm 1 link nữa, bạn cần nạp: 💰 10,000đ

Gõ /upgrade
→ Nhận link thanh toán: /payment?chat_id=123456789
```

### 3. **Payment System**
```
Visit: http://localhost:8080/payment?chat_id=123456789

Thấy:
- 📱 Your Telegram ID: 123456789
- 4 packages: +1 slot (10k) / +5 (45k) / +10 (80k) / +20 (150k)
- Payment methods: QR Code hoặc Bank Transfer
```

### 4. **Web Dashboard**
```
Visit: http://localhost:8080

Thấy:
- Tab 1: Tracking (add/view products)
- Tab 2: Admin (manage users)
- Tab 3: 📖 Guide (view help page)
- Telegram ID box (when logged in with ID)
```

### 5. **Comprehensive Guide**
```
On bot: /guide
Or visit: http://localhost:8080/guide

Nội dung:
- Telegram ID explained (how to find it)
- All 8 commands with examples
- Payment step-by-step (5 steps)
- FAQ (8 questions)
- Usage tips & security
```

---

## 🧹 **Cleanup & Restart**

### Reset Database (Start Fresh)
```bash
# Stop services
# Local: Ctrl+C on both terminals
# Docker: docker-compose down

# Remove database
rm tracker.db

# Start again
python api.py    # Terminal 1
python bot.py    # Terminal 2
# OR
docker-compose up -d
```

### View Logs
```bash
# Local: Check terminal output

# Docker: 
docker logs -f tool_tracking-bot-1
```

### Stop Services
```bash
# Local: Press Ctrl+C on both terminals

# Docker:
docker-compose down
```

---

## 📁 **File Locations**

```
d:\tool_tracking\
├── bot.py                    ← Telegram bot (start here)
├── api.py                    ← Web server (start here)
├── database.py               ← SQLite ORM
├── scraper.py                ← URL parser
├── tracker.db                ← Database (auto-created)
├── requirements.txt          ← Dependencies
├── .env                      ← Your config (create from .env.example)
├── .env.example              ← Template (copy this)
├── templates/
│   ├── dashboard.html        ← Main UI (http://localhost:8080)
│   ├── payment.html          ← Payment (http://localhost:8080/payment)
│   ├── guide.html            ← Guide (http://localhost:8080/guide)
│   └── admin.html            ← Admin
└── docs/
    ├── USAGE.md              ← Full guide (3000+ words)
    ├── README.md             ← Project info
    ├── ARCHITECTURE.md       ← System design
    ├── TELEGRAM_ID_GUIDE.md  ← ID explanation
    ├── TESTING_CHECKLIST.md  ← Testing guide
    ├── TROUBLESHOOTING.md    ← FAQ
    └── CHANGELOG.md          ← Version history
```

---

## 🆘 **Troubleshooting**

### Bot không respond
```bash
# Check token in .env
# Restart bot: python bot.py
# Check: docker logs (if using Docker)
```

### Port 8080 already in use
```bash
# Find process using port 8080:
# Windows: netstat -ano | findstr 8080
# Mac/Linux: lsof -i :8080

# Kill process or change FLASK_PORT in .env
```

### Database locked
```bash
# Close all connections:
# Restart bot/api
# Delete .db-journal file if exists
```

### Still stuck?
- 📖 Check: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 📚 Check: [USAGE.md](USAGE.md)
- 🏗️ Check: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🎯 **Next Steps**

### 1. Production Deployment
- [ ] Deploy to VPS/Cloud
- [ ] Setup real payment gateway (Momo, ZaloPay, etc.)
- [ ] Configure production bot token
- [ ] Setup database backups

### 2. Enhancements
- [ ] Add more e-commerce platforms (Tiki, Amazon, etc.)
- [ ] Add price history tracking
- [ ] Add notifications (email, SMS)
- [ ] Multi-language support

### 3. Analytics
- [ ] Track user activity
- [ ] Monitor payment success rate
- [ ] Generate usage reports
- [ ] Dashboard statistics

---

## 📞 **Support**

- 📖 Read: USAGE.md (comprehensive guide)
- 🔧 Debug: TROUBLESHOOTING.md (FAQ)
- 🏗️ Learn: ARCHITECTURE.md (system design)
- 🆔 ID Help: TELEGRAM_ID_GUIDE.md (how to find ID)

---

## ✨ **That's It!**

You now have a fully functional Bot Săn Sale system with:
- ✅ 8 Telegram commands
- ✅ 13 API endpoints
- ✅ Web dashboard
- ✅ Payment system (4 tiers)
- ✅ Slot limiting
- ✅ Comprehensive guide
- ✅ Full documentation

**Enjoy tracking! 🚀**

---

**Version:** 1.0.0  
**Last Updated:** 2026-06-05  
**Status:** Ready for Production ✅
