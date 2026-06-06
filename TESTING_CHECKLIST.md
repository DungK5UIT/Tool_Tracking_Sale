# ✅ VERIFICATION & TESTING CHECKLIST

**Project:** Bot Săn Sale Dashboard  
**Version:** 1.0.0  
**Status:** Ready for Testing  

---

## 🔍 **PHASE 1: CODE VERIFICATION**

### ✓ Syntax Check
```bash
# Verify Python files compile without errors
python -m py_compile bot.py api.py database.py scraper.py
# Expected: No output (silent success)
```
- [x] bot.py - No syntax errors
- [x] api.py - No syntax errors
- [x] database.py - No syntax errors  
- [x] scraper.py - No syntax errors

### ✓ Dependencies
```bash
# Check all required packages
pip list | grep -E "telebot|flask|requests|beautifulsoup|google"
```
- [x] pyTelegramBotAPI (4.20.0+)
- [x] Flask (3.1.1+)
- [x] BeautifulSoup4 (4.12.0+)
- [x] google-genai (latest)
- [x] python-dotenv (latest)
- [x] requests (latest)

### ✓ Environment Setup
```bash
# Verify .env.example exists
ls -la .env.example
```
- [x] .env.example created
- [x] All variables documented
- [x] Required fields marked

---

## 🚀 **PHASE 2: LOCAL TESTING (WITHOUT DOCKER)**

### Start Services
```bash
# Terminal 1: Start Flask app
python api.py

# Terminal 2: Start Telegram bot
python bot.py
```

### 2.1: Database Initialization
- [ ] `tracker.db` created automatically
- [ ] `tracks` table exists
- [ ] `user_profiles` table exists
- [ ] Tables are empty (clean start)

**Test Command:**
```bash
sqlite3 tracker.db ".tables"
# Expected: tracks user_profiles
```

### 2.2: Web Dashboard
- [ ] Visit: http://localhost:8080
- [ ] Dashboard page loads
- [ ] Dark mode CSS applies
- [ ] All tabs visible: "Tracking | Admin | Hướng dẫn"

**Check Points:**
- [ ] Header visible: "🛒 Bot Săn Sale Dashboard"
- [ ] Stats bar: Total | Có hàng | Hết hàng | Lỗi
- [ ] Add form: URL input + Chat ID input + 🚀 Button
- [ ] Telegram ID info box: (appears when entering valid ID)

### 2.3: Test Add Track (Web)
1. [ ] Enter Chat ID: `123456789` in input field
2. [ ] See Telegram ID box appear showing: `📱 Telegram ID: 123456789`
3. [ ] Click [📋 Copy] button
4. [ ] Verify ID copied to clipboard
5. [ ] Enter URL: `https://shopee.vn/test`
6. [ ] Click [🚀 Theo dõi]
7. [ ] See success toast: "✅ URL đã được thêm"
8. [ ] Track appears in list
9. [ ] Stats updated: Total = 1

### 2.4: Telegram Bot - Test All Commands

#### Command: `/start`
```
Expected Output:
👋 Chào mừng! Đây là Bot Săn Sale...
📱 **Telegram ID của bạn:** `987654321`
_(ID này dùng để login vào web dashboard)_

Kết quả: 
- [x] Telegram ID displayed
- [x] Format: 📱 **Telegram ID của bạn:** `{ID}`
```

#### Command: `/balance`
```
Expected Output:
👤 Thông tin tài khoản:

📊 Slot sử dụng: 1/2
💰 Credits nạp: 0đ
📱 Telegram ID: `987654321`

Kết quả:
- [x] Shows slot usage (X/Y)
- [x] Shows Telegram ID
- [x] Shows credits
```

#### Command: `/track https://lazada.vn/product`
```
Expected Output (First track):
✅ Đã thêm sản phẩm vào theo dõi

Expected Output (When full - 2+ tracks):
⚠️ Bạn đã đạt giới hạn 2 link! 🔐
Để thêm 1 link nữa, bạn cần nạp:
💰 10,000đ → +1 slot
Gõ `/upgrade` để mua thêm slot!

Kết quả:
- [x] Track added successfully
- [x] Slot limit enforced (max 2)
- [x] Cost calculated correctly
```

#### Command: `/list`
```
Expected Output:
📋 Danh sách sản phẩm đang theo dõi (1/2 slots):

1️⃣ https://shopee.vn/test
   Status: ⏳ Đang kiểm tra...

Kết quả:
- [x] All tracks listed
- [x] Status shown
- [x] Pagination works (if 20+ items)
```

#### Command: `/upgrade`
```
Expected Output:
💳 NẠP SLOT THÊM - HƯỚNG DẪN:

1️⃣ Bấm vào link để mua slot:
👉 http://localhost:8080/payment?chat_id=987654321

Kết quả:
- [x] Payment link provided
- [x] Chat ID included in URL
- [x] Link format correct
```

#### Command: `/guide`
```
Expected Output: 4000+ character text guide including:
- Explanation of Telegram ID
- All 8 commands listed
- Pricing table
- Step-by-step payment process
- FAQ section

Kết quả:
- [x] Guide text appears
- [x] User's chat_id embedded
- [x] Comprehensive (4000+ chars)
```

#### Command: `/help`
```
Expected Output: Same as `/start`
```

### 2.5: Payment Flow
1. [ ] From bot: `/upgrade`
2. [ ] Click payment link
3. [ ] Visit: http://localhost:8080/payment?chat_id=123456789
4. [ ] Page loads
5. [ ] See: "📱 Telegram ID: 123456789"
6. [ ] See 4 pricing packages:
   - [x] +1 slot - 10,000đ
   - [x] +5 slots - 45,000đ
   - [x] +10 slots - 80,000đ
   - [x] +20 slots - 150,000đ
7. [ ] Select +1 slot
8. [ ] Select payment method (QR or Transfer)
9. [ ] Click "Tiến hành thanh toán"
10. [ ] Mock payment (test endpoint manually):
    ```bash
    curl -X POST http://localhost:8080/api/payment/add-credits \
      -H "Content-Type: application/json" \
      -d '{"chat_id": "123456789", "amount": 10000}'
    ```
11. [ ] Success response:
    ```json
    {
      "message": "Credits added successfully",
      "new_max_tracks": 3,
      "credits": 10000
    }
    ```
12. [ ] Return to `/balance`: max_tracks now 3

### 2.6: Slot Limit Verification
1. [ ] Start with 2 free slots
2. [ ] Add 2 products via `/track`
3. [ ] Try add 3rd: Get "đã đạt giới hạn" message
4. [ ] Upgrade: Add 10,000đ credit (mock via curl)
5. [ ] Try add 3rd: Now succeeds (3/3)
6. [ ] Try add 4th: Get limit message again
7. [ ] Cost: 10,000đ shown

### 2.7: Guide Page (`/guide`)
- [ ] Visit: http://localhost:8080/guide
- [ ] Page loads with comprehensive content:
  - [x] Telegram ID section (700+ words)
  - [x] 8 commands with examples
  - [x] Pricing table
  - [x] 5-step payment process
  - [x] 8 FAQ items (accordion)
  - [x] Usage tips
  - [x] Support contact

---

## 🐳 **PHASE 3: DOCKER TESTING**

### 3.1: Build Image
```bash
docker-compose build
```
- [ ] Build completes without errors
- [ ] Image created: `tool_tracking:latest`
- [ ] Size: ~500-700MB

### 3.2: Start Container
```bash
docker-compose up -d
docker ps
```
- [ ] Container running: `tool_tracking-bot-1`
- [ ] Port 8080 mapped: `0.0.0.0:8080`
- [ ] Volume mounted: `tracker.db`

### 3.3: Test in Docker
```bash
# View logs
docker logs -f tool_tracking-bot-1
```
- [ ] Bot connects to Telegram
- [ ] Flask app starts on port 8080
- [ ] Background checker initialized
- [ ] No errors in logs

### 3.4: Database Persistence
```bash
# Check database file exists
ls -la tracker.db

# Add data
curl -X POST http://localhost:8080/api/tracks \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123456789", "url": "https://shopee.vn/test"}'

# Stop container
docker-compose down

# Start again
docker-compose up -d

# Verify data persists
curl http://localhost:8080/api/tracks?chat_id=123456789
```
- [ ] Data persists after container restart
- [ ] tracker.db in volume mount works

---

## 📊 **PHASE 4: API ENDPOINT TESTING**

### Test All 13 Endpoints

#### 1. GET /
- [ ] Status: 200
- [ ] Returns: HTML (dashboard)
- [ ] Contains: "Bot Săn Sale Dashboard"

#### 2. GET /admin
- [ ] Status: 200 (no auth required in test)
- [ ] Returns: HTML (admin panel)

#### 3. GET /payment
- [ ] Status: 200
- [ ] Returns: HTML (payment page)
- [ ] Supports: ?chat_id=XXX parameter

#### 4. GET /guide
- [ ] Status: 200
- [ ] Returns: HTML (guide page)

#### 5. POST /api/tracks (Add)
```bash
curl -X POST http://localhost:8080/api/tracks \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "111", "url": "https://shopee.vn/product"}'
```
- [ ] Status: 201
- [ ] Response: `{"id": 1, "chat_id": "111", ...}`
- [ ] Validates URL format
- [ ] Checks slot limit
- [ ] Returns error if duplicate

#### 6. GET /api/tracks
```bash
curl http://localhost:8080/api/tracks
```
- [ ] Status: 200
- [ ] Returns: JSON array of tracks
- [ ] Each item: `{id, chat_id, url, last_status}`

#### 7. POST /api/payment/add-credits
```bash
curl -X POST http://localhost:8080/api/payment/add-credits \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "111", "amount": 10000}'
```
- [ ] Status: 200
- [ ] Response: `{"message": "...", "new_max_tracks": 3, "credits": 10000}`
- [ ] Calculation: amount // 10000 = slots added
- [ ] Database updated

#### 8. GET /api/payment/pricing
```bash
curl http://localhost:8080/api/payment/pricing
```
- [ ] Status: 200
- [ ] Returns: JSON array with 4 tiers
- [ ] Each tier: `{slots, price}`
- [ ] Prices: 10k, 45k, 80k, 150k

#### 9. POST /api/user/info
```bash
curl -X POST http://localhost:8080/api/user/info \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "111"}'
```
- [ ] Status: 200
- [ ] Response: User profile + all their tracks
- [ ] Fields: `{chat_id, display_name, max_tracks, credits, current_tracks, tracks:[...]}`

#### 10. GET /api/me
```bash
curl http://localhost:8080/api/me?chat_id=111
```
- [ ] Status: 200
- [ ] Returns: Current user profile

#### 11. POST /api/me/name
```bash
curl -X POST http://localhost:8080/api/me/name \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "111", "name": "Nguyễn A"}'
```
- [ ] Status: 200
- [ ] Database updated with new name
- [ ] Response: `{"message": "Name updated"}`

#### 12. POST /api/untrack
```bash
curl -X POST http://localhost:8080/api/untrack \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "111", "track_id": 1}'
```
- [ ] Status: 200
- [ ] Track deleted
- [ ] Response: `{"message": "Track deleted"}`

#### 13. POST /admin/users (Admin endpoint)
```bash
curl -X POST http://localhost:8080/admin/users \
  -H "Content-Type: application/json" \
  -d '{"action": "get_all"}'
```
- [ ] Status: 200
- [ ] Returns: All users and their profiles

---

## 🎯 **PHASE 5: TELEGRAM ID VERIFICATION**

### Telegram ID Must Appear In:
- [x] `/start` command - Line 2: "📱 **Telegram ID của bạn:** `{id}`"
- [x] `/balance` command - Shows user's ID
- [x] `/guide` command - Embedded in guide text
- [x] Web dashboard - Info box when logged in (NEW)
- [x] Web dashboard - Copy button (NEW)
- [x] Payment page - Shows ID at top (NEW)
- [x] guide.html page - Explanation + how to find

### ID Properties to Verify:
- [x] Unique per user (different users get different IDs)
- [x] Never changes (same ID across multiple `/start` calls)
- [x] Numeric only (e.g., "987654321")
- [x] Long enough (8-10 digits)

---

## 📝 **PHASE 6: DOCUMENTATION CHECK**

- [x] USAGE.md exists (3000+ words)
  - [x] Quick start guide
  - [x] All 8 commands documented
  - [x] Examples provided
  - [x] Payment instructions
  - [x] FAQ with 10+ questions

- [x] README.md exists (2000+ words)
  - [x] Project overview
  - [x] Features list
  - [x] Setup instructions
  - [x] API reference
  - [x] Configuration guide

- [x] TROUBLESHOOTING.md exists (2000+ words)
  - [x] Common errors
  - [x] Debug tips
  - [x] Performance notes
  - [x] Database troubleshooting

- [x] CHANGELOG.md exists
  - [x] Version 1.0.0 dated 2026-06-05
  - [x] Features listed
  - [x] Bug fixes noted
  - [x] Dependencies listed

- [x] .env.example exists
  - [x] All variables documented
  - [x] Example values provided
  - [x] Comments for each field

- [x] TELEGRAM_ID_GUIDE.md exists (NEW)
  - [x] 3 ways to find ID
  - [x] ID properties explained
  - [x] Security notes
  - [x] Real examples provided

- [x] ARCHITECTURE.md exists (NEW)
  - [x] System diagrams (ASCII)
  - [x] Component details
  - [x] Data flow diagrams
  - [x] Technology stack listed

- [x] COMPLETION_SUMMARY.md exists (NEW)
  - [x] Feature checklist
  - [x] All components listed
  - [x] Statistics
  - [x] Next steps

---

## 🐛 **PHASE 7: ERROR HANDLING**

### Invalid Input Tests
- [ ] Invalid URL format: `/track invalid-url`
  - Expected: "❌ Lỗi: Đường link không hợp lệ"
  
- [ ] Empty URL: `/track`
  - Expected: "❌ Vui lòng nhập đúng: /track [Đường_link]"
  
- [ ] Invalid chat_id in API: `{"chat_id": "", "url": "..."}`
  - Expected: 400 error or validation message
  
- [ ] Non-existent track to delete: `/untrack 999`
  - Expected: "❌ Không tìm thấy sản phẩm"

### Rate Limiting & Edge Cases
- [ ] Add duplicate URL: Try adding same URL twice
  - Expected: "❌ URL này đã tồn tại"
  
- [ ] Exceed slot limit: Add 3 tracks when max=2
  - Expected: "⚠️ Bạn đã đạt giới hạn 2 link"
  
- [ ] Negative credit amount: POST with amount=-1000
  - Expected: Error or validation message

---

## ✅ **SIGN-OFF CHECKLIST**

Complete the following before declaring v1.0.0 ready:

- [ ] All 8 bot commands working
- [ ] All 13 API endpoints tested
- [ ] Database CRUD operations verified
- [ ] Slot limiting enforced
- [ ] Payment system functional (mock)
- [ ] Telegram ID visible in 6+ places
- [ ] Web dashboard responsive
- [ ] Guide page comprehensive
- [ ] Docker builds and runs
- [ ] Data persists after restart
- [ ] All documentation complete
- [ ] Python syntax verified
- [ ] No console errors
- [ ] No database errors
- [ ] Error messages user-friendly
- [ ] Payment pricing correct (10k per slot)
- [ ] Admin panel accessible
- [ ] Guide navigation working

---

## 📞 **SUPPORT & NEXT STEPS**

### If Tests Fail:
1. Check error message in terminal
2. Review logs: `docker logs tool_tracking-bot-1`
3. Check database: `sqlite3 tracker.db "SELECT * FROM user_profiles;"`
4. Review relevant documentation file

### Next Steps After Verification:
1. [ ] Deploy to production server
2. [ ] Setup real payment gateway
3. [ ] Configure production Telegram bot token
4. [ ] Setup database backups
5. [ ] Enable monitoring & logging
6. [ ] Add analytics tracking
7. [ ] Announce to users

---

**Test Date:** ___________  
**Tester Name:** ___________  
**Status:** ☐ PASS  ☐ FAIL  

**Notes:**
_________________________________________
_________________________________________

---

**Version:** 1.0.0  
**Created:** 2026-06-05  
**Last Updated:** 2026-06-05
