# LSA Booking System

## 🚀 Project Overview

This is a production-ready backend prototype for an LSA (Learning Support Assistant) Service Booking system. The platform connects parents with Learning Support Assistants for children with learning difficulties, built with Django REST Framework and optimized for performance and data integrity.

**Assignment**: Python Backend Developer - Hiring Project
**Submission Date**: August 13th, 2026
**Author**: Ajmal Danish
**Contact**: ajmaldanish0786@gmail.com
**GitHub**: https://github.com/AjmalDanish

## 🏗️ Architecture & Design Choices

### MVC vs MVT Pattern

This project implements Django's **MVT (Model-View-Template)** pattern, which is Django's interpretation of the traditional MVC architecture:

- **Model**: Handles data structure and business logic
- **View**: Handles user request processing and response formatting
- **Template**: Handles presentation layer (minimal in this API-focused project)

**Why MVT over MVC?**
- Django's built-in ORM and admin interface work seamlessly with MVT
- Better separation of concerns for API development
- Reduced boilerplate code compared to traditional MVC
- Built-in validation and serialization capabilities

### Database Design Principles

The database schema follows these principles:

1. **Normalization**: Third Normal Form (3NF) compliance
2. **Referential Integrity**: Foreign key constraints and cascading rules
3. **Indexing Strategy**: Strategic indexes on frequently queried columns
4. **Poka-Yoke Design**: Built-in validation prevents double-bookings and data inconsistencies

### Query Optimization Strategy

The system employs several techniques to prevent the N+1 query problem:

1. **select_related()**: For forward Foreign Key relationships
2. **prefetch_related()**: For reverse Foreign Key and Many-to-Many relationships
3. **Database Indexes**: Strategic indexing on filter and join columns
4. **QuerySet Caching**: Efficient queryset evaluation and caching

## 📁 Project Structure

```
lsa_booking/
├── lsa_booking/          # Main project directory
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── bookings/             # Main application
│   ├── models.py         # Database models
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   ├── urls.py           # API URLs
│   ├── admin.py          # Admin interface
│   ├── payment_service.py # Mock payment gateway
│   ├── webhooks.py       # Payment webhook handlers
│   └── tests.py          # Comprehensive test suite
├── requirements.txt      # Python dependencies
├── pytest.ini           # Pytest configuration
├── manage.py            # Django management script
└── .github/workflows/   # CI/CD pipeline
```

## 🗄️ Database Schema

### Entities and Relationships

#### 1. **Parent** Model
- Represents parents/guardians seeking LSA services
- **Key Fields**: personal information, contact details, address
- **Indexes**: email (unique), city, state for search optimization

#### 2. **LSA_Profile** Model
- Represents Learning Support Assistants
- **Key Fields**: professional details, skills, availability, pricing
- **Indexes**: email (unique), experience_level, location fields
- **Relationships**: One-to-Many with Booking_Request

#### 3. **Booking_Request** Model
- Represents booking sessions between parents and LSAs
- **Key Fields**: session details, payment information, status tracking
- **Indexes**: composite indexes on time ranges and status fields
- **Relationships**: Many-to-One with both Parent and LSA_Profile

### Key Database Features

- **Composite Indexes**: `(start_time, end_time)`, `(parent, status)`
- **Unique Constraints**: Email addresses for all users
- **Validation**: Built-in datetime and amount validation
- **Cascading Deletes**: Proper foreign key handling

## 🔌 API Endpoints

### Health Check
```
GET /api/v1/health/
```
Returns system health status and version information.

### Booking Management

#### Create Booking
```
POST /api/v1/bookings/
```
Creates a new booking request with automatic validation.

**Request Body:**
```json
{
  "parent": 1,
  "lsa": 2,
  "child_name": "Tom",
  "child_age": 10,
  "learning_needs": "ADHD support",
  "session_type": "online",
  "start_time": "2024-08-12T10:00:00Z",
  "end_time": "2024-08-12T12:00:00Z",
  "subject": "Math",
  "goals": "Improve math skills",
  "hourly_rate": "45.00",
  "total_hours": "2.00",
  "total_amount": "90.00",
  "currency": "USD"
}
```

**Response:** `201 Created` with booking details

#### List Bookings
```
GET /api/v1/bookings/
```
Returns paginated list of bookings with optional filtering.

**Query Parameters:**
- `status`: Filter by booking status
- `payment_status`: Filter by payment status
- `parent_id`: Filter by parent
- `lsa_id`: Filter by LSA

#### Confirm Booking
```
POST /api/v1/bookings/{id}/confirm/
```
Confirms a booking after successful payment verification.

#### Cancel Booking
```
POST /api/v1/bookings/{id}/cancel/
```
Cancels a booking with optional reason.

### LSA Search

#### Search Available LSAs
```
GET /api/v1/lsas/search/
```
Search for LSAs with optimized queries (no N+1 problems).

**Query Parameters:**
- `skills`: Comma-separated skill filters (e.g., "ADHD,Autism")
- `city`: Location filter
- `state`: State filter
- `experience_level`: Experience level filter
- `min_hourly_rate` / `max_hourly_rate`: Price range filter
- `specialization`: Specialization filter

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "full_name": "Jane Smith",
      "specialization": "ADHD",
      "hourly_rate": "45.00",
      "skills_list": ["ADHD", "Autism", "Sign Language"]
    }
  ]
}
```

#### Check Availability
```
GET /api/v1/lsas/check-availability/?lsa_id=1&start_time=2024-08-12T10:00:00Z&end_time=2024-08-12T12:00:00Z
```
Check specific LSA availability for a time period.

### Payment Webhooks

#### Payment Webhook
```
POST /api/v1/payments/webhook/
```
Handles payment success/failure events and automatically updates booking status.

**Webhook Payload:**
```json
{
  "event": "payment.success",
  "payment_id": "pay_12345",
  "booking_id": 1,
  "amount": 90.00,
  "currency": "USD",
  "timestamp": "2024-08-12T10:30:00Z"
}
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip and virtualenv

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd lsa_booking
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file
   DB_NAME=lsa_booking
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DJANGO_SECRET_KEY=your-secret-key
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Access API**
   - API Base URL: `http://localhost:8000/api/v1/`
   - Admin Panel: `http://localhost:8000/admin/`

## 🧪 Testing

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=bookings --cov-report=html

# Run specific test module
pytest bookings/tests.py

# Run with verbose output
pytest -v
```

### Test Coverage

The project includes comprehensive test coverage:
- **Model Tests**: Data validation, relationships, business logic
- **API Tests**: Endpoint functionality, error handling
- **Integration Tests**: End-to-end workflows
- **Payment Service Tests**: Mock payment gateway operations

**Coverage Areas:**
- ✅ Success scenarios
- ✅ Edge cases and boundary conditions
- ✅ Failure scenarios and error handling
- ✅ Double-booking prevention (Poka-Yoke)
- ✅ Payment webhook processing

## 🔒 Security Features

### Data Integrity & Validation

1. **Double-Booking Prevention**: Built-in validation prevents overlapping sessions
2. **Payment Validation**: Automatic amount calculation and verification
3. **Input Validation**: Comprehensive serializer validation
4. **SQL Injection Protection**: Django ORM parameterized queries

### Authentication & Authorization

- Admin panel authentication required
- API endpoints designed for future JWT integration
- Proper CORS configuration for frontend integration

### Error Handling

- Comprehensive exception handling in payment service
- Detailed error messages for API clients
- Logging for debugging and monitoring

## 📊 Performance Optimizations

### Database Query Optimization

1. **N+1 Query Prevention**
   ```python
   # Instead of multiple queries (N+1 problem)
   bookings = Booking_Request.objects.all()  # Bad
   for booking in bookings:
       print(booking.parent.name)  # N+1 queries!

   # Optimized approach
   bookings = Booking_Request.objects.select_related('parent', 'lsa')  # Good!
   for booking in bookings:
       print(booking.parent.name)  # No additional queries
   ```

2. **Strategic Indexing**
   - Email fields (unique)
   - Location fields (city, state)
   - Status fields
   - Time ranges (start_time, end_time)

3. **QuerySet Caching**
   - Efficient queryset evaluation
   - Prefetch for reverse relationships

### API Performance

- Pagination enabled (20 items per page)
- Efficient serialization
- Minimal data transfer with selective field exposure

## 🔄 CI/CD Pipeline

The project includes automated testing via GitHub Actions:

**Pipeline Features:**
- Automatic testing on push/PR
- PostgreSQL service integration
- Code coverage reporting
- Flake8 code quality checks
- Automated deployment readiness checks

**Workflow:**
1. Code checkout
2. Python environment setup
3. Dependency installation
4. Database migrations
5. Test execution with coverage
6. Code quality checks

## 📝 API Documentation Examples

### Creating a Booking

```bash
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "parent": 1,
    "lsa": 2,
    "child_name": "Tom",
    "child_age": 10,
    "learning_needs": "ADHD support",
    "session_type": "online",
    "start_time": "2024-08-12T10:00:00Z",
    "end_time": "2024-08-12T12:00:00Z",
    "subject": "Math",
    "goals": "Improve math skills",
    "hourly_rate": "45.00",
    "total_hours": "2.00",
    "total_amount": "90.00",
    "currency": "USD"
  }'
```

### Searching LSAs

```bash
curl -X GET "http://localhost:8000/api/v1/lsas/search/?skills=ADHD&city=Los+Angeles&min_hourly_rate=30&max_hourly_rate=60"
```

### Payment Webhook Simulation

```bash
curl -X POST http://localhost:8000/api/v1/payments/webhook/test/ \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "success",
    "booking_id": 1
  }'
```

## 🎯 Key Features & Implementation

### ✅ Implemented Requirements

- ✅ Normalized and indexed relational database schema
- ✅ High-performance query optimization (N+1 prevention)
- ✅ Robust booking API with double-booking prevention
- ✅ Automated webhook endpoint for payment events
- ✅ Comprehensive test suite (pytest)
- ✅ Technical documentation
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Mock payment gateway integration
- ✅ Admin interface for data management

### 🛡️ Poka-Yoke Design Patterns

The system implements mistake-proofing (Poka-Yoke) principles:

1. **Automatic Booking Validation**: Prevents overlapping sessions
2. **Payment Amount Verification**: Automatic calculation and validation
3. **Availability Checks**: Real-time LSA availability verification
4. **Status Automation**: Automatic status transitions based on events

## 🚧 Future Enhancements

- JWT authentication and authorization
- Real-time notifications system
- Advanced scheduling and calendar integration
- Rating and review system
- Payment gateway integration (Stripe/PayPal)
- WebSocket support for real-time updates
- Redis caching for improved performance
- Docker containerization
- Kubernetes deployment configuration

## 📞 Contact & Support

**Project**: LSA Booking System - Python Backend Developer Project
**Author**: Ajmal Danish
**Email**: ajmaldanish0786@gmail.com
**GitHub**: https://github.com/AjmalDanish

---

**Built with Django REST Framework**
*Connecting families with specialized learning support*