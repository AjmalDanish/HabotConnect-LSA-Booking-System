"""
Comprehensive Unit Tests for LSA Booking System.
Tests cover success cases, edge cases, and failure scenarios.
"""
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from .models import Parent, LSA_Profile, Booking_Request


class ParentModelTest(TestCase):
    """Test cases for Parent model."""

    def setUp(self):
        """Set up test data for Parent model."""
        self.parent_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'gender': 'M',
            'address': '123 Main St',
            'city': 'New York',
            'state': 'NY',
            'postal_code': '10001',
            'country': 'USA',
            'date_of_birth': '1980-01-01'
        }

    def test_create_parent_success(self):
        """Test successful parent creation."""
        parent = Parent.objects.create(**self.parent_data)
        self.assertEqual(parent.email, 'john.doe@example.com')
        self.assertEqual(parent.full_name, 'John Doe')
        self.assertTrue(parent.is_active)

    def test_parent_email_unique(self):
        """Test that parent emails are unique."""
        Parent.objects.create(**self.parent_data)
        with self.assertRaises(Exception):  # Database integrity error
            Parent.objects.create(**self.parent_data)

    def test_parent_str_method(self):
        """Test Parent string representation."""
        parent = Parent.objects.create(**self.parent_data)
        expected = "John Doe (john.doe@example.com)"
        self.assertEqual(str(parent), expected)


class LSA_ProfileModelTest(TestCase):
    """Test cases for LSA_Profile model."""

    def setUp(self):
        """Set up test data for LSA model."""
        self.lsa_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '+9876543210',
            'gender': 'F',
            'qualification': 'bachelor',
            'experience_level': 'intermediate',
            'years_of_experience': 3,
            'specialization': 'ADHD',
            'address': '456 Oak Ave',
            'city': 'Los Angeles',
            'state': 'CA',
            'postal_code': '90001',
            'country': 'USA',
            'skills': 'ADHD,Autism,Sign Language',
            'hourly_rate': Decimal('45.00'),
            'is_available': True,
            'verified': True,
            'profile_status': 'active'
        }

    def test_create_lsa_success(self):
        """Test successful LSA profile creation."""
        lsa = LSA_Profile.objects.create(**self.lsa_data)
        self.assertEqual(lsa.email, 'jane.smith@example.com')
        self.assertEqual(lsa.specialization, 'ADHD')
        self.assertTrue(lsa.is_available)

    def test_lsa_skills_list_property(self):
        """Test LSA skills list property."""
        lsa = LSA_Profile.objects.create(**self.lsa_data)
        skills_list = lsa.skills_list
        self.assertEqual(len(skills_list), 3)
        self.assertIn('ADHD', skills_list)
        self.assertIn('Autism', skills_list)


class Booking_RequestModelTest(TestCase):
    """Test cases for Booking_Request model."""

    def setUp(self):
        """Set up test data for booking model."""
        self.parent = Parent.objects.create(
            first_name='John', last_name='Doe', email='john@example.com',
            phone='+1234567890', gender='M', address='123 St',
            city='NYC', state='NY', postal_code='10001',
            date_of_birth='1980-01-01'
        )

        self.lsa = LSA_Profile.objects.create(
            first_name='Jane', last_name='Smith', email='jane@example.com',
            phone='+9876543210', gender='F', qualification='bachelor',
            experience_level='intermediate', years_of_experience=3,
            specialization='ADHD', address='456 Ave', city='LA',
            state='CA', postal_code='90001', hourly_rate=Decimal('45.00'),
            is_available=True, verified=True, profile_status='active'
        )

        self.booking_data = {
            'parent': self.parent,
            'lsa': self.lsa,
            'child_name': 'Tom',
            'child_age': 10,
            'child_grade': '5th',
            'learning_needs': 'ADHD support',
            'session_type': 'online',
            'start_time': timezone.now() + timedelta(days=1),
            'end_time': timezone.now() + timedelta(days=1, hours=2),
            'subject': 'Math',
            'goals': 'Improve math skills',
            'hourly_rate': Decimal('45.00'),
            'total_hours': Decimal('2.00'),
            'total_amount': Decimal('90.00'),
            'currency': 'USD'
        }

    def test_create_booking_success(self):
        """Test successful booking creation."""
        booking = Booking_Request.objects.create(**self.booking_data)
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.child_name, 'Tom')
        self.assertEqual(booking.total_amount, Decimal('90.00'))

    def test_booking_validation_end_time_after_start(self):
        """Test that end_time must be after start_time."""
        self.booking_data['end_time'] = timezone.now() + timedelta(days=1, hours=-1)
        with self.assertRaises(ValidationError):
            booking = Booking_Request(**self.booking_data)
            booking.full_clean()

    def test_booking_double_booking_prevention(self):
        """Test Poka-Yoke: Prevent double-booking of LSA."""
        # Create first booking
        Booking_Request.objects.create(**self.booking_data)

        # Try to create overlapping booking
        overlapping_data = self.booking_data.copy()
        overlapping_data['start_time'] = timezone.now() + timedelta(days=1, hours=1)
        overlapping_data['end_time'] = timezone.now() + timedelta(days=1, hours=3)

        with self.assertRaises(ValidationError):
            overlapping_booking = Booking_Request(**overlapping_data)
            overlapping_booking.full_clean()

    def test_booking_amount_calculation(self):
        """Test automatic total amount calculation."""
        booking_data = self.booking_data.copy()
        booking_data['total_amount'] = None  # Let it calculate automatically

        booking = Booking_Request(**booking_data)
        booking.save()  # This should auto-calculate

        self.assertEqual(booking.total_amount, Decimal('90.00'))

    def test_booking_confirm_method(self):
        """Test booking confirmation method."""
        booking = Booking_Request.objects.create(**self.booking_data)
        booking.payment_status = 'completed'
        booking.confirm_booking()

        self.assertEqual(booking.status, 'confirmed')
        self.assertIsNotNone(booking.confirmed_at)

    def test_booking_cancel_method(self):
        """Test booking cancellation method."""
        booking = Booking_Request.objects.create(**self.booking_data)
        booking.cancel_booking('Test cancellation')

        self.assertEqual(booking.status, 'cancelled')
        self.assertIsNotNone(booking.cancelled_at)


class BookingAPITest(APITestCase):
    """Test cases for Booking API endpoints."""

    def setUp(self):
        """Set up test data for API tests."""
        self.client = APIClient()

        # Create test parent
        self.parent = Parent.objects.create(
            first_name='John', last_name='Doe', email='john@example.com',
            phone='+1234567890', gender='M', address='123 St',
            city='NYC', state='NY', postal_code='10001',
            date_of_birth='1980-01-01'
        )

        # Create test LSA
        self.lsa = LSA_Profile.objects.create(
            first_name='Jane', last_name='Smith', email='jane@example.com',
            phone='+9876543210', gender='F', qualification='bachelor',
            experience_level='intermediate', years_of_experience=3,
            specialization='ADHD', address='456 Ave', city='LA',
            state='CA', postal_code='90001', hourly_rate=Decimal('45.00'),
            is_available=True, verified=True, profile_status='active'
        )

    def test_create_booking_api_success(self):
        """Test successful booking creation via API."""
        start_time = timezone.now() + timedelta(days=1)
        booking_data = {
            'parent': self.parent.id,
            'lsa': self.lsa.id,
            'child_name': 'Tom',
            'child_age': 10,
            'learning_needs': 'ADHD support',
            'session_type': 'online',
            'start_time': start_time.isoformat(),
            'end_time': (start_time + timedelta(hours=2)).isoformat(),
            'subject': 'Math',
            'goals': 'Improve math skills',
            'hourly_rate': '45.00',
            'total_hours': '2.00',
            'total_amount': '90.00',
            'currency': 'USD'
        }

        response = self.client.post('/api/v1/bookings/', booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking_Request.objects.count(), 1)

    def test_create_booking_api_double_booking_prevention(self):
        """Test API prevents double-booking."""
        start_time = timezone.now() + timedelta(days=1)

        # Create first booking
        first_booking_data = {
            'parent': self.parent.id,
            'lsa': self.lsa.id,
            'child_name': 'Tom',
            'child_age': 10,
            'learning_needs': 'ADHD support',
            'session_type': 'online',
            'start_time': start_time.isoformat(),
            'end_time': (start_time + timedelta(hours=2)).isoformat(),
            'subject': 'Math',
            'goals': 'Improve math skills',
            'hourly_rate': '45.00',
            'total_hours': '2.00',
            'total_amount': '90.00',
            'currency': 'USD'
        }

        response1 = self.client.post('/api/v1/bookings/', first_booking_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Try to create overlapping booking
        overlapping_data = first_booking_data.copy()
        overlapping_data['start_time'] = (start_time + timedelta(hours=1)).isoformat()
        overlapping_data['end_time'] = (start_time + timedelta(hours=3)).isoformat()

        response2 = self.client.post('/api/v1/bookings/', overlapping_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lsa_search_api_success(self):
        """Test LSA search endpoint."""
        response = self.client.get('/api/v1/lsas/search/?skills=ADHD&city=LA')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)


class PaymentServiceTest(TestCase):
    """Test cases for Payment Service."""

    def test_create_payment_intent(self):
        """Test payment intent creation."""
        from .payment_service import payment_gateway

        payment_intent = payment_gateway.create_payment_intent(
            amount=Decimal('50.00'),
            currency='USD',
            description='Test payment'
        )

        self.assertTrue(payment_intent['success'])
        self.assertIn('payment_id', payment_intent)
        self.assertEqual(payment_intent['amount'], Decimal('50.00'))

    def test_process_payment_success(self):
        """Test successful payment processing."""
        from .payment_service import payment_gateway

        # Create payment intent
        payment_intent = payment_gateway.create_payment_intent(
            amount=Decimal('50.00'),
            currency='USD'
        )

        # Process payment
        payment_result = payment_gateway.process_payment(
            payment_id=payment_intent['payment_id']
        )

        self.assertIn('success', payment_result)
        self.assertIn('status', payment_result)


class LSA_AvailabilityTest(TestCase):
    """Test cases for LSA availability system."""

    def setUp(self):
        """Set up test data."""
        self.parent = Parent.objects.create(
            first_name='John', last_name='Doe', email='john@example.com',
            phone='+1234567890', gender='M', address='123 St',
            city='NYC', state='NY', postal_code='10001',
            date_of_birth='1980-01-01'
        )

        self.lsa = LSA_Profile.objects.create(
            first_name='Jane', last_name='Smith', email='jane@example.com',
            phone='+9876543210', gender='F', qualification='bachelor',
            experience_level='intermediate', years_of_experience=3,
            specialization='ADHD', address='456 Ave', city='LA',
            state='CA', postal_code='90001', hourly_rate=Decimal('45.00'),
            is_available=True, verified=True, profile_status='active'
        )

    def test_lsa_available_for_booking(self):
        """Test LSA availability check."""
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)

        is_available = self.lsa.is_available_for_booking(start_time, end_time)
        self.assertTrue(is_available)

    def test_lsa_not_available_when_booked(self):
        """Test LSA unavailable when already booked."""
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)

        # Create first booking
        Booking_Request.objects.create(
            parent=self.parent, lsa=self.lsa,
            child_name='Tom', child_age=10,
            learning_needs='ADHD', session_type='online',
            start_time=start_time, end_time=end_time,
            subject='Math', goals='Help with math',
            hourly_rate=Decimal('45.00'), total_hours=Decimal('2.00'),
            total_amount=Decimal('90.00'),
            status='confirmed'
        )

        # Check availability for same time
        is_available = self.lsa.is_available_for_booking(start_time, end_time)
        self.assertFalse(is_available)
