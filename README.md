<div align="center">

# 🎓 LSA Booking System

**Production-ready backend for connecting parents with Learning Support Assistants (LSAs) for children with learning difficulties**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.14.0-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)
![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen.svg)
![CI](https://github.com/AjmalDanish/LSA-Booking-System/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-70%25-yellow.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📌 Overview

A complete **REST API backend** for an LSA (Learning Support Assistant) service booking platform. Parents can search for specialized LSAs (ADHD, Autism, Dyslexia support, etc.), check real-time availability, create bookings with automatic double-booking prevention (Poka-Yoke), and process payments through a mock payment gateway with webhook integration.

Built as a **Python Backend Developer hiring project** with a strong focus on:

- 🛡️ **Data integrity** — mistake-proofing (Poka-Yoke) validation at model & serializer level
- ⚡ **Query optimization** — N+1 prevention with `select_related` / `prefetch_related`
- 🗄️ **Database design** — 3NF normalization, strategic composite indexes, referential integrity
- 🧪 **Comprehensive testing** — 18 tests covering success, edge, and failure scenarios (70% coverage)
- 🔄 **CI/CD** — GitHub Actions with PostgreSQL service, automated tests, coverage & flake8 linting

## 🏗️ Tech Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Framework  | Django 4.2.7 + Django REST Framework 3.14     |
| Database   | PostgreSQL 15+ (psycopg2)                      |
| Testing    | pytest, pytest-django, coverage, factory-boy   |
| CI/CD      | GitHub Actions (test + lint jobs)              |
| Tooling    | django-environ, flake8, black, isort           |

## ✨ Key Features

- **LSA Search API** — filter by skills, city, state, experience level, specialization & hourly rate range
- **Availability Check API** — real-time slot validation with overlapping-booking detection
- **Booking API** — full CRUD with automatic amount calculation and validation
- **Poka-Yoke Double-Booking Prevention** — enforced at both serializer and model level across all active booking statuses
- **Mock Payment Gateway** — payment intents, processing, and automatic status transitions
- **Webhook Endpoint** — handles `payment.success` / `payment.failed` / `payment.refunded` events
- **Admin Panel** — full Django admin interface for parents, LSAs and bookings
- **Health Check** — `/api/v1/health/` monitoring endpoint

## 📁 Project Structure

```
LSA-Booking-System/
├── lsa_booking/            # Django project (settings, urls, wsgi)
├── bookings/                # Main application
│   ├── models.py            # Parent, LSA_Profile, Booking_Request (indexed, normalized)
│   ├── serializers.py       # DRF serializers + Poka-Yoke validation
│   ├── views.py             # ViewSets & API views (N+1-free queries)
│   ├── urls.py              # API routing
│   ├── payment_service.py   # Mock payment gateway
│   ├── webhooks.py          # Payment webhook handlers
│   ├── admin.py             # Admin interface
│   ├── migrations/          # Database migrations
│   └── tests.py             # 18 tests (model, API, integration, payment)
├── DOCUMENTATION/           # Full technical documentation
├── .github/workflows/       # CI/CD pipeline (test + lint)
├── requirements.txt         # Dependencies
├── setup.sh                 # One-command setup script
└── create_sample_data.py    # Sample data generator
```

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- PostgreSQL 15+

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AjmalDanish/LSA-Booking-System.git
cd LSA-Booking-System

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env            # then edit with your database credentials

# 5. Run migrations and start
python manage.py migrate
python manage.py runserver
```

Or use the one-command setup:

```bash
./setup.sh
```

### Useful Commands

```bash
python manage.py createsuperuser          # Create admin user
python manage.py runserver                # Start dev server at :8000
python manage.py shell < create_sample_data.py   # Seed sample data
pytest --cov=bookings --cov-report=html   # Run tests with coverage
```

**API Base URL**: `http://localhost:8000/api/v1/` · **Admin**: `http://localhost:8000/admin/`

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health/` | Health check |
| `POST` | `/api/v1/bookings/` | Create booking (validated, double-booking safe) |
| `GET` | `/api/v1/bookings/` | List bookings (paginated, filterable) |
| `GET` | `/api/v1/bookings/{id}/` | Retrieve booking |
| `PATCH` | `/api/v1/bookings/{id}/` | Update booking |
| `POST` | `/api/v1/bookings/{id}/confirm/` | Confirm booking |
| `POST` | `/api/v1/bookings/{id}/cancel/` | Cancel booking |
| `GET` | `/api/v1/lsas/search/` | Search LSAs (skills, location, rate filters) |
| `GET` | `/api/v1/lsas/check-availability/` | Check LSA availability for a time slot |
| `POST` | `/api/v1/payments/webhook/` | Payment webhook (success/failed/refunded) |
| `POST` | `/api/v1/payments/webhook/test/` | Simulate payment webhook events |

### Example: Create a Booking

```bash
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "parent": 1,
    "lsa": 1,
    "child_name": "Tom",
    "child_age": 10,
    "learning_needs": "ADHD support",
    "session_type": "online",
    "start_time": "2026-08-12T10:00:00Z",
    "end_time": "2026-08-12T12:00:00Z",
    "subject": "Math",
    "goals": "Improve math skills",
    "hourly_rate": "45.00",
    "total_hours": "2.00",
    "total_amount": "90.00",
    "currency": "USD"
  }'
```

## 🧪 Testing

```bash
# Full suite with coverage
pytest --cov=bookings --cov-report=html

# Specific tests
pytest bookings/tests.py -v
```

Coverage areas: ✅ model validation ✅ double-booking prevention ✅ amount auto-calculation ✅ API endpoints ✅ payment gateway ✅ webhook processing ✅ LSA search & availability

## 🔄 CI/CD Pipeline

GitHub Actions runs on every push/PR to `main`/`develop`:

1. **Test job** — Python 3.11 + PostgreSQL 15 service → migrations → pytest with coverage (uploaded to Codecov)
2. **Lint job** — flake8 (max-line-length=120) across `bookings/` and `lsa_booking/`

## 📚 Documentation

Detailed technical documentation lives in [`DOCUMENTATION/`](DOCUMENTATION/):

- [Project Explanation](DOCUMENTATION/PROJECT_EXPLANATION.md) — architecture, design decisions, database schema
- [API Documentation](DOCUMENTATION/API_DOCUMENTATION.md) — full endpoint reference with examples
- [Quickstart Guide](DOCUMENTATION/QUICKSTART.md) — environment setup & sample data
- [Visual Flowcharts](DOCUMENTATION/VISUAL_FLOWCHARTS.md) — booking & payment flows
- [Folder Structure](DOCUMENTATION/FOLDER_STRUCTURE.md)
- [Presentation](DOCUMENTATION/PRESENTATION.md)

## 🗺️ Roadmap

- [ ] JWT authentication & authorization
- [ ] Stripe / PayPal real payment gateway
- [ ] Redis caching & rate limiting
- [ ] Docker & Kubernetes deployment
- [ ] Real-time notifications (WebSockets)
- [ ] Rating & review system

## 📄 License

Distributed under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ by [Ajmal Danish](https://github.com/AjmalDanish) · Django REST Framework · PostgreSQL**

*Connecting families with specialized learning support*

</div>
