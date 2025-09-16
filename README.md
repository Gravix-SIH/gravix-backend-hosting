# Gravix Backend API Documentation

## User Endpoints

### Sign Up
Register a new user account.

```
POST /api/signup
```

**Input**
```json
{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "secure_password",
    "role": "student",
    "department": "Engineering"
}
```

**Response**
```json
{
    "user": {
        "id": "uuid-here",
        "name": "John Doe",
        "email": "user@example.com",
        "department": "Engineering",
        "role": "student",
        "is_anonymous": false,
        "anon_id": null,
        "is_active": true,
        "created_at": "2025-09-16T10:00:00Z",
        "updated_at": "2025-09-16T10:00:00Z"
    },
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token"
}
```

### Login
Login with existing credentials.

```
POST /api/login
```

**Input**
```json
{
    "email": "user@example.com",
    "password": "secure_password"
}
```

**Response**
```json
{
    "user": {
        "id": "uuid-here",
        "name": "John Doe",
        "email": "user@example.com",
        "department": "Engineering",
        "role": "student",
        "is_anonymous": false,
        "anon_id": null,
        "is_active": true,
        "created_at": "2025-09-16T10:00:00Z",
        "updated_at": "2025-09-16T10:00:00Z"
    },
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token"
}
```

### Create Anonymous Session
Creates a new anonymous user session.

```
POST /api/anon
```

**Response**
```json
{
    "user": {
        "id": "uuid-here",
        "name": "anon_xxxxxxxx",
        "email": null,
        "department": "",
        "role": "anonymous",
        "is_anonymous": true,
        "anon_id": "anon_xxxxxxxx",
        "is_active": true,
        "created_at": "2025-09-16T10:00:00Z",
        "updated_at": "2025-09-16T10:00:00Z"
    },
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token"
}
```

### Get User Profile
Get the current user's profile.

```
GET /api/users/me
```

**Headers**
```
Authorization: Bearer <jwt-access-token>
```

**Response**
For regular users:
```json
{
    "user": {
        "id": "uuid-here",
        "name": "John Doe",
        "email": "user@example.com",
        "department": "Engineering",
        "role": "student",
        "is_anonymous": false,
        "anon_id": null,
        "is_active": true,
        "created_at": "2025-09-16T10:00:00Z",
        "updated_at": "2025-09-16T10:00:00Z"
    }
}
```

For anonymous users:
```json
{
    "user": {
        "id": "uuid-here",
        "name": "anon_xxxxxxxx",
        "email": null,
        "department": "",
        "role": "anonymous",
        "is_anonymous": true,
        "anon_id": "anon_xxxxxxxx",
        "is_active": true,
        "created_at": "2025-09-16T10:00:00Z",
        "updated_at": "2025-09-16T10:00:00Z"
    }
}
```

### Get User Details
Get details of a specific user. Only accessible by admins or the user themselves.

```
GET /api/users/<uuid>
```

**Headers**
```
Authorization: Bearer <jwt-access-token>
```

**Response**
```json
{
    "user": {
        "id": "uuid-here",
        "name": "John Doe",
        "email": "user@example.com",
        "department": "Engineering",
        "role": "student",
        "is_anonymous": false,
        "anon_id": null,
        "is_active": true,
        "created_at": "2025-09-16T10:00:00Z",
        "updated_at": "2025-09-16T10:00:00Z"
    }
}
```

### Update User Details
Update details of a specific user. Only accessible by admins or the user themselves.

```
PATCH /api/users/<uuid>
```

**Headers**
```
Authorization: Bearer <jwt-access-token>
```

**Input**
```json
{
    "name": "Updated Name",
    "department": "Updated Department"
}
```

**Response**
```json
{
    "user": {
        "id": "uuid-here",
        "name": "Updated Name",
        "email": "user@example.com",
        "department": "Updated Department",
        "role": "student",
        "is_anonymous": false,
        "anon_id": null,
        "is_active": true,
        "created_at": "2025-09-16T10:00:00Z",
        "updated_at": "2025-09-16T10:00:00Z"
    }
}
```

### Refresh Token
Get a new access token using refresh token.

```
POST /api/refresh
```

**Input**
```json
{
    "refresh": "jwt-refresh-token"
}
```

**Response**
```json
{
    "access": "new-jwt-access-token"
}
```

## Authentication
All endpoints except `/api/anon`, `/api/signup`, `/api/login`, and `/api/refresh` require authentication using JWT Bearer token in the Authorization header.

```
Authorization: Bearer <jwt-access-token>
```

## Chat Endpoints

### Health Check
Check if the chat service is running.

```
GET /api/v1/chatbot/health/
```

**Response**
```json
{
    "status": "healthy",
    "timestamp": "2025-09-16T10:00:00Z"
}
```

### Chat Message
Send a message to the AI chatbot and get a response.

```
POST /api/v1/chatbot/chat/
```

**Input**
```json
{
    "message": "I'm feeling anxious about my exams",
    "session_id": "uuid-here",  // Optional
    "anonymous_id": "anon_id"   // Optional
}
```

**Response**
```json
{
    "response": "I understand that exams can be stressful...",
    "session_id": "uuid-here",
    "crisis_detected": false     // true if crisis keywords detected
}
```

#### Features:
- Maintains conversation history within a session
- Detects and tracks user's mood patterns
- Crisis detection and immediate support resources
- Works with both authenticated and anonymous users
- Session persistence for continuous conversations

### Get Conversation History
Retrieve the chat history for a specific session.

```
GET /api/v1/chatbot/chat/history/<session_id>/
```

**Response**
```json
{
    "messages": [
        {
            "sender": "user",
            "message": "Hi, I'm feeling stressed",
            "timestamp": "2025-09-16T10:00:00Z",
            "mood": "anxious"
        },
        {
            "sender": "bot",
            "message": "I understand that you're feeling stressed...",
            "timestamp": "2025-09-16T10:00:01Z"
        }
    ]
}
```

### Get Mood Summary
Get a summary of mood patterns for a specific chat session.

```
GET /api/v1/chatbot/chat/mood/<session_id>/
```

**Response**
```json
{
    "session_id": "uuid-here",
    "mood_summary": {
        "anxious": 3,
        "sad": 1,
        "happy": 2
    },
    "start_date": "2025-09-16T10:00:00Z",
    "end_date": "2025-09-16T11:00:00Z"
}
