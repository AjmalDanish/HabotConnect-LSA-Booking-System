"""
API Views for LSA Booking System.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone
import logging

from .models import LSA_Profile, Booking_Request
from .serializers import (
    LSA_ProfileSerializer, Booking_RequestSerializer,
    Booking_CreateSerializer, Booking_UpdateSerializer, LSA_SearchSerializer
)

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Health check endpoint for monitoring."""

    def get(self, request):
        """Return health status."""
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'service': 'Habot LSA Booking API',
            'version': '1.0.0'
        })


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing booking requests.
    Provides CRUD operations for booking management.
    """
    queryset = Booking_Request.objects.all()
    serializer_class = Booking_RequestSerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return Booking_CreateSerializer
        elif self.action in ['update', 'partial_update']:
            return Booking_UpdateSerializer
        return Booking_RequestSerializer

    def get_queryset(self):
        """
        Get optimized queryset to avoid N+1 queries.
        Uses select_related and prefetch_related for optimal performance.
        """
        queryset = Booking_Request.objects.select_related(
            'parent', 'lsa'
        ).prefetch_related(
            'parent__booking_requests', 'lsa__booking_requests'
        )

        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by payment status if provided
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        # Filter by parent if provided
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        # Filter by LSA if provided
        lsa_id = self.request.query_params.get('lsa_id')
        if lsa_id:
            queryset = queryset.filter(lsa_id=lsa_id)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new booking request.
        Includes comprehensive validation to prevent double-booking.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            booking = serializer.save()
            logger.info(f"Booking #{booking.id} created successfully")
            return Response(
                Booking_RequestSerializer(booking).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            return Response(
                {'error': 'Failed to create booking', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking (after payment verification)."""
        booking = self.get_object()

        try:
            booking.confirm_booking()
            logger.info(f"Booking #{booking.id} confirmed successfully")
            return Response({
                'message': 'Booking confirmed successfully',
                'booking': Booking_RequestSerializer(booking).data
            })
        except ValueError as e:
            logger.error(f"Error confirming booking #{booking.id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        reason = request.data.get('reason', 'No reason provided')

        try:
            booking.cancel_booking(reason)
            logger.info(f"Booking #{booking.id} cancelled")
            return Response({
                'message': 'Booking cancelled successfully',
                'booking': Booking_RequestSerializer(booking).data
            })
        except Exception as e:
            logger.error(f"Error cancelling booking #{booking.id}: {str(e)}")
            return Response(
                {'error': 'Failed to cancel booking', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LSA_SearchView(APIView):
    """
    API endpoint for searching available LSAs.
    Optimized to prevent N+1 queries using proper Django ORM techniques.
    """

    def get(self, request):
        """
        Search for LSAs based on various filters.
        Returns optimized query results to avoid N+1 problems.
        """
        serializer = LSA_SearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # Start with base queryset - use select_related to avoid N+1
        queryset = LSA_Profile.objects.filter(
            profile_status='active',
            verified=True
        ).select_related()  # Optimize for single-related objects

        # Apply filters if provided
        skills = serializer.validated_data.get('skills')
        if skills:
            # Filter by skills (stored as comma-separated values)
            skill_list = [skill.strip().lower() for skill in skills.split(',')]
            skills_filter = Q()
            for skill in skill_list:
                skills_filter |= Q(skills__icontains=skill)
            queryset = queryset.filter(skills_filter)

        city = serializer.validated_data.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)

        state = serializer.validated_data.get('state')
        if state:
            queryset = queryset.filter(state__icontains=state)

        experience_level = serializer.validated_data.get('experience_level')
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)

        min_hourly_rate = serializer.validated_data.get('min_hourly_rate')
        if min_hourly_rate:
            queryset = queryset.filter(hourly_rate__gte=min_hourly_rate)

        max_hourly_rate = serializer.validated_data.get('max_hourly_rate')
        if max_hourly_rate:
            queryset = queryset.filter(hourly_rate__lte=max_hourly_rate)

        is_available = serializer.validated_data.get('is_available')
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available)

        specialization = serializer.validated_data.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)

        # Use prefetch_related for reverse relationships to avoid N+1
        queryset = queryset.prefetch_related('booking_requests')

        logger.info(f"LSA search performed: {queryset.count()} results found")

        # Serialize and return results
        serializer = LSA_ProfileSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })


class LSA_AvailabilityView(APIView):
    """
    Check availability for a specific LSA during a time period.
    """

    def get(self, request):
        """
        Check if an LSA is available for a given time period.
        """
        lsa_id = request.query_params.get('lsa_id')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')

        if not all([lsa_id, start_time, end_time]):
            return Response({
                'error': 'Missing required parameters: lsa_id, start_time, end_time'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            from datetime import datetime
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

            lsa = LSA_Profile.objects.get(id=lsa_id)
            is_available = lsa.is_available_for_booking(start_time, end_time)

            if not is_available:
                overlapping = lsa.get_overlapping_bookings(start_time, end_time)
                return Response({
                    'available': False,
                    'lsa_id': lsa.id,
                    'lsa_name': lsa.full_name,
                    'reason': 'LSA has existing bookings during this time period',
                    'overlapping_bookings': Booking_RequestSerializer(overlapping, many=True).data
                })

            return Response({
                'available': True,
                'lsa_id': lsa.id,
                'lsa_name': lsa.full_name,
                'message': 'LSA is available for booking during this time period'
            })

        except LSA_Profile.DoesNotExist:
            return Response({
                'error': 'LSA not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({
                'error': f'Invalid datetime format: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return Response({
                'error': 'Failed to check availability',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
