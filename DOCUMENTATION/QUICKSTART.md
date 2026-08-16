# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+ installed
- PostgreSQL 15+ installed and running
- Git installed

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone [your-repo-url]
cd lsa_booking

# (Optional) Run setup script
chmod +x setup.sh
./setup.sh

# Or manual setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Database
```bash
# Create PostgreSQL database
createdb lsa_booking

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
# DB_NAME=lsa_booking
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
```

### Step 3: Run Migrations
```bash
python manage.py migrate
```

### Step 4: Create Sample Data (Optional)
```bash
python create_sample_data.py
```

### Step 5: Start Server
```bash
python manage.py runserver
```

### Step 6: Test the API
```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Search LSAs
curl http://localhost:8000/api/v1/lsas/search/

# Access admin panel
# http://localhost:8000/admin/
# (Create superuser first: python manage.py createsuperuser)
```

## 🧪 Run Tests
```bash
# Run all tests with coverage
pytest --cov=bookings --cov-report=html

# Run specific tests
pytest bookings/tests.py::BookingAPITest::test_create_booking_api_success

# View coverage report
open htmlcov/index.html
```

## 📚 API Testing Examples

### Create a Booking
```bash
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "parent": 1,
    "lsa": 1,
    "child_name": "Test Child",
    "child_age": 10,
    "learning_needs": "Test support",
    "session_type": "online",
    "start_time": "2024-08-13T10:00:00Z",
    "end_time": "2024-08-13T12:00:00Z",
    "subject": "Math",
    "goals": "Test goals",
    "hourly_rate": "45.00",
    "total_hours": "2.00",
    "total_amount": "90.00",
    "currency": "USD"
  }'
```

### Test Double-Booking Prevention
```bash
# Try to create overlapping booking (should fail)
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "parent": 1,
    "lsa": 1,
    "child_name": "Test Child",
    "child_age": 10,
    "learning_needs": "Test support",
    "session_type": "online",
    "start_time": "2024-08-13T11:00:00Z",
    "end_time": "2024-08-13T13:00:00Z",
    "subject": "Math",
    "goals": "Test goals",
    "hourly_rate": "45.00",
    "total_hours": "2.00",
    "total_amount": "90.00",
    "currency": "USD"
  }'
```

### Test Payment Webhook
```bash
curl -X POST http://localhost:8000/api/v1/payments/webhook/test/ \
  -H "Content-Type: application/json" \
  -d '{"scenario":"success","booking_id":1}'
```

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U postgres -d lsa_booking

# Check database exists
psql -U postgres -l
```

### Migration Issues
```bash
# Reset migrations (WARNING: Deletes data)
python manage.py migrate --zero
python manage.py migrate

# Create new database
dropdb lsa_booking && createdb lsa_booking
python manage.py migrate
```

### Port Already in Use
```bash
# Use different port
python manage.py runserver 8001
```

## 📖 Next Steps

1. **Explore the Admin Panel**: http://localhost:8000/admin/
2. **Read the Documentation**: Check README.md and API_DOCUMENTATION.md
3. **Review the Tests**: Look at bookings/tests.py for usage examples
4. **Check the Presentation**: Review PRESENTATION.md for architecture details

## 🎯 Key Features to Try

- [ ] Create a booking via API
- [ ] Search for LSAs with different filters
- [ ] Try to double-book an LSA (should be prevented)
- [ ] Test the payment webhook system
- [ ] Check LSA availability
- [ ] Run the test suite
- [ ] Explore the admin interface

## 📞 Need Help?

- Check the main README.md for detailed documentation
- Review API_DOCUMENTATION.md for API examples
- Look at tests in bookings/tests.py for code examples
- Examine the presentation slides in PRESENTATION.md

Happy coding! 🚀