# Foton API Documentation

## Base URL

```
https://foton.onrender.com/api
```

---

## Authentication

### Login

**Endpoint:** `POST /auth/login/`
**Authentication:** Public

**Request:**

```json
{
  "phone": "0783154278",
  "password": "your_password"
}
```

**Response:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error:**

```json
{
  "error": "Invalid Credentials"
}
```

---

### Refresh Token

**Endpoint:** `POST /token/refresh/`
**Authentication:** Public

**Request:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Verify Token

**Endpoint:** `POST /token/verify/`
**Authentication:** Public

**Request:**

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**

```json
{}
```

_Empty response means token is valid_

---

## Using Authenticated Endpoints

Add this header to all protected endpoints:

```
Authorization: Bearer <access_token>
```

**Example:**

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Password Reset

### Request OTP

**Endpoint:** `POST /auth/password-reset/request/`
**Authentication:** Public

**Request:**

```json
{
  "phone": "0783154278"
}
```

**Response:**

```json
{
  "success": true,
  "message": "OTP sent successfully"
}
```

---

### Verify OTP

**Endpoint:** `POST /auth/password-reset/verify/`
**Authentication:** Public

**Request:**

```json
{
  "phone": "0783154278",
  "otp": "123456"
}
```

**Response:**

```json
{
  "success": true,
  "message": "OTP verified successfully",
  "reset_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Reset Password

**Endpoint:** `POST /auth/password-reset/confirm/`
**Authentication:** Public

**Request:**

```json
{
  "reset_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "new_password": "new_password123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

---

## Transactions

### Send Money

**Endpoint:** `POST /transactions/send/`
**Authentication:** Required (Bearer Token)

**Request:**

```json
{
  "amount": 15000.0,
  "sender": {
    "first_name": "Mohamed",
    "last_name": "Benali",
    "phone_number": "0777777777",
    "national_id_number": "123456789"
  },
  "recipient": {
    "first_name": "Amine",
    "last_name": "Aiba",
    "phone_number": "0555555555"
  }
}
```

_Note: `national_id_number` is optional._

**Response:**

```json
{
  "message": "Transaction successful",
  "transfer_code": "1234567890",
  "transaction_id": "a1b2c3d4-e5f6-4g7h-8i9j-k0l1m2n3o4p5",
  "fee_charged": 150.0
}
```

**Error:**

```json
{
  "error": "Insufficient funds in agent wallet."
}
```

---

### Receive Money (Step 1: Lookup)

**Endpoint:** `POST /transactions/receive/lookup/`
**Authentication:** Required (Bearer Token)

**Request (Option A: By Code):**

```json
{
  "transfer_code": "1234567890"
}
```

**Request (Option B: By Name & Phone):**

```json
{
  "phone_number": "0555555555",
  "last_name": "Aiba"
}
```

**Response:**

```json
{
  "transaction_id": "a1b2c3d4-e5f6-...",
  "amount": 15000.0,
  "sender": {
    "name": "Mohamed Benali",
    "phone": "0777777777"
  },
  "recipient": {
    "name": "Amine Aiba",
    "phone": "0555555555"
  },
  "created_at": "2025-11-28T10:30:00Z",
  "status": "pending"
}
```

---

### Receive Money (Step 2: Claim)

**Endpoint:** `POST /transactions/receive/claim/`
**Authentication:** Required (Bearer Token)

**Request:**

```json
{
  "transaction_id": "a1b2c3d4-e5f6-...",
  "national_id_number": "987654321"
}
```

_Note: `national_id_number` is optional (from ID scan)._

**Response:**

```json
{
  "message": "Transaction claimed successfully.",
  "transaction_id": "a1b2c3d4-e5f6-...",
  "amount": 15000.0,
  "claimed_at": "2025-11-28T10:35:00Z"
}
```

---

## Token Lifetimes

- **Access Token:** 150 minutes
- **Refresh Token:** 100000 days
