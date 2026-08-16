"""
URL configuration for Bookings API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookingViewSet, LSA_SearchView, LSA_AvailabilityView, HealthCheckView
)
from . import webhooks

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    # Health check endpoint
    path('health/', HealthCheckView.as_view(), name='health-check'),

    # Booking endpoints
    path('', include(router.urls)),

    # LSA search endpoint
    path('lsas/search/', LSA_SearchView.as_view(), name='lsa-search'),

    # LSA availability check endpoint
    path('lsas/check-availability/', LSA_AvailabilityView.as_view(), name='lsa-availability'),

    # Payment webhook endpoint
    path('payments/webhook/', webhooks.payment_webhook, name='payment-webhook'),

    # Test webhook endpoint
    path('payments/webhook/test/', webhooks.test_webhook, name='test-webhook'),
]
