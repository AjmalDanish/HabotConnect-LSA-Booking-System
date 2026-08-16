"""
Sample Data Generation Script for Testing
Populate the database with sample Parents, LSAs, and Bookings for testing
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lsa_booking.settings')
django.setup()

from bookings.models import Parent, LSA_Profile, Booking_Request


def create_sample_parents():
    """Create sample parent accounts."""
    parents_data = [
        {
            'first_name': 'John', 'last_name': 'Doe',
            'email': 'john.doe@example.com', 'phone': '+1234567890',
            'gender': 'M', 'address': '123 Main St', 'city': 'New York',
            'state': 'NY', 'postal_code': '10001', 'date_of_birth': '1980-05-15'
        },
        {
            'first_name': 'Sarah', 'last_name': 'Johnson',
            'email': 'sarah.j@example.com', 'phone': '+1234567891',
            'gender': 'F', 'address': '456 Oak Ave', 'city': 'Los Angeles',
            'state': 'CA', 'postal_code': '90001', 'date_of_birth': '1985-08-22'
        },
        {
            'first_name': 'Michael', 'last_name': 'Williams',
            'email': 'm.williams@example.com', 'phone': '+1234567892',
            'gender': 'M', 'address': '789 Pine Rd', 'city': 'Chicago',
            'state': 'IL', 'postal_code': '60601', 'date_of_birth': '1978-12-10'
        },
    ]

    parents = []
    for data in parents_data:
        parent, created = Parent.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
        parents.append(parent)
        print(f"{'Created' if created else 'Found'} parent: {parent.full_name}")

    return parents


def create_sample_lsas():
    """Create sample LSA profiles."""
    lsas_data = [
        {
            'first_name': 'Jane', 'last_name': 'Smith',
            'email': 'jane.smith@example.com', 'phone': '+9876543210',
            'gender': 'F', 'qualification': 'bachelor',
            'experience_level': 'intermediate', 'years_of_experience': 3,
            'specialization': 'ADHD', 'address': '321 Elm St',
            'city': 'Los Angeles', 'state': 'CA', 'postal_code': '90001',
            'skills': 'ADHD,Autism,Child Psychology',
            'hourly_rate': Decimal('45.00'), 'verified': True,
            'profile_status': 'active'
        },
        {
            'first_name': 'Emily', 'last_name': 'Brown',
            'email': 'emily.brown@example.com', 'phone': '+9876543211',
            'gender': 'F', 'qualification': 'master',
            'experience_level': 'senior', 'years_of_experience': 7,
            'specialization': 'Autism', 'address': '654 Maple Dr',
            'city': 'New York', 'state': 'NY', 'postal_code': '10002',
            'skills': 'Autism,Sign Language,Applied Behavior Analysis',
            'hourly_rate': Decimal('55.00'), 'verified': True,
            'profile_status': 'active'
        },
        {
            'first_name': 'David', 'last_name': 'Lee',
            'email': 'david.lee@example.com', 'phone': '+9876543212',
            'gender': 'M', 'qualification': 'bachelor',
            'experience_level': 'entry', 'years_of_experience': 1,
            'specialization': 'Dyslexia', 'address': '987 Oak Ln',
            'city': 'Chicago', 'state': 'IL', 'postal_code': '60602',
            'skills': 'Dyslexia,Reading Intervention,Multisensory Teaching',
            'hourly_rate': Decimal('35.00'), 'verified': True,
            'profile_status': 'active'
        },
        {
            'first_name': 'Lisa', 'last_name': 'Garcia',
            'email': 'lisa.garcia@example.com', 'phone': '+9876543213',
            'gender': 'F', 'qualification': 'phd',
            'experience_level': 'expert', 'years_of_experience': 12,
            'specialization': 'Learning Disabilities', 'address': '147 Pine St',
            'city': 'Houston', 'state': 'TX', 'postal_code': '77001',
            'skills': 'Learning Disabilities,Assessment,Educational Therapy',
            'hourly_rate': Decimal('75.00'), 'verified': True,
            'profile_status': 'active'
        },
        {
            'first_name': 'Robert', 'last_name': 'Chen',
            'email': 'robert.chen@example.com', 'phone': '+9876543214',
            'gender': 'M', 'qualification': 'master',
            'experience_level': 'senior', 'years_of_experience': 8,
            'specialization': 'Executive Function', 'address': '258 Cedar Ave',
            'city': 'Seattle', 'state': 'WA', 'postal_code': '98101',
            'skills': 'Executive Function,ADHD,Study Skills,Time Management',
            'hourly_rate': Decimal('60.00'), 'verified': True,
            'profile_status': 'active'
        },
    ]

    lsas = []
    for data in lsas_data:
        lsa, created = LSA_Profile.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
        lsas.append(lsa)
        print(f"{'Created' if created else 'Found'} LSA: {lsa.full_name} - {lsa.specialization}")

    return lsas


def create_sample_bookings(parents, lsas):
    """Create sample booking requests."""
    booking_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    payment_statuses = ['pending', 'completed', 'failed']

    bookings_data = [
        {
            'parent': parents[0], 'lsa': lsas[0],
            'child_name': 'Tom', 'child_age': 10, 'child_grade': '5th',
            'learning_needs': 'ADHD support for math', 'session_type': 'online',
            'start_time': datetime.now() + timedelta(days=1),
            'end_time': datetime.now() + timedelta(days=1, hours=2),
            'subject': 'Math', 'goals': 'Improve focus and calculation skills',
            'hourly_rate': lsas[0].hourly_rate, 'total_hours': Decimal('2.00'),
            'status': 'confirmed', 'payment_status': 'completed'
        },
        {
            'parent': parents[1], 'lsa': lsas[1],
            'child_name': 'Emma', 'child_age': 8, 'child_grade': '3rd',
            'learning_needs': 'Autism spectrum support', 'session_type': 'in_person',
            'start_time': datetime.now() + timedelta(days=2),
            'end_time': datetime.now() + timedelta(days=2, hours=1),
            'subject': 'Social Skills', 'goals': 'Improve social interaction',
            'hourly_rate': lsas[1].hourly_rate, 'total_hours': Decimal('1.00'),
            'status': 'completed', 'payment_status': 'completed'
        },
        {
            'parent': parents[2], 'lsa': lsas[2],
            'child_name': 'Jake', 'child_age': 12, 'child_grade': '7th',
            'learning_needs': 'Reading difficulties', 'session_type': 'online',
            'start_time': datetime.now() + timedelta(days=3),
            'end_time': datetime.now() + timedelta(days=3, hours=1, minutes=30),
            'subject': 'Reading', 'goals': 'Improve reading comprehension',
            'hourly_rate': lsas[2].hourly_rate, 'total_hours': Decimal('1.5'),
            'status': 'pending', 'payment_status': 'pending'
        },
    ]

    for data in bookings_data:
        # Calculate total amount (quantize to 2 decimal places for DecimalField)
        data['total_amount'] = (data['hourly_rate'] * data['total_hours']).quantize(Decimal('0.01'))
        data['currency'] = 'USD'

        # Check if similar booking already exists
        existing = Booking_Request.objects.filter(
            parent=data['parent'],
            lsa=data['lsa'],
            start_time=data['start_time']
        ).first()

        if existing:
            print(f"Found existing booking: {existing.id}")
            continue

        booking = Booking_Request.objects.create(**data)
        print(f"Created booking: {booking.id} - {booking.parent.full_name} with {booking.lsa.full_name}")


def main():
    """Main function to create all sample data."""
    print("🌱 Creating sample data for LSA Booking System\n")

    try:
        # Create parents
        print("👨‍👩‍👧‍👦 Creating parents...")
        parents = create_sample_parents()
        print(f"✅ Created {len(parents)} parents\n")

        # Create LSAs
        print("🎓 Creating LSAs...")
        lsas = create_sample_lsas()
        print(f"✅ Created {len(lsas)} LSAs\n")

        # Create bookings
        print("📅 Creating bookings...")
        create_sample_bookings(parents, lsas)
        print("✅ Created sample bookings\n")

        print("🎉 Sample data creation completed!")
        print("\n📊 Summary:")
        print(f"- Parents: {Parent.objects.count()}")
        print(f"- LSAs: {LSA_Profile.objects.count()}")
        print(f"- Bookings: {Booking_Request.objects.count()}")

    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()