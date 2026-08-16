"""
Mock Payment Gateway Integration Service.
Simulates external payment gateway operations with proper error handling and logging.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class PaymentGatewayException(Exception):
    """Custom exception for payment gateway errors."""
    pass


class MockPaymentGateway:
    """
    Mock payment gateway service that simulates real payment processing.
    Includes comprehensive error handling, logging, and webhook functionality.
    """

    def __init__(self, api_key: str = None, mock_mode: bool = True):
        """
        Initialize the payment gateway.

        Args:
            api_key: API key for authentication (not used in mock mode)
            mock_mode: If True, simulates payment processing without real API calls
        """
        self.api_key = api_key
        self.mock_mode = mock_mode
        self.base_url = "https://api.mock-payment-gateway.com/v1" if not mock_mode else None

        # Mock payment records for testing
        self.mock_payments = {}

    def create_payment_intent(
        self,
        amount: float,
        currency: str = "USD",
        description: str = "",
        metadata: Dict = None
    ) -> Dict:
        """
        Create a payment intent for processing.

        Args:
            amount: Payment amount in decimal (e.g., 50.00)
            currency: Currency code (default: USD)
            description: Payment description
            metadata: Additional metadata

        Returns:
            Dict containing payment intent details

        Raises:
            PaymentGatewayException: If payment creation fails
        """
        try:
            payment_id = f"pay_{uuid.uuid4().hex[:24]}"

            payment_data = {
                "id": payment_id,
                "amount": amount,
                "currency": currency,
                "description": description,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }

            if self.mock_mode:
                # Store mock payment record
                self.mock_payments[payment_id] = payment_data
                logger.info(f"Mock payment intent created: {payment_id} for amount ${amount}")
            else:
                # In production, would make real API call here
                pass

            return {
                "success": True,
                "payment_id": payment_id,
                "amount": amount,
                "currency": currency,
                "status": "pending",
                "client_secret": f"pi_{payment_id}_secret_{uuid.uuid4().hex[:16]}"
            }

        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            raise PaymentGatewayException(f"Failed to create payment intent: {str(e)}")

    def process_payment(
        self,
        payment_id: str,
        payment_method: str = "card",
        card_details: Dict = None
    ) -> Dict:
        """
        Process a payment using the given payment method.

        Args:
            payment_id: Payment intent ID
            payment_method: Payment method type (card, bank_transfer, etc.)
            card_details: Card details (card number, expiry, cvv)

        Returns:
            Dict containing payment processing result

        Raises:
            PaymentGatewayException: If payment processing fails
        """
        try:
            if payment_id not in self.mock_payments and self.mock_mode:
                raise PaymentGatewayException(f"Payment intent {payment_id} not found")

            # Simulate payment processing with random success/failure
            import random
            success = random.random() > 0.1  # 90% success rate for testing

            if success:
                payment_status = "succeeded"
                self.mock_payments[payment_id]["status"] = "succeeded"
                self.mock_payments[payment_id]["processed_at"] = datetime.utcnow().isoformat()
                logger.info(f"Payment {payment_id} processed successfully")
            else:
                payment_status = "failed"
                self.mock_payments[payment_id]["status"] = "failed"
                self.mock_payments[payment_id]["failure_reason"] = "Insufficient funds"
                logger.warning(f"Payment {payment_id} failed: Insufficient funds")

            return {
                "success": success,
                "payment_id": payment_id,
                "status": payment_status,
                "amount": self.mock_payments.get(payment_id, {}).get("amount", 0),
                "currency": self.mock_payments.get(payment_id, {}).get("currency", "USD"),
                "processed_at": datetime.utcnow().isoformat() if success else None,
                "failure_reason": None if success else "Insufficient funds"
            }

        except PaymentGatewayException:
            raise
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            raise PaymentGatewayException(f"Payment processing failed: {str(e)}")

    def get_payment_status(self, payment_id: str) -> Dict:
        """
        Get the current status of a payment.

        Args:
            payment_id: Payment intent ID

        Returns:
            Dict containing payment status
        """
        try:
            if payment_id not in self.mock_payments and self.mock_mode:
                raise PaymentGatewayException(f"Payment {payment_id} not found")

            payment_data = self.mock_payments.get(payment_id, {})

            return {
                "payment_id": payment_id,
                "status": payment_data.get("status", "unknown"),
                "amount": payment_data.get("amount", 0),
                "currency": payment_data.get("currency", "USD"),
                "created_at": payment_data.get("created_at"),
                "processed_at": payment_data.get("processed_at"),
                "failure_reason": payment_data.get("failure_reason"),
                "metadata": payment_data.get("metadata", {})
            }

        except PaymentGatewayException:
            raise
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            raise PaymentGatewayException(f"Failed to get payment status: {str(e)}")

    def refund_payment(self, payment_id: str, amount: float = None) -> Dict:
        """
        Refund a payment (full or partial).

        Args:
            payment_id: Payment intent ID
            amount: Refund amount (None for full refund)

        Returns:
            Dict containing refund details
        """
        try:
            if payment_id not in self.mock_payments and self.mock_mode:
                raise PaymentGatewayException(f"Payment {payment_id} not found")

            payment_data = self.mock_payments.get(payment_id, {})
            if payment_data.get("status") != "succeeded":
                raise PaymentGatewayException("Only successful payments can be refunded")

            refund_amount = amount if amount else payment_data.get("amount", 0)
            refund_id = f"ref_{uuid.uuid4().hex[:24]}"

            logger.info(f"Refund {refund_id} created for payment {payment_id}, amount: ${refund_amount}")

            return {
                "success": True,
                "refund_id": refund_id,
                "payment_id": payment_id,
                "amount": refund_amount,
                "currency": payment_data.get("currency", "USD"),
                "status": "succeeded",
                "created_at": datetime.utcnow().isoformat()
            }

        except PaymentGatewayException:
            raise
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            raise PaymentGatewayException(f"Refund processing failed: {str(e)}")


# Singleton instance for use across the application
payment_gateway = MockPaymentGateway(mock_mode=True)


def process_booking_payment(
    booking_id: int,
    amount: float,
    currency: str = "USD",
    card_details: Dict = None
) -> Tuple[bool, Dict]:
    """
    Process payment for a booking.

    Args:
        booking_id: Booking ID
        amount: Payment amount
        currency: Currency code
        card_details: Payment card details

    Returns:
        Tuple of (success, response_data)
    """
    try:
        # Create payment intent
        payment_intent = payment_gateway.create_payment_intent(
            amount=amount,
            currency=currency,
            description=f"Payment for booking #{booking_id}",
            metadata={"booking_id": booking_id}
        )

        if not payment_intent["success"]:
            return False, payment_intent

        # Process the payment
        payment_result = payment_gateway.process_payment(
            payment_id=payment_intent["payment_id"],
            card_details=card_details
        )

        return payment_result["success"], payment_result

    except PaymentGatewayException as e:
        logger.error(f"Booking payment processing error: {str(e)}")
        return False, {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in booking payment: {str(e)}")
        return False, {"error": "Unexpected payment processing error"}
