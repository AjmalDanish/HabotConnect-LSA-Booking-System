"""
Payment Webhook Handler for Booking System.
Processes payment success/failure events and updates booking status automatically.
"""
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from .models import Booking_Request

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook(request):
    """
    Handle payment webhook notifications from external payment gateway.
    Automatically transitions booking states based on payment status.

    Expected webhook payload format:
    {
        "event": "payment.success" | "payment.failed" | "payment.refunded",
        "payment_id": "pay_xxx",
        "booking_id": 123,
        "amount": 50.00,
        "currency": "USD",
        "timestamp": "2024-08-11T10:30:00Z",
        "metadata": {}
    }
    """
    try:
        # Parse webhook payload
        payload = json.loads(request.body)
        logger.info(f"Received payment webhook: {payload.get('event')}")

        event_type = payload.get('event')
        payment_id = payload.get('payment_id')
        booking_id = payload.get('booking_id')
        amount = payload.get('amount')

        # Validate required fields
        if not all([event_type, payment_id, booking_id]):
            return HttpResponseBadRequest('Missing required fields')

        # Get the booking
        try:
            booking = Booking_Request.objects.get(id=booking_id)
        except Booking_Request.DoesNotExist:
            logger.error(f"Booking {booking_id} not found for payment webhook")
            return JsonResponse({'error': 'Booking not found'}, status=404)

        # Process different webhook events
        if event_type == 'payment.success':
            return handle_payment_success(booking, payment_id, amount, payload)
        elif event_type == 'payment.failed':
            return handle_payment_failure(booking, payment_id, payload)
        elif event_type == 'payment.refunded':
            return handle_payment_refund(booking, payment_id, amount, payload)
        else:
            logger.warning(f"Unknown webhook event type: {event_type}")
            return JsonResponse({'error': 'Unknown event type'}, status=400)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return HttpResponseBadRequest('Invalid JSON')
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({'error': 'Webhook processing failed'}, status=500)


def handle_payment_success(booking, payment_id, amount, payload):
    """Handle successful payment webhook event."""
    try:
        # Update booking payment details
        booking.payment_status = 'completed'
        booking.payment_id = payment_id
        booking.payment_date = timezone.now()
        booking.status = 'payment_pending'  # Waiting for booking confirmation
        booking.save()

        logger.info(f"Booking {booking.id} payment completed with payment_id {payment_id}")

        # Attempt to confirm the booking automatically
        try:
            booking.confirm_booking()
            logger.info(f"Booking {booking.id} automatically confirmed after payment")
        except Exception as e:
            logger.warning(f"Could not auto-confirm booking {booking.id}: {str(e)}")
            # Keep as payment_pending if auto-confirmation fails

        return JsonResponse({
            'success': True,
            'message': 'Payment processed successfully',
            'booking_id': booking.id,
            'booking_status': booking.status
        })

    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")
        return JsonResponse({'error': 'Failed to process payment success'}, status=500)


def handle_payment_failure(booking, payment_id, payload):
    """Handle payment failure webhook event."""
    try:
        # Update booking with payment failure details
        booking.payment_status = 'failed'
        booking.payment_id = payment_id
        booking.status = 'payment_failed'
        booking.save()

        failure_reason = payload.get('failure_reason', 'Unknown error')
        logger.warning(f"Booking {booking.id} payment failed: {failure_reason}")

        return JsonResponse({
            'success': True,
            'message': 'Payment failure processed',
            'booking_id': booking.id,
            'booking_status': booking.status,
            'failure_reason': failure_reason
        })

    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")
        return JsonResponse({'error': 'Failed to process payment failure'}, status=500)


def handle_payment_refund(booking, payment_id, amount, payload):
    """Handle payment refund webhook event."""
    try:
        # Update booking with refund details
        booking.payment_status = 'refunded'

        # If booking was confirmed, cancel it
        if booking.status in ['confirmed', 'in_progress']:
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()

        booking.save()

        logger.info(f"Booking {booking.id} payment refunded, amount: ${amount}")

        return JsonResponse({
            'success': True,
            'message': 'Refund processed successfully',
            'booking_id': booking.id,
            'refund_amount': amount
        })

    except Exception as e:
        logger.error(f"Error handling payment refund: {str(e)}")
        return JsonResponse({'error': 'Failed to process refund'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_webhook(request):
    """
    Test endpoint for simulating payment webhooks.
    Useful for testing webhook handling without actual payment gateway.
    """
    try:
        payload = json.loads(request.body)

        # Simulate different webhook scenarios
        scenario = payload.get('scenario', 'success')

        if scenario == 'success':
            test_payload = {
                'event': 'payment.success',
                'payment_id': 'pay_test_12345',
                'booking_id': payload.get('booking_id', 1),
                'amount': 50.00,
                'currency': 'USD',
                'timestamp': timezone.now().isoformat(),
                'metadata': {}
            }
        elif scenario == 'failure':
            test_payload = {
                'event': 'payment.failed',
                'payment_id': 'pay_test_failed',
                'booking_id': payload.get('booking_id', 1),
                'amount': 50.00,
                'currency': 'USD',
                'timestamp': timezone.now().isoformat(),
                'failure_reason': 'Insufficient funds',
                'metadata': {}
            }
        elif scenario == 'refund':
            test_payload = {
                'event': 'payment.refunded',
                'payment_id': 'pay_test_refund',
                'booking_id': payload.get('booking_id', 1),
                'amount': 50.00,
                'currency': 'USD',
                'timestamp': timezone.now().isoformat(),
                'metadata': {}
            }
        else:
            return HttpResponseBadRequest('Unknown test scenario')

        # Process the test webhook
        return payment_webhook(request.__class__(content=json.dumps(test_payload).encode()))

    except Exception as e:
        logger.error(f"Error in test webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
