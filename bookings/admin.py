"""
Admin configuration for LSA Booking System.
"""
from django.contrib import admin
from .models import Parent, LSA_Profile, Booking_Request


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    """Admin interface for Parent model."""
    list_display = ['full_name', 'email', 'phone', 'city', 'state', 'is_active', 'created_at']
    list_filter = ['gender', 'city', 'state', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'gender', 'date_of_birth')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LSA_Profile)
class LSA_ProfileAdmin(admin.ModelAdmin):
    """Admin interface for LSA_Profile model."""
    list_display = [
        'full_name', 'email', 'specialization', 'experience_level',
        'city', 'is_available', 'profile_status', 'created_at'
    ]
    list_filter = ['gender', 'qualification', 'experience_level', 'is_available', 'profile_status', 'verified']
    search_fields = ['first_name', 'last_name', 'email', 'specialization', 'skills']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'gender')
        }),
        ('Professional Details', {
            'fields': ('qualification', 'experience_level', 'years_of_experience', 'specialization', 'bio')
        }),
        ('Skills & Certifications', {
            'fields': ('skills', 'certifications')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country', 'is_willing_to_relocate')
        }),
        ('Availability & Pricing', {
            'fields': ('is_available', 'available_from', 'available_to', 'available_days', 'hourly_rate')
        }),
        ('Verification', {
            'fields': ('background_check_completed', 'background_check_date', 'verified')
        }),
        ('Status', {
            'fields': ('profile_status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Booking_Request)
class Booking_RequestAdmin(admin.ModelAdmin):
    """Admin interface for Booking_Request model."""
    list_display = [
        'id', 'parent', 'lsa', 'start_time', 'end_time', 'status',
        'payment_status', 'total_amount', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'session_type', 'created_at']
    search_fields = ['parent__first_name', 'parent__last_name', 'lsa__first_name', 'lsa__last_name', 'child_name']
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'completed_at', 'cancelled_at']
    fieldsets = (
        ('Relationships', {
            'fields': ('parent', 'lsa')
        }),
        ('Child Information', {
            'fields': ('child_name', 'child_age', 'child_grade', 'learning_needs')
        }),
        ('Booking Details', {
            'fields': ('session_type', 'start_time', 'end_time', 'location')
        }),
        ('Session Information', {
            'fields': ('subject', 'goals', 'notes')
        }),
        ('Payment Details', {
            'fields': (
                'hourly_rate', 'total_hours', 'total_amount', 'currency',
                'payment_status', 'payment_id', 'payment_date'
            )
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'completed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
