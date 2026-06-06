# 📝 CHANGELOG - Bot Săn Sale

Tất cả những thay đổi quan trọng trong dự án này sẽ được ghi lại tại đây.

## [1.0.0] - 2026-06-05

### ✨ Tính Năng Mới

#### Bot Telegram
- ✅ **Hỗ trợ /track** - Thêm sản phẩm vào theo dõi
- ✅ **Hỗ trợ /list** - Xem danh sách sản phẩm
- ✅ **Hỗ trợ /untrack** - Ngừng theo dõi sản phẩm
- ✅ **Thêm /balance** - Kiểm tra slot còn lại và credits
- ✅ **Thêm /upgrade** - Mua thêm slot (link thanh toán)
- ✅ **Thêm /start** - Hướng dẫn sử dụng với danh sách lệnh

#### Hệ Thống Slot & Thanh Toán
- ✅ **Mỗi user có 2 link miễn phí**
- ✅ **Mua thêm slot**: 10.000đ = +1 slot
- ✅ **Bảng giá linh hoạt**: 1 slot, 5 slots, 10 slots, 20 slots
- ✅ **Endpoint API công khai**: `/api/payment/add-credits`
- ✅ **Endpoint API**: `/api/payment/pricing` - Xem bảng giá

#### Trang Thanh Toán Web
- ✅ **Giao diện đẹp mắt** - Hiện đại, responsive
- ✅ **Hiển thị thông tin user** - Telegram ID, trạng thái
- ✅ **Chọn gói nạp** - 4 gói khác nhau
- ✅ **Phương thức thanh toán** - QR Code, Chuyển khoản
- ✅ **Hiển thị kết quả** - Success/Error message
- ✅ **FAQ** - Câu hỏi thường gặp

#### Database & API
- ✅ **Fix lỗi hàm `add_credits`** - Kiểm tra null trước `dict()`
- ✅ **Fix lỗi hàm `get_all_users`** - Thêm return statement
- ✅ **Kiểm tra slot limit** - Trong lệnh `/track`
- ✅ **Cảnh báo khi hết slot** - Hướng dẫn mua thêm

#### Tài Liệu
- ✅ **Tạo USAGE.md** - Hướng dẫn sử dụng chi tiết
  - Khởi động nhanh
  - Danh sách lệnh
  - Hướng dẫn nạp tiền
  - Ví dụ thực tế
  - FAQ & Troubleshooting
  
- ✅ **Cập nhật README.md** - Toàn diện
  - Tính năng chính
  - Cài đặt nhanh
  - Danh sách API
  - Bảng giá
  - Project structure
  
- ✅ **Tạo .env.example** - Hướng dẫn cấu hình

### 🔧 Cải Thiện

- ✅ **Cải thiện help message** - Liệt kê đầy đủ các lệnh
- ✅ **Kiểm tra URL trước khi thêm** - Validate URL format
- ✅ **Thông báo chi tiết** - Khi vượt quá giới hạn slot
- ✅ **Dashboard đẹp hơn** - Responsive design

### 🐛 Fix Lỗi

- ✅ **Fix kiểm tra slot limit** - Lệnh `/track` không kiểm tra giới hạn
- ✅ **Fix hàm `add_credits`** - NoneType error khi row = None
- ✅ **Fix hàm `get_all_users`** - Missing return statement
- ✅ **Fix validate URL** - Cảnh báo khi URL không hợp lệ

### 📦 Dependencies

Các thư viện sử dụng:
```
pyTelegramBotAPI==4.20.0
requests==2.31.0
beautifulsoup4==4.12.3
python-dotenv==1.0.1
google-genai
flask==3.1.1
```

### 🚀 Deployment

- ✅ Hỗ trợ chạy trực tiếp: `python bot.py`
- ✅ Hỗ trợ Docker: `docker-compose up -d`
- ✅ Volume mount database - Dữ liệu không mất khi rebuild

### 📊 Trạng Thái Hoàn Thiện

- [x] Core bot functionality
- [x] Tracking system
- [x] Payment system
- [x] Web dashboard
- [x] Admin panel
- [x] Documentation
- [ ] Mobile app (roadmap)
- [ ] More e-commerce platforms
- [ ] Price history tracking

---

## Ghi Chú Phát Triển

### Điều Chỉnh Trong Tương Lai
- Hỗ trợ thanh toán bằng ví điện tử (Momo, ZaloPay)
- Thông báo giảm giá (theo %)
- Chia sẻ tracking list với bạn bè
- Tích hợp webhook cho 3rd party
- API rate limiting

### Known Issues
- Một số website phức tạp có thể cần thêm thời gian để xác định trạng thái
- Bot check mỗi 2 phút (có thể điều chỉnh qua `CHECK_INTERVAL`)

---

**Phiên bản hiện tại:** 1.0.0  
**Ngày phát hành:** 2026-06-05  
**Trạng thái:** ✅ Stable
