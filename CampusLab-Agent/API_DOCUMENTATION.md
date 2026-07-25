# CampusLab Agent — REST API Documentation

Base URL: `/api`  
All endpoints returning JSON require standard HTTP status codes.  
Protected endpoints require HTTP Header: `Authorization: Bearer <JWT_TOKEN>`

---

## 1. Authentication Endpoints

### `POST /api/register`
Register a new student, faculty, or lab admin user.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@campus.edu",
  "password": "securepassword",
  "role": "student"
}
```

**Response (201 Created):**
```json
{
  "token": "eyJhbGciOiJIUzI1Ni...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@campus.edu",
    "role": "student",
    "created_at": "2026-07-25 14:00:00"
  }
}
```

---

### `POST /api/login`
Authenticate existing user and obtain a JWT access token.

**Request Body:**
```json
{
  "email": "john@campus.edu",
  "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1Ni...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@campus.edu",
    "role": "student"
  }
}
```

---

## 2. Laboratory Endpoints

### `GET /api/labs`
Fetch list of all computer laboratories with real-time seat counts.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Lab A - AI & Data Science",
    "capacity": 20,
    "open_time": "08:00",
    "close_time": "20:00",
    "description": "High performance GPU workstations",
    "total_systems": 20,
    "available_systems": 18
  }
]
```

---

### `GET /api/labs/{id}`
Fetch detailed lab information along with individual system statuses.

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Lab A - AI & Data Science",
  "capacity": 20,
  "systems": [
    { "id": 1, "lab_id": 1, "system_number": 1, "status": "available" },
    { "id": 2, "lab_id": 1, "system_number": 2, "status": "faulty" }
  ]
}
```

---

## 3. Computer System Endpoints

### `GET /api/systems`
List computer systems, optionally filtered by `lab_id` or `status`.

**Query Parameters:**
- `lab_id` (optional, integer)
- `status` (optional, string: `available` | `reserved` | `faulty`)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "lab_id": 1,
    "lab_name": "Lab A - AI & Data Science",
    "system_number": 1,
    "status": "available"
  }
]
```

---

### `PATCH /api/systems/{id}`
*(Admin Only)* Update a computer system's status (e.g. mark faulty or available).

**Request Body:**
```json
{
  "status": "faulty"
}
```

---

## 4. Booking Endpoints

### `POST /api/book`
*(Protected)* Reserve a computer system.

**Request Body:**
```json
{
  "lab_id": 1,
  "system_number": 5,
  "booking_date": "2026-07-26",
  "start_time": "10:00",
  "end_time": "12:00"
}
```

**Response (201 Created):**
```json
{
  "id": 10,
  "user_id": 1,
  "system_id": 5,
  "system_number": 5,
  "lab_name": "Lab A - AI & Data Science",
  "booking_date": "2026-07-26",
  "start_time": "10:00",
  "end_time": "12:00",
  "status": "active"
}
```

**Conflict Error Response (409 Conflict):**
```json
{
  "error": "Booking Conflict: System 5 is already reserved between 10:00 and 12:00.",
  "conflict_resolution": {
    "alternative_seats": [6, 7, 8],
    "alternative_timings": [
      { "start_time": "12:00", "end_time": "14:00" }
    ]
  }
}
```

---

### `PUT /api/booking/{id}`
*(Protected)* Modify an existing active reservation date, time, or system number.

**Request Body:**
```json
{
  "booking_date": "2026-07-27",
  "start_time": "14:00",
  "end_time": "16:00"
}
```

---

### `DELETE /api/booking/{id}`
*(Protected)* Cancel a reservation.

**Response (200 OK):**
```json
{
  "message": "Booking cancelled successfully.",
  "booking": { "id": 10, "status": "cancelled" }
}
```

---

### `GET /api/bookings`
*(Protected)* Retrieve user reservations. Admins retrieve all system bookings.

---

## 5. Fault Reporting Endpoints

### `POST /api/fault`
*(Protected)* Report an issue with a system.

**Request Body:**
```json
{
  "system_id": 4,
  "issue_type": "mouse",
  "description": "Right click button broken"
}
```

---

### `GET /api/faults`
*(Protected)* Retrieve fault reports.

---

### `PATCH /api/fault/{id}`
*(Admin Only)* Update fault status (`open`, `in_progress`, `repaired`).

---

## 6. AI Assistant Endpoint

### `POST /api/chat`
*(Protected)* Send a natural language string. The AI parses intent, executes backend services, and returns structured result & natural language output.

**Request Body:**
```json
{
  "message": "I need Lab A tomorrow from 10 to 12."
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "🎉 Successfully booked System #1 in Lab A - AI & Data Science for 2026-07-26 (10:00 - 12:00). Booking ID: #12",
  "booking": { "id": 12, "system_number": 1 }
}
```
