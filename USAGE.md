# 📖 HƯỚNG DẪN SỬ DỤNG - Bot Săn Sale Telegram

## 🎯 Tổng Quan
**Bot Săn Sale** là một trợ lý tự động giúp bạn theo dõi giá sản phẩm trên các trang thương mại điện tử. Khi sản phẩm có hàng hoặc giá thay đổi, bot sẽ thông báo cho bạn ngay lập tức qua Telegram.

---

## 🚀 KHỞI ĐỘNG NHANH

### 1️⃣ Tìm Bot Trên Telegram
- Mở Telegram và tìm bot: **@YourBotUsername** (thay bằng link bot thực tế)
- Nhấn **"Start"** hoặc gõ `/start`

### 2️⃣ Các Lệnh Cơ Bản

#### 📌 `/track [URL]` - Thêm sản phẩm vào theo dõi
```
Ví dụ:
/track https://www.shopee.vn/product-name
/track https://www.lazada.vn/product-name
```
**Kết quả:** Bot sẽ bắt đầu theo dõi sản phẩm và thông báo khi có hàng

---

#### 📋 `/list` - Xem danh sách sản phẩm đang theo dõi
```
/list
```
**Kết quả:** Hiển thị tất cả link đang theo dõi, trạng thái hàng, và ID

**Trạng thái:**
- ✅ **available** - Sản phẩm có hàng
- ❌ **soldout** - Hết hàng
- ⚠️ **error** - Lỗi khi lấy dữ liệu
- ⏳ **unknown** - Chưa xác định được

---

#### 🗑️ `/untrack [ID]` - Ngừng theo dõi sản phẩm
```
Ví dụ:
/untrack 5
```
**Cách tìm ID:** Gõ `/list` để xem ID của mỗi sản phẩm

---

#### 💰 `/balance` - Kiểm tra số slot còn lại
```
/balance
```
**Kết quả:** Hiển thị:
- Số slot đã sử dụng (ví dụ: 2/2)
- Tổng tiền credits nạp vào
- Telegram ID của bạn

---

#### 🎁 `/upgrade` - Mua thêm slot
```
/upgrade
```
**Kết quả:** Bot sẽ gửi link thanh toán để bạn nạp tiền mua slot

---

#### ❓ `/help` hoặc `/start` - Xem danh sách lệnh
```
/help
```

---

## 💳 HƯỚNG DẪN NẠP TIỀN VÀ MỞ RỘNG SLOT

### 📊 Bảng Giá
| Slot | Giá | Tiết Kiệm |
|------|-----|----------|
| +1 slot | 10.000đ | - |
| +5 slots | 45.000đ | 5.000đ |
| +10 slots | 80.000đ | 20.000đ |
| +20 slots | 150.000đ | 50.000đ |

### 📲 Quy Trình Nạp Tiền

#### **Bước 1:** Mở Trang Nạp Tiền
Gõ `/upgrade` → Bot gửi link → Bấm vào link

#### **Bước 2:** Chọn Gói Nạp
- Chọn số lượng slot cần mua
- Hiển thị: Số slot, giá tiền, tổng chi phí

#### **Bước 3:** Chọn Phương Thức Thanh Toán
**Tuỳ chọn:**
- 📱 **QR Code** - Quét mã QR trên Telegram
- 🏦 **Chuyển Khoản** - Chuyển khoản ngân hàng (số tài khoản sẽ hiển thị)

#### **Bước 4:** Xác Nhận Thanh Toán
- Bấm nút **"Tiếp Tục Thanh Toán"**
- Chờ xử lý (thường 5-30 giây)

#### **Bước 5:** Hoàn Tất
- Nếu thành công → Hiển thị màn hình "✅ Thanh Toán Thành Công!"
- Slot sẽ tự động cộng vào tài khoản
- Quay lại Telegram bot để tiếp tục sử dụng

### ✅ Xác Nhận Slot Mới
Sau khi thanh toán xong, gõ `/balance` để kiểm tra:
```
📊 Slot sử dụng: 2/7   (nếu mua +5 slots)
💰 Credits nạp: 45.000đ
```

---

## 🎯 VÍ DỤ THỰC TẾ

### Ví dụ 1: Theo Dõi Áo Khoác Trên Shopee
```
👤 Bạn: /track https://shopee.vn/Áo-khoác-nam-giá-rẻ

🤖 Bot: 🎯 Đã thêm vào danh sách theo dõi!
        🔗 Bot đang quét ngầm link này...

...sau 3 phút...

🤖 Bot: 🎉 TIN VUI SĂN SALE:
        Sản phẩm bạn theo dõi hiện ĐÃ CÓ HÀNG!
        👉 Vào mua ngay: https://shopee.vn/...
```

### Ví dụ 2: Đạt Giới Hạn Slot
```
👤 Bạn: /track https://lazada.vn/product-2

🤖 Bot: ⚠️ Bạn đã đạt giới hạn 2 link! 🔐

        Để thêm 1 link nữa, bạn cần nạp:
        💰 10.000đ → +1 slot
        
        Gõ /upgrade để mua thêm slot!
```

### Ví dụ 3: Kiểm Tra Trạng Thái
```
👤 Bạn: /list

🤖 Bot: 📋 DANH SÁCH ĐANG THEO DÕI:

        🔹 ID: 1
        🔗 Link: https://shopee.vn/product-1
        ✅ Trạng thái: available
        
        🔹 ID: 2
        🔗 Link: https://lazada.vn/product-2
        ⏳ Trạng thái: unknown
```

---

## 🌐 DASHBOARD WEB (Tùy Chọn)

### Truy Cập Dashboard
Mở trong trình duyệt: `http://localhost:8080` (hoặc domain của bạn)

### Tính Năng Trên Web
- 📊 Xem danh sách sản phẩm đang theo dõi
- 🔍 Tìm kiếm sản phẩm nhanh
- 🗑️ Xóa sản phẩm khỏi danh sách
- 💳 Nạp tiền (có thể làm từ web thay vì bot)

### Admin Panel
- Đăng nhập tại: `/admin`
- Quản lý người dùng, thêm tiền, xem báo cáo

---

## ❓ CÂU HỎI THƯỜNG GẶP

### Q: Sao bot lâu lâu mới thông báo?
**A:** Bot kiểm tra mỗi 2 phút. Nếu sản phẩm có hàng, bot sẽ thông báo ngay. Nếu chậm hơn có thể do:
- Máy chủ trang web bị chậm
- API của trang bị giới hạn yêu cầu
- Bạn tắt Telegram

### Q: Có phí gì khi sử dụng bot?
**A:** 
- **Miễn phí:** 2 link đầu tiên
- **Mua thêm:** 10.000đ = +1 link
- **Không có phí duy trì:** Slot mua một lần sử dụng vĩnh viễn

### Q: Tôi muốn ngừng dùng, có mất tiền không?
**A:** Không! Slot mua được lưu vĩnh viễn. Bạn có thể dừng sử dụng bất kỳ lúc nào mà không mất tiền.

### Q: Có hoàn tiền được không?
**A:** Không hỗ trợ hoàn tiền, nhưng slot vẫn luôn có thể sử dụng lại.

### Q: Link theo dõi hỗ trợ những nơi nào?
**A:** Hiện tại hỗ trợ:
- ✅ Shopee
- ✅ Lazada
- ✅ Tiki
- ✅ Amazon
- ✅ eBay
- ✅ Các trang web thương mại điện tử khác

### Q: Bot có theo dõi được tất cả loại sản phẩm không?
**A:** Bot hoạt động tốt với hầu hết sản phẩm. Một số sản phẩm có trang web phức tạp có thể cần thêm thời gian để xác định trạng thái.

### Q: Dữ liệu của tôi có được lưu không?
**A:** Có! Bot lưu:
- Danh sách sản phẩm đang theo dõi
- Thông tin tài khoản (Telegram ID, số slot)
- Lịch sử thanh toán

**An toàn:** Dữ liệu được lưu trên máy chủ riêng và không được chia sẻ với bên thứ 3.

---

## 🛠️ TROUBLESHOOTING - KHẮC PHỤC SỰ CỐ

### Bot không trả lời khi gõ lệnh
**Giải pháp:**
1. Kiểm tra xem bạn đã gõ `/` ở đầu lệnh chưa (ví dụ: `/start` chứ không phải `start`)
2. Đợi 2-3 giây rồi thử lại
3. Khởi động lại bot: gõ `/start`

### "Không tìm thấy sản phẩm ID: X"
**Giải pháp:**
1. Gõ `/list` để xem danh sách ID
2. Dùng ID đúng từ danh sách đó

### "URL không hợp lệ"
**Giải pháp:**
- Đảm bảo URL bắt đầu bằng `http://` hoặc `https://`
- Ví dụ sai: `shopee.vn/product` 
- Ví dụ đúng: `https://shopee.vn/product`
- Copy-paste URL từ thanh địa chỉ của trình duyệt

### Thanh toán không xử lý được
**Giải pháp:**
1. Kiểm tra kết nối internet
2. Thử làm lại từ đầu: `/upgrade`
3. Thử phương thức thanh toán khác (QR hoặc chuyển khoản)

### Slot chưa cộng sau thanh toán
**Giải pháp:**
1. Chờ 5 phút
2. Gõ `/balance` để kiểm tra lại
3. Nếu vẫn không có, liên hệ admin: @support_bot

---

## 📞 HỖ TRỢ VÀ LIÊN HỆ

- **Bot Username:** @YourBotUsername
- **Admin:** @support_bot
- **Website:** http://localhost:8080
- **Dashboard:** http://localhost:8080/admin (admin only)

---

## 📝 GHI CHÚ

- Bot hoạt động 24/7 trên máy chủ
- Slot không hết hạn - sử dụng vĩnh viễn
- Bạn có thể theo dõi bao nhiêu link tùy thích (có đủ slot)
- Cảm ơn bạn đã sử dụng Bot Săn Sale! 🙏

---

**Phiên bản:** 1.0  
**Cập nhật lần cuối:** 2026-06-05  
**Ngôn ngữ:** Tiếng Việt
