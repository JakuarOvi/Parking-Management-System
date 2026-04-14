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



### Frontend
The frontend is a single HTML file. Open `frontend/index.html` in a browser after starting the backend server.




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
