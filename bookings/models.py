"""
Database models for LSA Booking System.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)


class Parent(models.Model):
    """
    Parent/Guardian model representing parents seeking LSA services for their children.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, db_index=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'parents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['city', 'state']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        """Return the full name of the parent."""
        return f"{self.first_name} {self.last_name}"


class LSA_Profile(models.Model):
    """
    Learning Support Assistant profile model.
    Represents LSAs who provide support services to children with learning difficulties.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    QUALIFICATION_CHOICES = [
        ('high_school', 'High School Diploma'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('phd', 'PhD'),
        ('certification', 'Professional Certification'),
    ]

    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level (0-2 years)'),
        ('intermediate', 'Intermediate (2-5 years)'),
        ('senior', 'Senior (5-10 years)'),
        ('expert', 'Expert (10+ years)'),
    ]

    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, db_index=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    # Professional details
    qualification = models.CharField(max_length=20, choices=QUALIFICATION_CHOICES, db_index=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, db_index=True)
    years_of_experience = models.IntegerField(default=0)
    specialization = models.CharField(max_length=200, help_text="Area of specialization (e.g., ADHD, Autism, Dyslexia)")

    # Location details
    address = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    is_willing_to_relocate = models.BooleanField(default=False)

    # Skills and expertise (stored as comma-separated values for text-based search)
    skills = models.TextField(help_text="Comma-separated list of skills (e.g., 'ADHD,Autism,Sign Language')")
    certifications = models.TextField(blank=True, help_text="Comma-separated list of certifications")
    bio = models.TextField(blank=True)

    # Availability and pricing
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Hourly rate in USD")
    is_available = models.BooleanField(default=True, db_index=True)
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)
    available_days = models.CharField(max_length=50, default='Mon,Tue,Wed,Thu,Fri',
                                      help_text="Comma-separated days of availability")

    # Background check and verification
    background_check_completed = models.BooleanField(default=False)
    background_check_date = models.DateField(null=True, blank=True)
    verified = models.BooleanField(default=False, db_index=True)

    # Profile status
    profile_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Approval'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('inactive', 'Inactive'),
        ],
        default='pending',
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lsa_profiles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_available']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['experience_level', 'qualification']),
            models.Index(fields=['profile_status', 'verified']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.specialization}"

    @property
    def full_name(self):
        """Return the full name of the LSA."""
        return f"{self.first_name} {self.last_name}"

    @property
    def skills_list(self):
        """Return skills as a list."""
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

    ACTIVE_BOOKING_STATUSES = ['pending', 'confirmed', 'in_progress']

    def get_overlapping_bookings(self, start_time, end_time, exclude_id=None):
        """
        Check for existing bookings that overlap with the given time range.
        This prevents double-booking.

        Args:
            start_time: Start of the requested time range
            end_time: End of the requested time range
            exclude_id: Optional booking ID to exclude (used when checking the booking itself)
        """
        bookings = self.booking_requests.filter(
            status__in=self.ACTIVE_BOOKING_STATUSES,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if exclude_id is not None:
            bookings = bookings.exclude(id=exclude_id)
        return bookings

    def is_available_for_booking(self, start_time, end_time, exclude_id=None):
        """
        Check if the LSA is available for the given time range.
        Considers existing active bookings and availability status.
        """
        if not self.is_available or self.profile_status != 'active':
            return False

        overlapping = self.get_overlapping_bookings(start_time, end_time, exclude_id=exclude_id)
        return overlapping.count() == 0


class Booking_Request(models.Model):
    """
    Booking request model connecting Parents with LSAs.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('payment_pending', 'Payment Pending'),
        ('payment_failed', 'Payment Failed'),
    ]

    SESSION_TYPE_CHOICES = [
        ('online', 'Online/Virtual'),
        ('in_person', 'In-Person'),
        ('hybrid', 'Hybrid'),
    ]

    # Core relationships
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='booking_requests')
    lsa = models.ForeignKey(LSA_Profile, on_delete=models.CASCADE, related_name='booking_requests')

    # Child information
    child_name = models.CharField(max_length=100)
    child_age = models.IntegerField()
    child_grade = models.CharField(max_length=50, blank=True)
    learning_needs = models.TextField(help_text="Description of child's learning needs")

    # Booking details
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='online')
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    location = models.CharField(max_length=255, blank=True, help_text="Location for in-person sessions")

    # Session details
    subject = models.CharField(max_length=200, help_text="Subject or topic for the session")
    goals = models.TextField(help_text="Learning goals for this session")
    notes = models.TextField(blank=True, help_text="Additional notes or requirements")

    # Payment details
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Payment status
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Payment Pending'),
            ('completed', 'Payment Completed'),
            ('failed', 'Payment Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    # Booking status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'booking_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['parent', 'status']),
            models.Index(fields=['lsa', 'status']),
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['status', 'payment_status']),
        ]

    def __str__(self):
        return f"Booking #{self.id} - {self.parent.full_name} with {self.lsa.full_name}"

    def clean(self):
        """Validate booking data to prevent double-booking and ensure data integrity."""
        # Validate end_time is after start_time
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

        # Check for overlapping bookings (Poka-Yoke: Prevent double-booking)
        if self.lsa and self.status in self.lsa.ACTIVE_BOOKING_STATUSES:
            overlapping = self.lsa.get_overlapping_bookings(
                self.start_time, self.end_time, exclude_id=self.id
            )

            if overlapping.exists():
                raise ValidationError(
                    f"The LSA {self.lsa.full_name} already has an active booking during this time period. "
                    "Please select a different time slot."
                )

        # Validate total amount calculation (skipped when amount is auto-calculated)
        if self.total_amount is not None and self.hourly_rate and self.total_hours:
            calculated_amount = self.hourly_rate * self.total_hours
            if abs(calculated_amount - self.total_amount) > 0.01:
                raise ValidationError(
                    f"Total amount mismatch. Expected: ${calculated_amount}, Provided: ${self.total_amount}"
                )

    def save(self, *args, **kwargs):
        """Override save to perform validation and automatic calculations."""
        # Auto-calculate total amount if not provided (before validation)
        if not self.total_amount and self.hourly_rate and self.total_hours:
            self.total_amount = (self.hourly_rate * self.total_hours).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

        self.full_clean()
        super().save(*args, **kwargs)

    def confirm_booking(self):
        """Confirm the booking if payment is completed and LSA is available."""
        if self.payment_status != 'completed':
            raise ValueError("Cannot confirm booking: Payment not completed")

        if not self.lsa.is_available_for_booking(self.start_time, self.end_time, exclude_id=self.id):
            raise ValueError("Cannot confirm booking: LSA not available for this time slot")

        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()

    def cancel_booking(self, reason=''):
        """Cancel the booking."""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.notes = f"Cancelled. Reason: {reason}"
        self.save()
