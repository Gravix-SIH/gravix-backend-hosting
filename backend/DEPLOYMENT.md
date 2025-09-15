# MindMate Backend Deployment Guide - PythonAnywhere

## Overview
This guide covers deploying the MindMate Django backend API to PythonAnywhere.

## API Endpoints Created

### Chat Endpoints
- `POST /api/chat/` - Send message and get bot response
- `GET /api/sessions/{session_id}/` - Get session summary

### Assessment Endpoints
- `POST /api/assessments/` - Submit PHQ-9 or GAD-7 assessment
- `GET /api/users/{user_id}/assessments/` - Get user's assessment history

### User Data Endpoints
- `GET /api/users/{user_id}/` - Get user profile
- `GET /api/users/{user_id}/moods/` - Get user's mood history

### Health Check
- `GET /api/health/` - API health status

## PythonAnywhere Deployment Steps

### 1. Upload Code
```bash
# On PythonAnywhere bash console
cd ~
git clone https://github.com/yourusername/your-repo.git mindmate
cd mindmate/backend
```

### 2. Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 mindmate
workon mindmate
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Create .env file
cp .env.example .env
nano .env

# Update with your values:
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
OPENAI_API_KEY=your-openai-api-key
```

### 4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Static Files
```bash
python manage.py collectstatic
```

### 6. WSGI Configuration
Create/edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

# Add your project directory to Python path
path = '/home/yourusername/mindmate/backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'mindmate.settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 7. Web App Configuration
In PythonAnywhere Web tab:
- Source code: `/home/yourusername/mindmate/backend`
- Working directory: `/home/yourusername/mindmate/backend`
- Virtualenv: `/home/yourusername/.virtualenvs/mindmate`

### 8. Static Files Mapping
- URL: `/static/`
- Directory: `/home/yourusername/mindmate/backend/static`

## API Usage Examples

### Chat Request
```bash
curl -X POST https://yourusername.pythonanywhere.com/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am feeling depressed lately",
    "user_id": "user123"
  }'
```

### Assessment Submission
```bash
curl -X POST https://yourusername.pythonanywhere.com/api/assessments/ \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_type": "phq9",
    "responses": [1,2,1,0,2,1,1,0,1],
    "user_id": "user123"
  }'
```

## Frontend Integration

### JavaScript Example
```javascript
// Chat with the bot
const chatResponse = await fetch('https://yourusername.pythonanywhere.com/api/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: userMessage,
    user_id: userId,
    session_id: sessionId // optional
  })
});

const data = await chatResponse.json();
console.log('Bot response:', data.response);
console.log('Session ID:', data.session_id);
```

## Database Schema

### Key Models
- **ChatSession**: User chat sessions
- **Conversation**: Individual message exchanges
- **MoodEntry**: Detected moods from conversations
- **Assessment**: PHQ-9/GAD-7 results
- **UserProfile**: User engagement tracking

## Security Notes
- OpenAI API key stored in environment variables
- CORS configured for allowed origins
- SQLite database (upgrade to MySQL for production)
- Session-based tracking (no user authentication required)

## Monitoring
- Check logs in PythonAnywhere error logs
- Use `/api/health/` endpoint for health checks
- Monitor OpenAI API usage through their dashboard

## Troubleshooting
1. **Import errors**: Check virtual environment activation
2. **Database errors**: Run migrations again
3. **CORS issues**: Update ALLOWED_HOSTS and CORS_ALLOWED_ORIGINS
4. **OpenAI errors**: Verify API key and quota