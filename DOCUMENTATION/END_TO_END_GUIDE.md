# 🎯 LSA Booking System — End-to-End Guide (Simple Explanation)

> Read this to understand the whole project from request to response, and to explain it
> confidently to anyone — interviewers, recruiters, or your LinkedIn audience.

---

## 1. The Elevator Pitch (30 seconds)

> *"I built a production-ready REST API that connects parents with specialized Learning
> Support Assistants (LSAs) for children with learning difficulties like ADHD, Autism, and
> Dyslexia. Parents can search for LSAs by skills, city, and price; check real-time
> availability; and book sessions — with the system automatically preventing
> double-bookings. It handles payments through a mock payment gateway with webhook
> integration, and comes with a 19-test suite, 70% code coverage, and a CI/CD pipeline
> running on PostgreSQL."*

**Tech stack:** Django 4.2 · Django REST Framework · PostgreSQL 15 · pytest · GitHub Actions

---

## 2. Simple Architecture (3 layers)

```
┌─────────────────────────────────────────────────────────────┐
│  CLIENT (browser / Postman / curl)                          │
│  sends HTTP request → receives JSON response                │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTP (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  DJANGO — Layer 1: URL routing (bookings/urls.py)           │
│  decides which view handles the request                     │
│                                                             │
│  Layer 2: VIEWS (bookings/views.py)                         │
│  receives request → asks serializer to validate →           │
│  talks to models → returns JSON response                    │
│                                                             │
│  Layer 3: SERIALIZERS (bookings/serializers.py)             │
│  convert JSON ↔ Python objects + validate business rules    │
│  (DRF equivalent of Django Forms)                           │
│                                                             │
│  Layer 4: MODELS (bookings/models.py)                       │
│  business logic + database mapping (ORM)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │  SQL (via Django ORM)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  POSTGRESQL — 3 tables: parents, lsa_profiles,              │
│  booking_requests (3NF normalized, composite indexes)       │
└─────────────────────────────────────────────────────────────┘

  + MOCK PAYMENT GATEWAY (payment_service.py) — simulates Stripe-like API
  + WEBHOOK HANDLER (webhooks.py) — payment gateway calls us back
```

**The one-sentence version:** *Client → URL → View → Serializer → Model → Database → Model → Serializer → JSON back to client.*

---

## 3. The 3 Database Tables (the heart of the project)

### 👨‍👩‍👧 `parents` — who is booking
| Field | Meaning |
|---|---|
| `email` | unique — one parent one account |
| `city`, `state` | used for local search |

### 👩‍🏫 `lsa_profiles` — who is being booked
| Field | Meaning |
|---|---|
| `specialization` | ADHD / Autism / Dyslexia… |
| `skills` | comma-separated text: `"ADHD,Autism,Sign Language"` (searchable) |
| `hourly_rate` | price per hour (Decimal, 2 dp) |
| `is_available` | can they accept new bookings? |
| `verified` + `profile_status` | only `active` + `verified` LSAs appear in search |

### 📅 `booking_requests` — the bridge between them
| Field | Meaning |
|---|---|
| `parent` (FK) → parents | who booked |
| `lsa` (FK) → lsa_profiles | who was booked |
| `start_time`, `end_time` | the session slot (both indexed) |
| `status` | `pending` → `confirmed` → `in_progress` → `completed` (or `cancelled`) |
| `payment_status` | `pending` → `completed` / `failed` / `refunded` |
| `total_amount` | auto-calculated = `hourly_rate × total_hours` |

**Relationships:** one Parent → many Bookings · one LSA → many Bookings (both `CASCADE`).

**Why indexes matter (interview point):** composite indexes on `(lsa, status)`,
`(start_time, end_time)`, `(profile_status, verified)` make the two hot queries fast:
*double-booking checks* and *LSA search*.

---

## 4. The End-to-End Story (walk through a real booking)

This is exactly what happens when a parent books Jane Smith (ADHD specialist, $45/hr)
for 2 hours of Math:

### Step 1 — Search (GET `/api/v1/lsas/search/?skills=ADHD&city=Los Angeles`)
```
URL router  →  LSA_SearchView
View        →  LSA_SearchSerializer validates the query params
            →  builds queryset: profile_status='active', verified=True
            →  .filter(skills__icontains='adhd')  →  .filter(city__icontains='los angeles')
            →  N+1 prevention: select_related() + prefetch_related('booking_requests')
            →  Response: {count: 1, results: [Jane Smith…]}
```
**Performance point:** `icontains` on a comma-separated skills text is simple and demo-able;
real production would use PostgreSQL full-text search or a many-to-many table.

### Step 2 — Check availability (GET `/api/v1/lsas/check-availability/?lsa_id=1&start_time=…&end_time=…`)
```
View → lsa.is_available_for_booking(start, end)
     → checks: is_available=True? profile_status='active'?
     → looks for overlapping active bookings: start < end_new AND end > start_new
     → returns {available: true/false, overlapping_bookings: […]}
```

### Step 3 — Create booking (POST `/api/v1/bookings/`)
```
URL router  →  BookingViewSet.create → Booking_CreateSerializer
Serializer  →  validates end_time > start_time
            →  validates the LSA exists, is available, profile is active
            →  POKA-YOKE: checks for overlapping bookings → 400 if conflict
            →  validates total_amount = hourly_rate × total_hours (±0.01)
Model       →  Booking_Request.save() → full_clean() runs again (second safety net)
            →  total_amount auto-calculated & quantized to 2 dp if missing
Database    →  INSERT row (status='pending', payment_status='pending')
Response    →  201 Created + full booking JSON
```

### Step 4 — Payment (mock gateway + webhook)
```
Payment gateway (simulated) creates a payment intent:
    payment_gateway.create_payment_intent(amount=90.00, currency='USD')
    → pay_abc123…, client_secret

Gateway "processes" the payment (90% random success):
    process_payment(payment_id) → {success: true, status: 'succeeded'}

Then the gateway calls OUR webhook (like Stripe does in real life):
    POST /api/v1/payments/webhook/
    {"event": "payment.success", "payment_id": "pay_abc…", "booking_id": 4, …}

Webhook handler:
    payment.success  → booking.payment_status='completed', payment_id saved
                     → auto-confirms: booking.confirm_booking()
                     → status='confirmed', confirmed_at=now
    payment.failed   → booking.payment_status='failed', status='payment_failed'
    payment.refunded → booking.payment_status='refunded', booking cancelled
```
**Interview point:** the webhook pattern means our server never calls the gateway to check;
the gateway *pushes* the result to us — decoupled, async, production-style.

### Step 5 — Confirm / Cancel (POST `/api/v1/bookings/{id}/confirm/` or `/cancel/`)
```
confirm → requires payment_status='completed'
        → re-checks LSA availability (the slot might have been taken since!)
        → status='confirmed', confirmed_at=now
cancel  → status='cancelled', cancelled_at=now, reason stored in notes
```

---

## 5. The Poka-Yoke (Double-Booking Prevention) — explained simply

**"Poka-Yoke" = mistake-proofing** (a Japanese manufacturing concept): design the system
so the mistake is *impossible*, not just unlikely.

Double-booking is prevented at **3 levels** (defense in depth):

| Level | Where | What happens |
|---|---|---|
| 1. Serializer | `Booking_CreateSerializer.validate()` | rejects overlapping bookings at the API boundary → HTTP 400 |
| 2. Model `clean()` | `Booking_Request.clean()` | same check runs on every save — even code paths that bypass the API |
| 3. Availability re-check | `confirm_booking()` | before confirming, the slot is checked *again* — because time may have passed |

**Overlap logic (the core SQL):**
```python
existing = Booking_Request.objects.filter(
    lsa=lsa,
    status__in=['pending', 'confirmed', 'in_progress'],  # active statuses only
    start_time__lt=end_time,       # existing booking STARTS before new one ends
    end_time__gt=start_time        # existing booking ENDS after new one starts
)
```
If existing → conflict. *(A cancelled booking never blocks a slot.)*

**Extra Poka-Yoke touches:**
- `total_amount` is **auto-calculated** from rate × hours — and if provided, verified against the math (error if off by more than $0.01)
- `end_time` must be after `start_time` — enforced in serializer AND model
- Payments can only confirm a booking; a booking can only be confirmed once

---

## 6. The 19 Test Cases — explained so you can talk about them

### `ParentModelTest` (3 tests) — the simplest entity
| Test | What it proves |
|---|---|
| `test_create_parent_success` | a parent can be created; `full_name` property works; default `is_active=True` |
| `test_parent_email_unique` | second parent with same email raises a DB integrity error (unique constraint) |
| `test_parent_str_method` | `str(parent)` → `"John Doe (john.doe@example.com)"` |

### `LSA_ProfileModelTest` (2 tests)
| Test | What it proves |
|---|---|
| `test_create_lsa_success` | LSA creation works with all professional fields |
| `test_lsa_skills_list_property` | `"ADHD,Autism,Sign Language"` → clean list of 3 skills |

### `Booking_RequestModelTest` (6 tests) — the business logic core
| Test | What it proves |
|---|---|
| `test_create_booking_success` | booking created with `status='pending'`, amount saved correctly |
| `test_booking_validation_end_time_after_start` | end before start → `ValidationError` |
| `test_booking_double_booking_prevention` | overlapping booking → `ValidationError` (model-level Poka-Yoke) |
| `test_booking_amount_calculation` | amount auto-calculated when omitted → exactly `90.00` |
| `test_booking_confirm_method` | confirm works when payment completed; sets `confirmed_at` |
| `test_booking_cancel_method` | cancel sets `cancelled`, records `cancelled_at` |

### `BookingAPITest` (3 tests) — the API layer
| Test | What it proves |
|---|---|
| `test_create_booking_api_success` | full JSON POST → **201**, exactly 1 booking in DB |
| `test_create_booking_api_double_booking_prevention` | first booking 201 → overlapping one **400** with conflict message |
| `test_lsa_search_api_success` | search returns the matching LSA (count=1, Jane Smith) — *regression test* |
| `test_lsa_search_api_no_filters_returns_all_active` | no filters → all active LSAs returned (count=1) — *regression test* |

> 🐛 **Story to tell:** the last two tests were added after I found a real bug — DRF's
> `BooleanField` treats query strings like HTML forms, so a missing `is_available` param
> became `False` and silently hid ALL available LSAs. The old test only checked HTTP 200,
> so it passed while the endpoint was broken. I fixed the view and strengthened the tests
> so it can't regress. (19 tests = 17 original + 2 new)

### `PaymentServiceTest` (2 tests) — the mock gateway
| Test | What it proves |
|---|---|
| `test_create_payment_intent` | returns `payment_id`, correct amount, status `pending` |
| `test_process_payment_success` | a created intent can be processed → `success` + `status` present |

### `LSA_AvailabilityTest` (2 tests) — the availability engine
| Test | What it proves |
|---|---|
| `test_lsa_available_for_booking` | free slot → `is_available_for_booking()` = True |
| `test_lsa_not_available_when_booked` | after a confirmed booking, same slot → False |

**Coverage:** 70% overall; models 96%, serializers 85%, tests 100%. Webhooks/views are
the gaps (endpoints exercised manually, not yet unit-tested) — a great "what's next" story.

---

## 7. Live Demo Script (show it, don't just tell it)

```bash
# 1. Seed sample data (3 parents, 5 LSAs, 3 bookings)
python create_sample_data.py

# 2. Search — filters work
curl "http://localhost:8000/api/v1/lsas/search/?skills=ADHD"

# 3. Check availability before booking
curl "http://localhost:8000/api/v1/lsas/check-availability/?lsa_id=4&start_time=2026-08-20T10:00:00Z&end_time=2026-08-20T12:00:00Z"

# 4. Create a booking → 201
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"parent":1,"lsa":4,"child_name":"Tom","child_age":10,
       "learning_needs":"ADHD support","session_type":"online",
       "start_time":"2026-08-20T10:00:00Z","end_time":"2026-08-20T12:00:00Z",
       "subject":"Math","goals":"Improve math","hourly_rate":"45.00",
       "total_hours":"2.00","total_amount":"90.00","currency":"USD"}'

# 5. Try the SAME slot again → 400 (double-booking prevented!)
curl -X POST http://localhost:8000/api/v1/bookings/ [same body]

# 6. Simulate the payment webhook → booking auto-confirms
curl -X POST http://localhost:8000/api/v1/payments/webhook/test/ \
  -H "Content-Type: application/json" \
  -d '{"scenario":"success","booking_id":4}'

# 7. Full test suite
pytest
```

---

## 8. Key Words to Drop (and what they actually mean)

| Term | Plain meaning |
|---|---|
| **Poka-Yoke** | mistake-proofing — the bug can't happen by design (3-layer double-booking check) |
| **3NF normalization** | no redundant data; each fact stored once, related by foreign keys |
| **Composite indexes** | DB indexes on multiple columns (`(lsa, status)`) → fast lookups |
| **N+1 query prevention** | one query instead of 1+per-row; `select_related` (JOINs) + `prefetch_related` (batched) |
| **Webhook integration** | the payment provider calls OUR endpoint when payment status changes |
| **Serializer-level + model-level validation** | rules enforced at the API boundary AND the data layer (defense in depth) |
| **Mock payment gateway** | a Stripe-like service simulated locally, with `create_payment_intent` / `process_payment` / `refund` |
| **CI/CD pipeline** | every push → GitHub Actions spins up PostgreSQL 15, runs all tests + flake8 automatically |
| **Decimal fields** | money stored as exact decimals (never float) to avoid rounding bugs |
| **`select_related` vs `prefetch_related`** | for FK lookups vs reverse/many relations — both kill N+1 |

---

## 9. Answering "What would you improve next?" (roadmap answers)

- **Auth** — JWT so parents/LSAs log in; right now there's no authentication
- **Real payment gateway** — swap the mock for Stripe/PayPal (the webhook already fits Stripe's pattern)
- **Search quality** — PostgreSQL full-text search instead of `icontains`
- **More tests** — push coverage past 85% (webhooks and views are the current gaps)
- **Docker** — containerize app + DB for one-command setup
- **Caching** — Redis for hot LSA search results; rate limiting on the API
