# ParkManager - Smart Parking Management System

A full-stack web application for managing parking slots, bookings, subscriptions, and staff operations with admin controls.

## Features

### User Management
- User registration with car number-based authentication
- Role-based access (User, Staff, Admin)
- User profile management
- Staff account creation with auto-generated credentials
- Staff ID card generation

### Parking Management
- Parking slot management (3 floors, 3 zones each)
- Real-time slot availability tracking
- Parking blueprints visualization
- Support for multiple vehicle types (Car, Bike, CNG)

### Booking System
- User slot booking with date/time selection
- Admin can book slots for users (auto-creates user accounts)
- QR code generation for bookings
- Automatic charge calculation based on parking duration
- Overstay detection and penalties

### Subscription Plans
- Basic Plan (৳500/month) - 1 reserved Bike slot, 10% discount
- Gold Plan (৳800/month) - Reserved Car slot, 15% discount
- Premium Plan (৳1200/month) - 2 reserved Car slots, 25% discount, waived overstay

### Payment Management
- Payment tracking (Cash, bKash, Nagad, Bank Transfer)
- Staff can mark payments as paid
- PDF receipt generation
- Payment status management

### Admin Dashboard
- Real-time occupancy statistics
- Income tracking (daily/monthly/yearly)
- Booking and subscription management
- Staff management and shift scheduling
- Lost & Found tracking
- Notification broadcasting

### Staff Operations
- Gate scanner for entry/exit (QR codes)
- Today's bookings view
- Cash payment collection
- Shift schedule management
- Duty status toggling

## Project Structure

```
ParkManager_FullStack/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3
│   ├── park_management/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── parking/
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── urls.py
│       ├── auth_urls.py
│       ├── permissions.py
│       ├── admin.py
│       └── migrations/
├── frontend/
│   └── index.html          # Single-page dashboard application
├── docs/
│   └── SETUP_GUIDE.md      # Setup instructions
└── database_setup.sql      # Database schema

```

## Technology Stack

### Backend
- **Framework:** Django 4.2.7
- **API:** Django REST Framework 3.14.0
- **Database:** SQLite3 (configurable to MySQL)
- **Authentication:** Session-based
- **WebSockets:** Channels 4.0.0
- **Task Queue:** Celery 5.3.4
- **QR Codes:** qrcode 7.4.2
- **PDF Generation:** WeasyPrint 60.1

### Frontend
- **Markup:** HTML5
- **Styling:** Custom CSS3 (responsive design)
- **Scripting:** Vanilla JavaScript (no frameworks)
- **Charts:** Chart.js 4.4.0

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Git

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

### Frontend
The frontend is a single HTML file. Open `frontend/index.html` in a browser after starting the backend server.

- **Backend runs on:** http://127.0.0.1:8000/
- **API endpoint:** http://127.0.0.1:8000/api/
- **Frontend connects to:** `http://localhost:8000` (configurable in code)

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/change-password/` - Change password

### Bookings
- `GET /api/bookings/` - List user bookings
- `POST /api/bookings/` - Create booking
- `POST /api/bookings/{id}/cancel/` - Cancel booking
- `POST /api/bookings/{id}/scan_entry/` - Mark entry
- `POST /api/bookings/{id}/scan_exit/` - Mark exit

### Payments
- `GET /api/payments/` - List payments
- `POST /api/payments/{id}/mark_paid/` - Mark payment as paid

### Subscriptions
- `GET /api/subscriptions/` - List subscriptions
- `POST /api/subscriptions/` - Create subscription

### Staff
- `GET /api/staff/` - List staff members
- `POST /api/staff/` - Create staff account
- `POST /api/staff/{id}/toggle_duty/` - Toggle on-duty status

### Slots
- `GET /api/slots/` - List parking slots
- `GET /api/slots/blueprint/` - Parking slot visualization

## Default Credentials

### Admin
- **Car Number:** `DHA-1234`
- **Password:** Configure via `create_admin.py`

### Staff Examples
- **ID:** `ST001` | **Car:** `DHA-0001` | **Password:** `ST001`
- **ID:** `ST002` | **Car:** `DHA-0002` | **Password:** `ST002`

## Configuration

Edit `backend/park_management/settings.py`:
- `DEBUG` - Toggle debug mode
- `ALLOWED_HOSTS` - Allowed host domains
- `DATABASES` - Database configuration
- `CORS_ALLOW_ALL_ORIGINS` - API CORS settings

Environment variables (`.env`):
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=park_management
DB_USER=root
DB_PASSWORD=your_password
```

## Usage

1. **Register as User:** Click "New user? Register here" and fill in car number, name, and password
2. **Login:** Use car number + password to login
3. **Book Slot:** Navigate to "Book a Slot", select floor/zone, and confirm booking
4. **Subscribe:** Go to "Subscription" and choose a plan
5. **Admin Functions:** Login with admin account to access admin dashboard

## Features Implemented

✅ User registration with car number validation  
✅ Admin bookings with auto-user creation  
✅ Staff account creation with auto-generated credentials  
✅ Staff ID card generation (printable)  
✅ Subscription plans with form confirmation  
✅ Payment marking by staff (auto-removes booking)  
✅ Chat functionality removed  
✅ QR code generation for bookings  
✅ Occupancy tracking and reports  
✅ Shift scheduling  
✅ Lost & Found system  

## Troubleshooting

### Backend not connecting
- Ensure Django server is running: `python manage.py runserver 8000`
- Check if backend is at `http://127.0.0.1:8000/`

### Registration fails
- Car number must match format: 2-3 letters + dash + 4 digits (e.g., `DHA-1234`)
- All required fields must be filled

### API returns 403 Forbidden
- Login first if accessing protected endpoints
- Check user role has required permissions

## Future Enhancements

- Mobile app version
- Payment gateway integration (bKash, Nagad, Rocket)
- SMS/Email notifications via Twilio
- Real-time WebSocket improvements
- Advanced analytics and reporting
- Multi-location support

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Version:** 1.0.0  
**Last Updated:** April 13, 2026  
**Author:** ParkManager Development Team
