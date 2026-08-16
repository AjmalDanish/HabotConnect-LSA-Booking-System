# API Documentation

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication
Currently, the API does not require authentication for testing purposes. In production, JWT authentication would be implemented.

## Endpoints

### Health Check

#### GET /health/
Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-08-11T10:00:00Z",
  "service": "Habot LSA Booking API",
  "version": "1.0.0"
}
```

---

### Bookings

#### POST /bookings/
Create a new booking request.

**Request Body:**
```json
{
  "parent": 1,
  "lsa": 2,
  "child_name": "Tom",
  "child_age": 10,
  "child_grade": "5th",
  "learning_needs": "ADHD support",
  "session_type": "online",
  "start_time": "2024-08-12T10:00:00Z",
  "end_time": "2024-08-12T12:00:00Z",
  "location": "",
  "subject": "Math",
  "goals": "Improve math skills",
  "notes": "",
  "hourly_rate": "45.00",
  "total_hours": "2.00",
  "total_amount": "90.00",
  "currency": "USD"
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "parent": 1,
  "lsa": 2,
  "child_name": "Tom",
  "status": "pending",
  "payment_status": "pending",
  "total_amount": "90.00",
  "created_at": "2024-08-11T10:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Validation error details",
  "start_time": ["LSA already has a confirmed booking during this time period."]
}
```

#### GET /bookings/
List all bookings with pagination and filtering.

**Query Parameters:**
- `status`: Filter by status (pending, confirmed, completed, etc.)
- `payment_status`: Filter by payment status
- `parent_id`: Filter by parent ID
- `lsa_id`: Filter by LSA ID
- `page`: Page number (default: 1)

**Response:**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/v1/bookings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "parent": 1,
      "lsa": 2,
      "status": "confirmed",
      "payment_status": "completed",
      "start_time": "2024-08-12T10:00:00Z",
      "end_time": "2024-08-12T12:00:00Z"
    }
  ]
}
```

#### POST /bookings/{id}/confirm/
Confirm a booking after successful payment.

**Response (200 OK):**
```json
{
  "message": "Booking confirmed successfully",
  "booking": {
    "id": 1,
    "status": "confirmed",
    "confirmed_at": "2024-08-11T10:30:00Z"
  }
}
```

#### POST /bookings/{id}/cancel/
Cancel a booking.

**Request Body:**
```json
{
  "reason": "Customer request"
}
```

**Response (200 OK):**
```json
{
  "message": "Booking cancelled successfully",
  "booking": {
    "id": 1,
    "status": "cancelled",
    "cancelled_at": "2024-08-11T11:00:00Z"
  }
}
```

---

### LSA Search

#### GET /lsas/search/
Search for available LSAs with various filters.

**Query Parameters:**
- `skills`: Comma-separated skills (e.g., "ADHD,Autism")
- `city`: City name
- `state`: State name
- `experience_level`: entry, intermediate, senior, expert
- `min_hourly_rate`: Minimum hourly rate
- `max_hourly_rate`: Maximum hourly rate
- `specialization`: Specialization keyword
- `is_available`: true/false

**Example:**
```
GET /lsas/search/?skills=ADHD&city=Los+Angeles&min_hourly_rate=30&max_hourly_rate=60
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "full_name": "Jane Smith",
      "email": "jane.smith@example.com",
      "specialization": "ADHD",
      "experience_level": "intermediate",
      "city": "Los Angeles",
      "state": "CA",
      "hourly_rate": "45.00",
      "skills_list": ["ADHD", "Autism", "Sign Language"],
      "is_available": true,
      "verified": true
    }
  ]
}
```

#### GET /lsas/check-availability/
Check if an LSA is available for a specific time period.

**Query Parameters:**
- `lsa_id`: LSA profile ID (required)
- `start_time`: Start time in ISO format (required)
- `end_time`: End time in ISO format (required)

**Example:**
```
GET /lsas/check-availability/?lsa_id=1&start_time=2024-08-12T10:00:00Z&end_time=2024-08-12T12:00:00Z
```

**Response (Available):**
```json
{
  "available": true,
  "lsa_id": 1,
  "lsa_name": "Jane Smith",
  "message": "LSA is available for booking during this time period"
}
```

**Response (Not Available):**
```json
{
  "available": false,
  "lsa_id": 1,
  "lsa_name": "Jane Smith",
  "reason": "LSA has existing bookings during this time period",
  "overlapping_bookings": [
    {
      "id": 5,
      "start_time": "2024-08-12T09:00:00Z",
      "end_time": "2024-08-12T13:00:00Z"
    }
  ]
}
```

---

### Payment Webhooks

#### POST /payments/webhook/
Handle payment gateway notifications.

**Webhook Payload (payment.success):**
```json
{
  "event": "payment.success",
  "payment_id": "pay_12345",
  "booking_id": 1,
  "amount": 90.00,
  "currency": "USD",
  "timestamp": "2024-08-12T10:30:00Z",
  "metadata": {}
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Payment processed successfully",
  "booking_id": 1,
  "booking_status": "confirmed"
}
```

#### POST /payments/webhook/test/
Test webhook endpoint for development.

**Request Body:**
```json
{
  "scenario": "success",
  "booking_id": 1
}
```

**Scenarios:**
- `success`: Simulate successful payment
- `failure`: Simulate payment failure
- `refund`: Simulate payment refund

---

## Error Responses

All endpoints may return error responses in the following format:

**400 Bad Request:**
```json
{
  "error": "Validation error",
  "detail": "Specific error message"
}
```

**404 Not Found:**
```json
{
  "error": "Resource not found",
  "detail": "Booking with ID 999 does not exist"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "detail": "An unexpected error occurred"
}
```

---

## Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Pagination

List endpoints support pagination with 20 items per page by default.

**Response Format:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/bookings/?page=3",
  "previous": "http://localhost:8000/api/v1/bookings/?page=1",
  "results": [...]
}
```

---

## Testing the API

### Using curl:

```bash
# Create booking
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"parent":1,"lsa":2,"child_name":"Tom","child_age":10,"learning_needs":"ADHD support","session_type":"online","start_time":"2024-08-12T10:00:00Z","end_time":"2024-08-12T12:00:00Z","subject":"Math","goals":"Improve skills","hourly_rate":"45.00","total_hours":"2.00","total_amount":"90.00","currency":"USD"}'

# Search LSAs
curl -X GET "http://localhost:8000/api/v1/lsas/search/?skills=ADHD"

# Test webhook
curl -X POST http://localhost:8000/api/v1/payments/webhook/test/ \
  -H "Content-Type: application/json" \
  -d '{"scenario":"success","booking_id":1}'
```

### Using Python requests:

```python
import requests

# Create booking
response = requests.post('http://localhost:8000/api/v1/bookings/', json={
    'parent': 1,
    'lsa': 2,
    'child_name': 'Tom',
    'child_age': 10,
    'learning_needs': 'ADHD support',
    'session_type': 'online',
    'start_time': '2024-08-12T10:00:00Z',
    'end_time': '2024-08-12T12:00:00Z',
    'subject': 'Math',
    'goals': 'Improve skills',
    'hourly_rate': '45.00',
    'total_hours': '2.00',
    'total_amount': '90.00',
    'currency': 'USD'
})

print(response.json())
```