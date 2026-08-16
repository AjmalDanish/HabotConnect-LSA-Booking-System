# 📁 Complete Folder Structure Overview

## Visual Directory Tree

```
habot_booking/                              # 🏠 ROOT PROJECT DIRECTORY
│
├── 📄 manage.py                           # Django management script
│   └── 🎯 Purpose: Command-line tool for Django operations
│       ├── runserver - Start development server
│       ├── migrate - Apply database changes
│       ├── createsuperuser - Create admin account
│       └── test - Run tests
│
├── 📋 requirements.txt                   # Python dependencies
│   ├── Django==4.2.7                     # Core framework
│   ├── djangorestframework==3.14.0       # API toolkit
│   ├── psycopg2-binary==2.9.9            # PostgreSQL adapter
│   ├── pytest==7.4.3                     # Testing framework
│   └── Other dependencies...
│
├── 📋 requirements-dev.txt               # Development dependencies
│   └── Extra tools for testing, linting, debugging
│
├── 📋 pytest.ini                         # Pytest configuration
│   └── 🎯 Purpose: Configure test runner settings
│
├── 📋 .env.example                       # Environment variables template
│   └── 🔐 Purpose: Database credentials, secret keys
│
├── 📋 .gitignore                         # Git ignore patterns
│   └── 🎯 Purpose: Exclude temporary files from version control
│
├── 🚀 setup.sh                           # Automated setup script
│   └── 🎯 Purpose: One-command project initialization
│
├── 🌱 create_sample_data.py             # Sample data generator
│   └── 🎯 Purpose: Populate database with test data
│
├── 📚 README.md                          # Main documentation
│   └── 🎯 Purpose: Complete project documentation
│
├── 📖 QUICKSTART.md                      # Quick start guide
│   └── 🎯 Purpose: 5-minute setup instructions
│
├── 📖 API_DOCUMENTATION.md               # API reference
│   └── 🎯 Purpose: Complete API endpoint documentation
│
├── 📖 PRESENTATION.md                    # Technical presentation
│   └── 🎯 Purpose: 15-slide presentation for interview
│
├── 📖 PROJECT_EXPLANATION.md             # Complete explanation
│   └── 🎯 Purpose: End-to-end system explanation
│
├── 📖 FOLDER_STRUCTURE.md                # This file
│   └── 🎯 Purpose: Folder structure and organization guide
│
├── 📁 habot_booking/                     # ⚙️ MAIN DJANGO PROJECT
│   ├── 📄 __init__.py                    # Package marker
│   ├── 📄 settings.py                    # Django configuration
│   │   └── 🎯 Purpose: Database, apps, middleware, security
│   ├── 📄 urls.py                        # Main URL routing
│   │   └── 🎯 Purpose: Map URLs to application URLs
│   ├── 📄 wsgi.py                        # WSGI configuration
│   │   └── 🎯 Purpose: Production deployment interface
│   └── 📄 celery.py (optional)          # Background tasks (future)
│
├── 📁 bookings/                          # 🎯 MAIN APPLICATION
│   │
│   ├── 📄 __init__.py                    # Package marker
│   │
│   ├── 📄 models.py                      # 🗄️ DATABASE MODELS
│   │   ├── class Parent(models.Model)  # Parents/guardians
│   │   ├── class LSA_Profile(models.Model) # Learning Assistants
│   │   └── class Booking_Request(models.Model) # Bookings
│   │   └── 🎯 Purpose: Define database structure and business logic
│   │
│   ├── 📄 admin.py                       # 🔧 ADMIN INTERFACE
│   │   └── 🎯 Purpose: Configure Django admin panel
│   │       ├── Parent model admin
│   │       ├── LSA_Profile model admin
│   │       └── Booking_Request model admin
│   │
│   ├── 📄 serializers.py                 # 🔄 DATA SERIALIZATION
│   │   ├── ParentSerializer             # Convert Parent objects to JSON
│   │   ├── LSA_ProfileSerializer        # Convert LSA objects to JSON
│   │   ├── Booking_RequestSerializer    # Convert Booking objects to JSON
│   │   └── 🎯 Purpose: Validate data and convert to/from JSON
│   │
│   ├── 📄 views.py                       # 🎮 API LOGIC
│   │   ├── BookingViewSet               # Booking CRUD operations
│   │   ├── LSA_SearchView              # LSA search endpoint
│   │   ├── LSA_AvailabilityView        # Availability checking
│   │   └── 🎯 Purpose: Handle API requests and responses
│   │
│   ├── 📄 urls.py                        # 🛣️ URL ROUTING
│   │   ├── /api/v1/bookings/            # Booking endpoints
│   │   ├── /api/v1/lsas/search/         # LSA search endpoint
│   │   └── /api/v1/payments/webhook/   # Payment webhook
│   │   └── 🎯 Purpose: Define API endpoints
│   │
│   ├── 📄 payment_service.py             # 💳 PAYMENT INTEGRATION
│   │   ├── class MockPaymentGateway     # Mock payment processor
│   │   ├── create_payment_intent()      # Create payment
│   │   ├── process_payment()            # Execute payment
│   │   └── 🎯 Purpose: Handle payment processing
│   │
│   ├── 📄 webhooks.py                    # 🔔 WEBHOOK HANDLERS
│   │   ├── payment_webhook()             # Payment events handler
│   │   ├── handle_payment_success()      # Success events
│   │   ├── handle_payment_failure()      # Failure events
│   │   └── 🎯 Purpose: Process payment notifications
│   │
│   └── 📄 tests.py                       # 🧪 TEST SUITE
│       ├── ParentModelTest               # Parent model tests
│       ├── LSA_ProfileModelTest          # LSA model tests
│       ├── Booking_RequestModelTest      # Booking model tests
│       ├── BookingAPITest                # API endpoint tests
│       ├── PaymentServiceTest           # Payment service tests
│       └── 🎯 Purpose: Ensure code quality and functionality
│
└── 📁 .github/                           # 🔄 CI/CD PIPELINE
    └── 📁 workflows/
        └── 📄 ci.yml                     # GitHub Actions workflow
            ├── Test automation
            ├── Code quality checks
            └── 🎯 Purpose: Automated testing and quality assurance
```

## 🗂️ File Categories & Purposes

### 1️⃣ **Configuration Files** ⚙️
```
├── manage.py              # Django command tool
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── pytest.ini            # Test configuration
├── .env.example          # Environment template
└── .gitignore            # Git exclusions
```

### 2️⃣ **Django Framework Files** 🎨
```
├── habot_booking/
│   ├── settings.py       # Main configuration
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # Production interface
│   └── __init__.py      # Package marker
```

### 3️⃣ **Application Logic Files** 💼
```
├── bookings/
│   ├── models.py        # Database models
│   ├── views.py         # API logic
│   ├── serializers.py  # Data conversion
│   ├── urls.py          # API endpoints
│   ├── admin.py         # Admin panel
│   ├── payment_service.py # Payment processing
│   └── webhooks.py      # Webhook handlers
```

### 4️⃣ **Testing Files** 🧪
```
├── bookings/tests.py    # Test suite
├── pytest.ini          # Test configuration
└── .github/workflows/ci.yml # Automated testing
```

### 5️⃣ **Documentation Files** 📚
```
├── README.md                    # Main documentation
├── QUICKSTART.md               # Quick start guide
├── API_DOCUMENTATION.md        # API reference
├── PRESENTATION.md             # Interview presentation
├── PROJECT_EXPLANATION.md      # Complete explanation
└── FOLDER_STRUCTURE.md         # This file
```

### 6️⃣ **Utility Files** 🛠️
```
├── setup.sh                # Automated setup
├── create_sample_data.py  # Data generation
└── .env.example          # Configuration template
```

## 📊 File Importance Levels

### 🔴 **CRITICAL** (Must have)
```
✅ manage.py              # Django functionality
✅ habot_booking/settings.py  # Configuration
✅ bookings/models.py     # Database structure
✅ bookings/views.py      # API functionality
✅ bookings/serializers.py  # Data handling
✅ requirements.txt       # Dependencies
```

### 🟡 **IMPORTANT** (Should have)
```
✅ bookings/tests.py     # Quality assurance
✅ bookings/urls.py      # API endpoints
✅ README.md            # Documentation
✅ .env.example         # Configuration guide
```

### 🟢 **HELPFUL** (Nice to have)
```
✅ QUICKSTART.md        # User guidance
✅ API_DOCUMENTATION.md # API reference
✅ setup.sh            # Automation
✅ create_sample_data.py # Testing data
```

### 🔵 **BONUS** (Enhanced experience)
```
✅ PRESENTATION.md      # Interview ready
✅ PROJECT_EXPLANATION.md # Learning resource
✅ FOLDER_STRUCTURE.md  # Organization guide
```

## 🔄 Data Flow Through Files

### Request Flow Example:
```
1. User sends request
   ↓
2. habot_booking/urls.py (Main routing)
   ↓
3. bookings/urls.py (Application routing)
   ↓
4. bookings/views.py (Business logic)
   ↓
5. bookings/serializers.py (Data validation)
   ↓
6. bookings/models.py (Database operations)
   ↓
7. PostgreSQL Database
   ↓
8. Response back through same path
```

### Development Workflow:
```
1. Edit bookings/models.py (Define data)
   ↓
2. Run: python manage.py migrate
   ↓
3. Edit bookings/serializers.py (Validate data)
   ↓
4. Edit bookings/views.py (Create logic)
   ↓
5. Edit bookings/urls.py (Add endpoint)
   ↓
6. Edit bookings/tests.py (Test functionality)
   ↓
7. Run: pytest (Verify code)
   ↓
8. Update README.md (Document changes)
```

## 🎯 Quick File Reference

| Need to... | Go to... |
|-----------|----------|
| Change database structure | bookings/models.py |
| Add new API endpoint | bookings/views.py + bookings/urls.py |
| Validate input data | bookings/serializers.py |
| Test new feature | bookings/tests.py |
| Configure database | habot_booking/settings.py |
| Add dependency | requirements.txt |
| Document API | API_DOCUMENTATION.md |
| Understand system | PROJECT_EXPLANATION.md |
| Setup project | QUICKSTART.md |

## 🚀 File Modification Priority

### For New Developers:
1. **Start with**: QUICKSTART.md, PROJECT_EXPLANATION.md
2. **Then explore**: bookings/models.py, bookings/views.py
3. **Then customize**: bookings/serializers.py
4. **Then extend**: bookings/tests.py

### For Deployment:
1. **Configure**: .env file (copy from .env.example)
2. **Install**: requirements.txt
3. **Run migrations**: python manage.py migrate
4. **Start server**: python manage.py runserver

### For Maintenance:
1. **Update dependencies**: requirements.txt
2. **Add tests**: bookings/tests.py
3. **Update docs**: README.md
4. **Check quality**: pytest (automated via CI/CD)

---

## 📝 Notes

- **All Python files** are properly organized in packages
- **All documentation** is in Markdown format for easy reading
- **All configuration** follows Django best practices
- **All testing** is automated via GitHub Actions
- **All security** follows Django recommendations

**This organization ensures**: Easy navigation, clear separation of concerns, and professional project structure! 🎉