# Foton API Documentation

## Base URL

```
https://foton.onrender.com/api
```

---

## Authentication

### Login

**Endpoint:** `POST /auth/login/`

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

## Token Lifetimes

- **Access Token:** 150 minutes
- **Refresh Token:** 100000 days
