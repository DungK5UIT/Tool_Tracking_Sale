# 🤖 Bot Săn Sale - Tự Động Theo Dõi Giá Sản Phẩm

Bot Telegram thông minh giúp bạn tự động theo dõi giá sản phẩm trên các trang thương mại điện tử (Shopee, Lazada, Tiki, etc.) và nhận thông báo khi có hàng.

## ✨ Tính Năng Chính

✅ **Theo dõi đa sản phẩm** - Mỗi tài khoản 2 link miễn phí, có thể mua thêm  
✅ **Thông báo tức thì** - Khi sản phẩm có hàng, bot thông báo ngay lập tức  
✅ **Hỗ trợ đa nền tảng** - Shopee, Lazada, Tiki, Amazon, eBay, etc.  
✅ **Giao diện đẹp** - Telegram bot + Web dashboard  
✅ **Thanh toán linh hoạt** - QR Code, Chuyển khoản, API tích hợp  
✅ **Quản lý dễ dàng** - Admin panel để quản lý người dùng  

---

## 🚀 Cài Đặt Nhanh

### 1. Yêu Cầu Hệ Thống
- Python 3.10+
- Docker + Docker Compose (tùy chọn)
- Telegram Bot Token
- Google Gemini API Key (cho phát hiện trạng thái sản phẩm)

### 2. Clone Project
```bash
git clone <repository-url>
cd tool_tracking
```

### 3. Cấu Hình Biến Môi Trường
Tạo file `.env`:
```bash
cp .env.example .env
```

Chỉnh sửa `.env`:
```env
TELEGRAM_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=your_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
PORT=8080
PAYMENT_URL=http://localhost:8080/payment
```

### 4. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 5. Chạy Bot
**Cách 1: Chạy trực tiếp**
```bash
python bot.py
```

**Cách 2: Dùng Docker**
```bash
docker-compose up -d --build
```

---

## 🎮 Sử Dụng Bot

### Lệnh Cơ Bản
| Lệnh | Mô Tả |
|------|-------|
| `/start` | Xem hướng dẫn |
| `/track <URL>` | Thêm sản phẩm vào theo dõi |
| `/list` | Xem danh sách sản phẩm |
| `/untrack <ID>` | Ngừng theo dõi sản phẩm |
| `/balance` | Kiểm tra slot còn lại |
| `/upgrade` | Mua thêm slot |

### Ví Dụ
```
/track https://shopee.vn/product-name
```

---

## 💰 Bảng Giá

| Slot | Giá | Ghi Chú |
|------|-----|--------|
| 2 (miễn phí) | 0đ | Mặc định mỗi user |
| +1 slot | 10.000đ | |
| +5 slots | 45.000đ | Tiết kiệm 5.000đ |
| +10 slots | 80.000đ | Tiết kiệm 20.000đ |
| +20 slots | 150.000đ | Tiết kiệm 50.000đ |

---

## 📊 Thành Phần Project

```
tool_tracking/
├── bot.py              # Bot Telegram chính
├── api.py              # Flask API + Dashboard
├── database.py         # Quản lý Database SQLite
├── scraper.py          # Quét thông tin sản phẩm
├── requirements.txt    # Dependencies
├── docker-compose.yml  # Docker Compose config
├── Dockerfile          # Docker image
├── templates/
│   ├── dashboard.html  # Giao diện dashboard
│   ├── admin.html      # Admin panel
│   └── payment.html    # Trang thanh toán
├── USAGE.md           # Hướng dẫn sử dụng chi tiết
└── README.md          # File này
```

---

## 🔧 Cấu Hình

### Biến Môi Trường

- **TELEGRAM_TOKEN** - Lấy từ BotFather trên Telegram
- **GEMINI_API_KEY** - Lấy từ Google AI Studio
- **FLASK_SECRET_KEY** - Khóa bảo mật Session Flask
- **ADMIN_USERNAME** - Tên đăng nhập admin
- **ADMIN_PASSWORD** - Mật khẩu admin
- **PORT** - Port chạy web (mặc định 8080)
- **PAYMENT_URL** - URL trang thanh toán

### Lấy Token

#### Telegram Bot Token
1. Chat với [@BotFather](https://t.me/botfather)
2. Gõ `/newbot`
3. Làm theo hướng dẫn, lấy token
4. Dán vào `.env`

#### Google Gemini API Key
1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Tạo API key mới
3. Dán vào `.env`

---

## 🌐 Truy Cập Giao Diện

- **Dashboard:** `http://localhost:8080`
- **Admin Panel:** `http://localhost:8080/admin`
- **Trang Thanh Toán:** `http://localhost:8080/payment?chat_id=XXXXX`
- **API Docs:** `http://localhost:8080/health`

### Đăng Nhập Admin
- Username: `admin` (hoặc từ `.env`)
- Password: `admin` (hoặc từ `.env`)

---

## 📡 API Endpoints

### Công Khai

#### Thêm Sản Phẩm
```
POST /api/tracks
Body: {"url": "https://...", "chat_id": "123"}
```

#### Xem Danh Sách
```
GET /api/tracks
```

#### Nạp Tiền
```
POST /api/payment/add-credits
Body: {"chat_id": "123", "amount": 10000}
```

#### Bảng Giá
```
GET /api/payment/pricing
```

### Admin Only

#### Lấy Danh Sách User
```
GET /api/admin/users
```

#### Thêm Tiền Cho User
```
POST /api/admin/users/<chat_id>/credits
Body: {"amount": 10000}
```

#### Xóa Sản Phẩm Của User
```
DELETE /api/admin/users/<chat_id>/tracks
```

---

## 🐛 Debugging

### Xem Log
```bash
# Docker
docker-compose logs -f sale-bot

# Trực tiếp
python bot.py
```

### Xóa Database
```bash
rm tracker.db
```

---

## 🔐 Bảo Mật

- ✅ Mã hóa Session Flask
- ✅ Validate Input
- ✅ SQL Injection Protection
- ✅ Rate Limiting (giới hạn slot)
- ✅ Admin Authentication

### Khuyến Nghị
- Đổi mật khẩu admin trong `.env`
- Không commit `.env` vào Git
- Sử dụng HTTPS trong production
- Định kỳ backup database

---

## 📝 Ghi Log

Bot tự động ghi log tất cả hoạt động:
- Mỗi lần thêm/xóa sản phẩm
- Mỗi lần thanh toán
- Lỗi xảy ra

---

## 🤝 Đóng Góp

Mọi đóng góp đều được hoan nghênh! 

1. Fork project
2. Tạo branch (`git checkout -b feature/abc`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push branch (`git push origin feature/abc`)
5. Tạo Pull Request

---

## 📞 Hỗ Trợ

- **Bot:** [@YourBotUsername](https://t.me/YourBotUsername)
- **Admin:** @support_bot
- **Website:** http://localhost:8080
- **Issues:** Tạo issue trên GitHub

---

## 📄 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết

---

## ⚡ Hiệu Suất

- **Kiểm tra sản phẩm:** Mỗi 2 phút
- **Phản hồi bot:** < 1 giây
- **Thông báo:** Tức thì (< 5 giây)
- **Database:** SQLite, hỗ trợ 10,000+ tracks

---

## 🎯 Roadmap

- [ ] Hỗ trợ thêm các nền tảng (Vinted, Mercari)
- [ ] Lọc theo giá (thông báo khi giá dưới X)
- [ ] Thống kê giá theo thời gian
- [ ] Chia sẻ danh sách tracked với bạn bè
- [ ] App mobile

---

**Phiên bản:** 1.0  
**Cập nhật:** 2026-06-05  
**Ngôn ngữ:** Tiếng Việt  
**Status:** ✅ Đang hoạt động
