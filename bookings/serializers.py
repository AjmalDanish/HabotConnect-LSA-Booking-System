"""
Serializers for LSA Booking System API.
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from .models import Parent, LSA_Profile, Booking_Request
import logging

logger = logging.getLogger(__name__)


class ParentSerializer(serializers.ModelSerializer):
    """Serializer for Parent model."""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Parent
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'gender', 'address', 'city', 'state', 'postal_code', 'country',
            'date_of_birth', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LSA_ProfileSerializer(serializers.ModelSerializer):
    """Serializer for LSA_Profile model."""
    full_name = serializers.ReadOnlyField()
    skills_list = serializers.ReadOnlyField()

    class Meta:
        model = LSA_Profile
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'gender',
            'qualification', 'experience_level', 'years_of_experience', 'specialization',
            'address', 'city', 'state', 'postal_code', 'country', 'is_willing_to_relocate',
            'skills', 'skills_list', 'certifications', 'bio',
            'hourly_rate', 'is_available', 'available_from', 'available_to', 'available_days',
            'background_check_completed', 'background_check_date', 'verified', 'profile_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LSA_SearchSerializer(serializers.Serializer):
    """Serializer for LSA search parameters."""
    skills = serializers.CharField(required=False, help_text="Comma-separated skills to filter")
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    experience_level = serializers.CharField(required=False)
    min_hourly_rate = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    max_hourly_rate = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    is_available = serializers.BooleanField(required=False)
    specialization = serializers.CharField(required=False)


class Booking_RequestSerializer(serializers.ModelSerializer):
    """Serializer for Booking_Request model."""
    parent_details = ParentSerializer(source='parent', read_only=True)
    lsa_details = LSA_ProfileSerializer(source='lsa', read_only=True)

    class Meta:
        model = Booking_Request
        fields = [
            'id', 'parent', 'parent_details', 'lsa', 'lsa_details',
            'child_name', 'child_age', 'child_grade', 'learning_needs',
            'session_type', 'start_time', 'end_time', 'location',
            'subject', 'goals', 'notes',
            'hourly_rate', 'total_hours', 'total_amount', 'currency',
            'payment_status', 'payment_id', 'payment_date',
            'status', 'created_at', 'updated_at', 'confirmed_at', 'completed_at', 'cancelled_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'confirmed_at', 'completed_at', 'cancelled_at']


class Booking_CreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating booking requests.
    Includes validation to prevent double-booking and ensure data integrity.
    """
    class Meta:
        model = Booking_Request
        fields = [
            'parent', 'lsa', 'child_name', 'child_age', 'child_grade', 'learning_needs',
            'session_type', 'start_time', 'end_time', 'location',
            'subject', 'goals', 'notes',
            'hourly_rate', 'total_hours', 'total_amount', 'currency'
        ]

    def validate(self, data):
        """
        Validate booking data with Poka-Yoke (mistake-proofing) design.
        """
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        lsa = data.get('lsa')

        # Validate time range
        if end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })

        # Check LSA availability
        if lsa:
            if not lsa.is_available:
                raise serializers.ValidationError({
                    'lsa': 'This LSA is currently not available for bookings.'
                })

            if lsa.profile_status != 'active':
                raise serializers.ValidationError({
                    'lsa': 'This LSA profile is not active.'
                })

            # Check for overlapping bookings (Poka-Yoke: Prevent double-booking)
            overlapping = Booking_Request.objects.filter(
                lsa=lsa,
                status__in=LSA_Profile.ACTIVE_BOOKING_STATUSES,
                start_time__lt=end_time,
                end_time__gt=start_time
            )

            if overlapping.exists():
                raise serializers.ValidationError({
                    'start_time': 'The LSA already has an active booking during this '
                                  'time period. Please select a different time slot.',
                    'end_time': 'The LSA already has an active booking during this '
                                'time period. Please select a different time slot.'
                })

        # Validate total amount
        hourly_rate = data.get('hourly_rate')
        total_hours = data.get('total_hours')
        total_amount = data.get('total_amount')

        if all([hourly_rate, total_hours, total_amount]):
            calculated_amount = hourly_rate * total_hours
            if abs(calculated_amount - total_amount) > 0.01:
                raise serializers.ValidationError({
                    'total_amount': f'Total amount mismatch. Expected: ${calculated_amount}, Provided: ${total_amount}'
                })

        return data

    def create(self, validated_data):
        """Create booking with automatic total amount calculation."""
        hourly_rate = validated_data.get('hourly_rate')
        total_hours = validated_data.get('total_hours')

        if not validated_data.get('total_amount') and all([hourly_rate, total_hours]):
            validated_data['total_amount'] = (hourly_rate * total_hours).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

        try:
            booking = Booking_Request.objects.create(**validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        logger.info(
            f"Created booking request #{booking.id} for parent {booking.parent.email} "
            f"with LSA {booking.lsa.email}"
        )
        return booking


class Booking_UpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking requests."""

    class Meta:
        model = Booking_Request
        fields = [
            'child_name', 'child_age', 'child_grade', 'learning_needs',
            'session_type', 'start_time', 'end_time', 'location',
            'subject', 'goals', 'notes', 'status', 'payment_status'
        ]

    def validate(self, data):
        """Validate booking updates."""
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # Validate time range if both are provided
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })

        return data
