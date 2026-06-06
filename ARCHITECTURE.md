# 📐 ARCHITECTURE - Bot Săn Sale Dashboard

## 🏗️ SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     BOT SĂN SALE - HỆ THỐNG HOÀN CHỈNH                 │
└─────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────────┐
                           │  TELEGRAM USERS     │
                           │  (Multiple)         │
                           └──────────┬──────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                    ┌─────▼─────┐         ┌─────▼──────┐
                    │  BOT API  │         │  WEB       │
                    │  Handlers │         │  Dashboard │
                    └─────┬─────┘         └─────┬──────┘
                          │                     │
                    ┌─────▼─────────────────────▼────┐
                    │  FLASK APP (PORT 8080)         │
                    │  - Routes: /track, /list, etc  │
                    │  - Dashboard UI               │
                    │  - Payment Page               │
                    │  - Guide Page                 │
                    └─────┬──────────────────────────┘
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
   ┌────▼────┐      ┌────▼────┐      ┌─────▼─────┐
   │ Database │      │ Scraper  │      │ Background│
   │ (SQLite) │      │ + AI     │      │ Checker   │
   │ ·Track   │      │ + Parser │      │ (120s)    │
   │ ·Users   │      └──────────┘      └───────────┘
   │ ·Credits │
   └─────┬────┘
         │
    ┌────▼──────────────┐
    │  PERSISTENCE      │
    │  tracker.db       │
    │  (Volume Mount)   │
    └───────────────────┘
```

---

## 🎯 **COMPONENT DETAILS**

### 1. **TELEGRAM BOT LAYER** (`bot.py`)
```
┌────────────────────────────────────┐
│  /start              /help          │
│  ✅ Show Telegram ID               │
│  ✅ Show quick guide               │
├────────────────────────────────────┤
│  /track [URL]                      │
│  ✅ Validate URL                   │
│  ✅ Check slot limit               │
│  ✅ Add to database                │
├────────────────────────────────────┤
│  /list                             │
│  ✅ Get all user's tracks          │
│  ✅ Show status + pagination       │
├────────────────────────────────────┤
│  /untrack [ID]                     │
│  ✅ Delete specific track          │
├────────────────────────────────────┤
│  /balance                          │
│  ✅ Show slot usage (X/Y)          │
│  ✅ Show Telegram ID               │
│  ✅ Show credits amount            │
├────────────────────────────────────┤
│  /upgrade                          │
│  ✅ Send payment link              │
│  ✅ Include chat_id in URL         │
├────────────────────────────────────┤
│  /guide                            │
│  ✅ Send 4000+ char guide          │
│  ✅ Include user's Telegram ID     │
└────────────────────────────────────┘
```

### 2. **FLASK API LAYER** (`api.py`)

#### Routes
```
GET  /                      Dashboard HTML
GET  /admin                 Admin panel
GET  /payment               Payment page
GET  /guide                 Guide page

POST /api/tracks            Add track (validate slot)
GET  /api/tracks            Get all tracks
POST /api/payment/add-credits  Add credits (10k per slot)
GET  /api/payment/pricing   Pricing tiers
POST /api/user/info         Get user profile + tracks
GET  /api/me                Get current user profile
POST /api/me/name           Set display name
POST /api/untrack           Delete track
POST /admin/users           Manage users (admin only)
```

#### Features
- ✅ Rate limit checking
- ✅ Session-based admin auth
- ✅ CORS + JSON responses
- ✅ Error handling

### 3. **DATABASE LAYER** (`database.py`)

#### Schema
```
┌─────────────────────────────────────┐
│ tracks TABLE                        │
├─────────────────────────────────────┤
│ id          INTEGER (PK)            │
│ chat_id     TEXT                    │
│ url         TEXT                    │
│ last_status TEXT (available/sold...)│
│ UNIQUE(chat_id, url)                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ user_profiles TABLE                 │
├─────────────────────────────────────┤
│ chat_id     TEXT (PK)               │
│ display_name TEXT (optional)        │
│ max_tracks  INTEGER (default 2)     │
│ credits     INTEGER (default 0)     │
└─────────────────────────────────────┘
```

#### Operations
```
get_or_create_user(chat_id)     → Create profile if missing
get_max_tracks(chat_id)         → Get user's slot limit
add_track(chat_id, url)         → Add track (check duplicate)
get_tracks_by_chat(chat_id)     → Get user's all tracks
add_credits(chat_id, amount)    → Add credits & calculate slots
get_all_user_profiles()         → Admin: get all users
get_all_tracks()                → Get all tracks for checking
```

### 4. **SCRAPER + AI LAYER** (`scraper.py`)

#### Flow
```
┌─────────────────────────────────────┐
│ URL Input                           │
│ https://shopee.vn/product           │
└──────────────┬──────────────────────┘
               │
        ┌──────▼──────────┐
        │ Detect Platform │
        │ (Shopee/Lazada..│
        └──────┬──────────┘
               │
     ┌─────────┴─────────┐
     │                   │
┌────▼────────┐    ┌────▼────────┐
│ BeautifulSoup│    │ Google Gemini│
│ HTML Parse  │    │ AI Analysis  │
└────┬────────┘    └────┬────────┘
     │                   │
     └─────────┬─────────┘
               │
        ┌──────▼──────────────┐
        │ Status Result       │
        │ ✅ available        │
        │ ❌ soldout          │
        │ ⏳ error/pending    │
        └─────────────────────┘
```

### 5. **BACKGROUND CHECKER THREAD**

```
Every 120 seconds:
┌──────────────────────────────────┐
│ 1. Get all tracks                │
├──────────────────────────────────┤
│ 2. For each track:               │
│    - Call scraper.check_url()    │
│    - Get status (available/...)  │
├──────────────────────────────────┤
│ 3. If status changed:            │
│    - Update database             │
│    - Send Telegram notification  │
├──────────────────────────────────┤
│ 4. Log results                   │
└──────────────────────────────────┘
```

### 6. **WEB UI LAYER**

#### Dashboard (`templates/dashboard.html`)
```
┌─────────────────────────────────────┐
│ HEADER: Bot Săn Sale Dashboard      │
├─────────────────────────────────────┤
│ 📱 TELEGRAM ID BOX                  │ ← NEW
│    ID: 123456789  [Copy]            │
├─────────────────────────────────────┤
│ STATS: Total | Available | SoldOut  │
├─────────────────────────────────────┤
│ TAB 1: TRACKING (Active)            │
│   - Add form                        │
│   - Track list                      │
├─────────────────────────────────────┤
│ TAB 2: ADMIN                        │
│   - User management                 │
│   - Track statistics                │
├─────────────────────────────────────┤
│ TAB 3: 📖 GUIDE                    │
│   - Link to /guide page             │
└─────────────────────────────────────┘
```

#### Payment Page (`templates/payment.html`)
```
┌──────────────────────────────┐
│ PAYMENT PAGE - Bot Săn Sale  │
├──────────────────────────────┤
│ 📱 Your Telegram ID:         │
│    123456789                 │
├──────────────────────────────┤
│ PRICING PACKAGES:            │
│ ☐ +1 slot   | 10k đ          │
│ ☐ +5 slots  | 45k đ (save 5k)│
│ ☐ +10 slots | 80k đ (save20k)│
│ ☐ +20 slots | 150k đ(save50k)│
├──────────────────────────────┤
│ PAYMENT METHOD:              │
│ ◉ QR Code  ○ Bank Transfer   │
├──────────────────────────────┤
│ [PROCEED TO PAYMENT]         │
├──────────────────────────────┤
│ FAQ (5 questions)            │
└──────────────────────────────┘
```

#### Guide Page (`templates/guide.html`)
```
┌──────────────────────────────────────┐
│ 📖 COMPREHENSIVE USER GUIDE          │
├──────────────────────────────────────┤
│ 1. Telegram ID Explanation           │
│ 2. 8 Commands (with examples)        │
│ 3. Pricing & Payment Steps (5 steps) │
│ 4. FAQ (8 questions accordion)       │
│ 5. Dashboard Info                    │
│ 6. Usage Tips                        │
│ 7. Support Contact                  │
└──────────────────────────────────────┘
```

---

## 🔄 **DATA FLOW - ADD PRODUCT FLOW**

```
User in Telegram              API Server              Database
    │                             │                        │
    │  /track https://...  ──────▶│                        │
    │                             │  get_tracks_by_chat()  │
    │                             ├───────────────────────▶│
    │                             │                  [Count: 1]
    │                             ◀───────────────────────┤
    │                             │                        │
    │                             │  get_max_tracks()      │
    │                             ├───────────────────────▶│
    │                             │                  [Max: 2]
    │                             ◀───────────────────────┤
    │                             │                        │
    │                             │  ✅ Check: 1 < 2       │
    │                             │                        │
    │                             │  add_track()           │
    │                             ├───────────────────────▶│
    │                             │          INSERT OK
    │                             ◀───────────────────────┤
    │  ✅ Added to tracking◀──────┤                        │
```

---

## 💰 **PAYMENT FLOW**

```
User in Web Dashboard     Payment Page         Server         Database
        │                      │                  │                │
        │  Click Upgrade ─────▶│                  │                │
        │                      │                  │                │
        │  Select Package ─────▶│                  │                │
        │                      │                  │                │
        │  Pay (QR/Transfer)──▶│                  │                │
        │                      │                  │                │
        │                      │  POST /api/payment/add-credits
        │                      │  {chat_id, amount} ──────────────▶│
        │                      │                  │        UPDATE
        │                      │                  │        max_tracks
        │                      │                  │      credits += amount
        │                      │                  │        │
        │                      │◀─────────────────────────────────│
        │                      │                  │        OK
        │  Success Message◀─────                  │
        │  Slots Updated       │                  │
```

---

## 🔐 **TELEGRAM ID - LIFECYCLE**

```
User A                  User B                Telegram System
  │                       │                          │
  │ Send /start ─────────────────────────────────▶│
  │                       │                  Assigns: chat_id = 987654321
  │                       │                        │
  │ Show ID ◀────────────────────────────────────│
  │ 987654321             │                        │
  │                       │ Send /start ─────────────────────────────▶│
  │                       │                  Assigns: chat_id = 123456789
  │                       │ Show ID ◀────────────────────────────────│
  │                       │ 123456789                                │
  │                       │                        │
  │ (Later) /start again──────────────────────────▶│
  │ Still: 987654321      │   Same ID returned    │
  │ ✅ ID never changes   │                        │
```

---

## 📊 **SLOT SYSTEM - VISUAL**

```
FREE USER (Default)         AFTER UPGRADE (+5 slots)      AFTER UPGRADE (+20)
┌─────────────────────┐    ┌────────────────────────┐    ┌──────────────────────┐
│ ████░░░░░░░░░░░░░░ │    │ ████████████░░░░░░░░░ │    │ ███████████████░░░░░ │
│ 2 / 2 FULL          │    │ 7 / 7 FULL              │    │ 22 / 22 FULL          │
│ (Paid 0đ)           │    │ (Paid 45.000đ for 5)    │    │ (Paid 150.000đ for 20)│
│                     │    │                        │    │                      │
│ Add 1 more?         │    │ Add 1 more?             │    │ Add 1 more?           │
│ Cost: 10.000đ       │    │ Cost: 10.000đ           │    │ Cost: 10.000đ         │
└─────────────────────┘    └────────────────────────┘    └──────────────────────┘
```

---

## 🗂️ **FILE STRUCTURE**

```
tool_tracking/
├── bot.py                      # Telegram bot handler (8 commands)
├── api.py                      # Flask API server (13 endpoints)
├── database.py                 # SQLite ORM layer
├── scraper.py                  # URL parser + Gemini AI
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Python 3.13-slim image
├── requirements.txt            # Dependencies (pinned versions)
├── tracker.db                  # SQLite database (volume mount)
│
├── templates/
│   ├── dashboard.html          # Main UI (dark mode glassmorphism)
│   ├── payment.html            # Payment page (4 tiers)
│   ├── guide.html              # Comprehensive guide (1500+ lines)
│   └── admin.html              # Admin panel
│
├── USAGE.md                    # Full user guide (3000+ words)
├── README.md                   # Project overview (2000+ words)
├── TROUBLESHOOTING.md          # FAQ & troubleshooting (2000+ words)
├── CHANGELOG.md                # Release notes
├── TELEGRAM_ID_GUIDE.md        # ID explanation (NEW)
├── COMPLETION_SUMMARY.md       # Feature summary (THIS FILE)
├── ARCHITECTURE.md             # System design (THIS FILE)
└── .env.example                # Template environment variables
```

---

## ⚙️ **TECHNOLOGY STACK**

| Layer | Technology | Version |
|---|---|---|
| **Bot** | pyTelegramBotAPI | 4.20.0 |
| **Web** | Flask | 3.1.1 |
| **Database** | SQLite | 3.x |
| **Parser** | BeautifulSoup4 | 4.12.x |
| **AI** | google-genai | Latest |
| **Container** | Docker | Latest |
| **Python** | Python | 3.13-slim |

---

## ✅ **VERIFICATION CHECKLIST**

- [x] Python syntax verified (zero errors)
- [x] All 8 bot commands implemented
- [x] 13 API endpoints working
- [x] Database schema created
- [x] Payment system integrated
- [x] Telegram ID visible in 5+ places
- [x] Web UI complete with tabs
- [x] Guide page (1500+ lines)
- [x] 6 documentation files
- [x] Docker setup ready
- [x] Rate limiting implemented
- [x] Admin panel created
- [x] Background checker thread
- [x] Error handling & validation

---

**Version:** 1.0.0  
**Status:** ✅ COMPLETE  
**Last Updated:** 2026-06-05
