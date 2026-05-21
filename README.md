# SmartHelmet — IoT Smart Helmet Safety System

A full-stack IoT-based smart helmet system for rider safety, featuring real-time fall detection, GPS tracking, emergency SOS alerts, and a live monitoring dashboard.

## Architecture

```
┌──────────────┐     HTTP/POST      ┌──────────────────┐     WebSocket     ┌──────────────────┐
│   ESP32 +    │ ──────────────────► │  Django Backend   │ ◄──────────────► │  React Frontend  │
│  MPU6050 +   │   Sensor/GPS/Alert  │  (DRF + Channels) │    Real-time     │  (Vite + Recharts│
│  GPS + GSM   │                     │                    │    Dashboard     │  + Leaflet)      │
└──────────────┘                     └──────────────────┘                   └──────────────────┘
```

### Tech Stack

| Layer      | Technology                                      |
|------------|--------------------------------------------------|
| Firmware   | ESP32, MPU6050, NEO-6M GPS, SIM800L GSM, BLE    |
| Backend    | Django 5, Django REST Framework, Channels, JWT   |
| Frontend   | React 19, Vite, Recharts, Leaflet, Lucide Icons  |
| Database   | SQLite (dev) / PostgreSQL (production)            |
| Real-time  | Django Channels (WebSocket)                       |

## Project Structure

```
smartproject/
├── firmware/           # ESP32 Arduino code (sensors, BLE, GSM)
│   └── src/
│       ├── main.ino
│       └── config.h
├── backend/            # Django REST API + WebSocket server
│   ├── smarthelmet/    # Django project settings & config
│   ├── api/            # Main app (models, views, serializers)
│   │   ├── views/      # Split by feature (auth, device, alerts, etc.)
│   │   ├── management/commands/
│   │   │   ├── simulate.py    # Sensor data simulator
│   │   │   └── seed_data.py   # Dev data seeding
│   │   └── ...
│   └── requirements.txt
└── frontend/           # React SPA dashboard
    └── src/
        ├── pages/      # Dashboard, MapView, Alerts, SOS, Settings
        ├── components/ # Sidebar, ProtectedRoute
        ├── services/   # Axios API client
        ├── context/    # Auth state management
        └── hooks/      # WebSocket hook
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Arduino IDE / PlatformIO (for firmware)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env       # Edit with your secret key

# Run migrations
python manage.py migrate

# Seed test data
python manage.py seed_data

# Start server (with WebSocket support)
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env       # Edit API URLs if needed

# Start dev server
npm run dev
```

### Simulator (Optional)

```bash
cd backend
python manage.py simulate    # Generates realistic sensor data
```

The app will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000/api/
- **Default login**: `admin` / `admin123`

## Features

- **Real-time Dashboard** — Live accelerometer & gyroscope charts via WebSocket
- **GPS Tracking** — Live map with Leaflet showing rider location & trail
- **Fall Detection** — Automatic alerts when abnormal G-force is detected
- **SOS System** — One-tap emergency alert with location sharing
- **Alert Management** — View, resolve, and track safety alerts
- **Emergency Contacts** — Manage contacts for SMS notifications
- **Device Settings** — Configure fall thresholds and device parameters
- **JWT Authentication** — Secure login with token refresh

## API Endpoints

| Method | Endpoint                          | Auth     | Description               |
|--------|-----------------------------------|----------|---------------------------|
| POST   | `/api/auth/register/`             | No       | User registration          |
| POST   | `/api/auth/login/`                | No       | JWT token obtain           |
| POST   | `/api/auth/refresh/`              | No       | JWT token refresh          |
| GET    | `/api/auth/profile/`              | Yes      | Get user profile           |
| GET    | `/api/dashboard/`                 | Yes      | Dashboard summary          |
| POST   | `/api/sensor-data/`               | No (ESP) | Post sensor readings       |
| POST   | `/api/gps/`                       | No (ESP) | Post GPS location          |
| POST   | `/api/alert/`                     | No (ESP) | Post alert from device     |
| GET    | `/api/alerts/`                    | Yes      | List user alerts           |
| POST   | `/api/sos/`                       | Yes      | Trigger SOS from web app   |
| WS     | `/ws/dashboard/`                  | No       | Real-time data stream      |

## License

This project is part of a final year academic project.
