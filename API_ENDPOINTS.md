# Authentication Endpoints Documentation

## Base URL: https://civic-ops.onrender.com

---

## 1. Send OTP
**Endpoint:** `POST /auth/send-otp`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "phone": "+1234567890"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "data": {
    "expires_in": 300,
    "retry_after": 60
  }
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Error message here"
}
```

---

## 2. Verify OTP
**Endpoint:** `POST /auth/verify-otp`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "phone": "+1234567890",
  "otp": "123456"
}
```

**Response (200 OK) - New User:**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "data": {
    "user_exists": false,
    "session": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh_token": "abc123def456...",
      "expires_at": "2024-01-01T01:00:00Z"
    }
  }
}
```

**Response (200 OK) - Existing User:**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "data": {
    "user_exists": true,
    "session": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh_token": "abc123def456...",
      "expires_at": "2024-01-01T01:00:00Z"
    },
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "phone": "+1234567890",
      "full_name": "John Doe",
      "created_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid or expired OTP"
}
```

---

## 3. Complete Profile
**Endpoint:** `POST /auth/complete-profile`

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "full_name": "John Doe"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile completed successfully",
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "phone": "+1234567890",
      "full_name": "John Doe",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid token"
}
```

**Response (422 Unprocessable Content):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["header", "authorization"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

## 4. Refresh Token
**Endpoint:** `POST /auth/refresh`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh_token": "abc123def456..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_at": "2024-01-01T01:00:00Z"
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid or expired refresh token"
}
```

---

## 5. Logout
**Endpoint:** `POST /auth/logout`

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid token"
}
```

**Response (422 Unprocessable Content):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["header", "authorization"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

## 6. Update Profile
**Endpoint:** `PUT /auth/profile`

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "full_name": "John Smith"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "phone": "+1234567890",
      "full_name": "John Smith",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T01:00:00Z"
    }
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid token"
}
```

**Response (422 Unprocessable Content):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["header", "authorization"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

## Authentication Flow

### For New Users:
1. `POST /auth/send-otp` with phone number
2. `POST /auth/verify-otp` with phone and OTP → get access_token (short expiry)
3. `POST /auth/complete-profile` with access_token and full_name → profile completed
4. Use new access_token for authenticated requests

### For Existing Users:
1. `POST /auth/send-otp` with phone number
2. `POST /auth/verify-otp` with phone and OTP → get access_token and user data
3. Use access_token for authenticated requests

### Token Management:
- Use `POST /auth/refresh` when access_token expires
- Use `POST /auth/logout` to invalidate tokens
- Use `PUT /auth/profile` to update user profile

---

## Notes:
- Phone numbers should be in international format (e.g., +1234567890)
- Access tokens expire in 24 hours (or 1 hour for incomplete profiles)
- Refresh tokens expire in 30 days
- OTP expires in 5 minutes
- All timestamps are in ISO 8601 format with 'Z' suffix (UTC)