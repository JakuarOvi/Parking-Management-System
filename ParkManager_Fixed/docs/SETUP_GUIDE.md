# 🅿 ParkManager — Complete Setup Guide

## What's Included

```
parkmanager/
├── backend/               ← Django REST API
│   ├── park_management/   ← Django project config
│   ├── parking/           ← Main app (models, views, tasks)
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example       ← Copy → .env and fill values
├── frontend/
│   └── index.html         ← Complete frontend (open in browser)
├── setup_windows.bat      ← One-click Windows setup
├── setup_mac_linux.sh     ← One-click Mac/Linux setup
├── start_windows.bat
├── start_mac_linux.sh
└── docs/
    └── SETUP_GUIDE.md     ← This file
```

---

## 📋 Prerequisites

Install these before running setup:

| Software    | Version  | Download                              |
|-------------|----------|---------------------------------------|
| Python      | 3.10+    | https://python.org/downloads          |
| MySQL       | 8.0+     | https://dev.mysql.com/downloads       |
| Redis       | 7.0+     | https://redis.io/download (see below) |
| Git (optional) | any   | https://git-scm.com                   |

### Redis on Windows
Download: https://github.com/microsoftarchive/redis/releases
Or use WSL2: `wsl --install` then `sudo apt install redis-server`

### Redis on Mac
```bash
brew install redis
brew services start redis
```

### Redis on Ubuntu/Debian
```bash
sudo apt update && sudo apt install redis-server -y
sudo systemctl start redis
```

---

## 🗄️ Database Setup (MySQL)

### Step 1 — Start MySQL
- Windows: Open MySQL Workbench or run `mysql -u root -p`
- Mac: `mysql.server start`
- Linux: `sudo systemctl start mysql`

### Step 2 — Create the database
```sql
-- Log in to MySQL first, then run:
CREATE DATABASE park_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Verify:
SHOW DATABASES;
```

### Step 3 — Set your password in .env
Open `backend/.env` (copy from `.env.example` first):
```env
DB_NAME=park_management
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
DB_HOST=localhost
DB_PORT=3306
```

---

## ⚙️ Installation Steps

### Windows

```cmd
1. Double-click: setup_windows.bat
   (This installs everything automatically)

2. When prompted, edit backend\.env with your MySQL password

3. After setup completes, double-click: start_windows.bat
```

### Mac / Linux

```bash
# Make executable (only once)
chmod +x setup_mac_linux.sh start_mac_linux.sh

# Run setup
./setup_mac_linux.sh

# Start the app
./start_mac_linux.sh
```

### Manual (any OS)
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Copy and edit .env
cp .env.example .env
# Edit .env with your MySQL password

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Seed initial data (slots + demo accounts)
python manage.py seed_data

# 7. Start Django server
python manage.py runserver

# 8. In separate terminals, start Celery:
celery -A park_management worker -l info
celery -A park_management beat -l info
```

---

## 🌐 Accessing the App

After starting, open:

| Service       | URL                                    |
|---------------|----------------------------------------|
| **Frontend**  | Open `frontend/index.html` in browser  |
| **API**       | http://localhost:8000/api/             |
| **Django Admin** | http://localhost:8000/admin/        |

---

## 👤 Demo Login Accounts (seeded automatically)

| Role  | Car Number / Username | Password  |
|-------|-----------------------|-----------|
| Admin | `ADMIN`               | `admin123`|
| Staff | `ST001CAR`            | `staff123`|
| User  | `DHA-1234`            | `myname`  |

> Note: The frontend works in **Demo Mode** without the backend running.
> Just open `frontend/index.html` and log in with any username/password.

---

## 🔌 API Endpoints Reference

### Auth
```
POST /api/auth/login/         → Login, returns JWT token
POST /api/auth/register/      → Register new user
POST /api/auth/logout/        → Logout (blacklist token)
GET  /api/auth/me/            → Get current user
PATCH /api/auth/me/update/    → Update profile
POST /api/auth/change-password/
```

### Slots
```
GET  /api/slots/              → List all slots (filter: floor, zone, status)
GET  /api/slots/blueprint/    → Full floor-by-floor slot map
POST /api/slots/              → Add slot (Admin only)
PATCH /api/slots/{id}/        → Edit slot
```

### Bookings
```
POST /api/bookings/           → Create booking (auto-generates QR)
GET  /api/bookings/           → List bookings (user sees own, admin sees all)
POST /api/bookings/{id}/cancel/     → Cancel booking
POST /api/bookings/{id}/scan_entry/ → Log vehicle entry (Staff)
POST /api/bookings/{id}/scan_exit/  → Log vehicle exit + calc overstay
POST /api/bookings/scan-qr/         → Lookup by QR scan
```

### Payments
```
POST /api/payments/create/         → Create payment record
POST /api/payments/{id}/mark_paid/ → Mark as paid + generate PDF receipt
POST /api/payments/{id}/refund/    → Process refund (Admin)
GET  /api/payments/                → List payments
```

### Admin
```
GET  /api/dashboard/admin/    → Stats: income, occupancy, overstays
GET  /api/dashboard/user/     → User's personal stats
GET  /api/reports/            → Chart data (period: daily/weekly/monthly)
GET  /api/reports/export-csv/ → Download CSV
GET  /api/settings/rates/     → View current rates
POST /api/settings/rates/     → Update rates
```

### Staff & Shifts
```
GET  /api/staff/              → Staff list
POST /api/staff/{id}/toggle_duty/ → On/off duty toggle
GET  /api/shifts/             → Shift schedules
POST /api/shifts/             → Assign shift (Admin)
```

### Other
```
GET  /api/notifications/           → User notifications
POST /api/notifications/broadcast/ → Send to all users (Admin)
POST /api/notifications/mark_all_read/
GET  /api/subscriptions/           → Subscriptions
POST /api/subscriptions/           → Subscribe to plan
GET  /api/lost-found/              → Lost & found log
POST /api/lost-found/{id}/mark_claimed/
```

---

## 🔄 How It Works

### Booking Flow
```
User selects slot on blueprint
        ↓
Chooses date, entry time, exit time, vehicle type
        ↓
System calculates estimated charge (rate × hours)
        ↓
Booking created → QR code auto-generated
        ↓
User shows QR at gate → Staff scans
        ↓
Entry logged (actual_entry timestamp)
        ↓
Exit logged → overstay calculated if late
        ↓
Payment collected → PDF receipt generated → emailed
```

### Real-Time Updates (WebSocket)
```
Django Channels + Redis
        ↓
ws://localhost:8000/ws/slots/
        ↓
On entry/exit → slot status broadcast to all connected clients
        ↓
Frontend slot blueprint updates color in real-time
```

### Background Tasks (Celery)
- Every 15 min → Check active bookings for overstay
- Every day    → Send subscription expiry reminders (3 days before)
- On payment   → Generate PDF receipt + send email

### Pricing System
| Vehicle | Rate     | Overstay Penalty |
|---------|----------|-----------------|
| Car     | ৳40/hr   | +৳20/hr extra   |
| Bike    | ৳20/hr   | +৳20/hr extra   |
| CNG     | ৳30/hr   | +৳20/hr extra   |

---

## 🚨 Troubleshooting

### "MySQL connection refused"
→ Make sure MySQL is running
→ Check DB_PASSWORD in .env matches your MySQL root password

### "Redis connection refused"
→ Start Redis: `redis-server` (Mac/Linux) or run Redis as Windows service

### "Module not found"
→ Make sure virtual environment is activated: `source venv/bin/activate`

### "WeasyPrint install fails" (Windows)
→ WeasyPrint needs GTK. Install from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
→ Or skip PDF receipt: remove WeasyPrint from requirements.txt (receipts won't generate but app still works)

### Frontend shows "Network Error"
→ Make sure Django is running at http://localhost:8000
→ The frontend works in **Demo Mode** without backend — just use it standalone

---

## 📦 Production Deployment (Optional)

For production use:
1. Set `DEBUG=False` in .env
2. Generate a strong `SECRET_KEY`
3. Use Nginx + Gunicorn + Daphne (for WebSockets)
4. Use a proper MySQL host (not localhost)
5. Set `ALLOWED_HOSTS=yourdomain.com`

```bash
# Install production server
pip install gunicorn daphne

# Run with Daphne (handles both HTTP and WebSocket)
daphne -b 0.0.0.0 -p 8000 park_management.asgi:application
```

---

*ParkManager — Built with Django + Channels + MySQL + Redis + Celery*
