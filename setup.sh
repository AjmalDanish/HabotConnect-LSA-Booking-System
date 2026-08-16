#!/bin/bash

# HabotConnect LSA Booking System - Setup Script
# This script helps set up the development environment

echo "🚀 Setting up HabotConnect LSA Booking System..."

# Check Python version
echo "📋 Checking Python version..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOL
# Database Configuration
DB_NAME=habot_booking
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
DJANGO_SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True

# Payment Gateway Configuration
PAYMENT_GATEWAY_MODE=mock
EOL
    echo "✅ .env file created. Please update with your database credentials."
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Run migrations (will fail if database not set up)
echo "🗄️  Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "⚠️  Migration failed. Please ensure PostgreSQL is running and database credentials are correct."
    echo "💡 You can run migrations manually later: python manage.py migrate"
fi

# Create superuser prompt
echo ""
echo "👤 Do you want to create a Django superuser now? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Update .env file with your database credentials"
echo "2. Ensure PostgreSQL is running"
echo "3. Run: python manage.py migrate (if not already done)"
echo "4. Start server: python manage.py runserver"
echo "5. Access API: http://localhost:8000/api/v1/"
echo "6. Access admin: http://localhost:8000/admin/"
echo ""
echo "📚 For testing, run: pytest --cov=bookings --cov-report=html"
echo ""
echo "Happy coding! 🚀"