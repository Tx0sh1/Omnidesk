# OmniDesk Setup Guide

## Overview
OmniDesk is a comprehensive ticketing system built with Flask (Python) backend and React (TypeScript) frontend.

## Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

## Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
A `.env` file has been created in the backend directory with default values:
```env
FLASK_APP=omnidesk.py
FLASK_ENV=development
SECRET_KEY=omni-dev-key-change-in-production
DATABASE_URL=sqlite:///app.db
MAIL_SERVER=
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=
MAIL_PASSWORD=
JWT_SECRET_KEY=jwt-dev-secret-change-in-production
```

**Important**: Update the SECRET_KEY and JWT_SECRET_KEY with secure random values for production.

### 5. Initialize database
**Option 1: Using Flask CLI (Make sure you're in the backend directory):**
```bash
# From the backend directory
flask db upgrade
```

**Option 2: Using the standalone migration script (if Flask CLI has issues):**
```bash
# From the backend directory
python run_migrations.py
```

If you get "Could not import 'omnidesk'" error, make sure:
- You're in the backend directory
- Your virtual environment is activated
- All dependencies are installed
- Try the standalone migration script: `python run_migrations.py`

### 6. Create admin user
```bash
python setup_admin.py
```

### 7. Run backend server
```bash
flask run
```
The backend will be available at `http://localhost:5000`

## Frontend Setup

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure environment
Create a `.env` file in the frontend directory:
```env
REACT_APP_API_URL=http://localhost:5000
```

### 4. Run frontend development server
```bash
npm start
```
The frontend will be available at `http://localhost:3000`

## Common Issues and Solutions

### 1. Jinja2 Template Errors
**Problem**: `TemplateNotFound` errors
**Solution**: All templates are now properly created in `backend/app/templates/`

### 2. Database Migration Issues
**Problem**: Database schema doesn't match models
**Solution**: 
```bash
flask db migrate -m "description"
flask db upgrade
```

### 3. Flask Command Issues
**Problem**: `Error: Could not import 'omnidesk'` or `Error: No such command 'db'`
**Solutions**: 
1. **Check working directory**: Make sure you're in the backend directory when running Flask commands
2. **Activate virtual environment**: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. **Verify dependencies**: `pip show Flask-Migrate` should show the package is installed
4. **Check .env file**: Ensure `.env` file exists in backend directory with `FLASK_APP=omnidesk.py`
5. **Use standalone migration script**: `python run_migrations.py`
6. **Alternative from project root**: 
   ```bash
   # From project root (where .flaskenv is located)
   flask db upgrade
   ```

**Note**: The correct command is `flask db upgrade`, not `flask db update`

### 4. CORS Issues
**Problem**: Frontend can't connect to backend
**Solution**: CORS is configured for `localhost:3000`. Update in `backend/app/__init__.py` if needed.

### 5. File Upload Issues
**Problem**: Uploaded files not found
**Solution**: Ensure `backend/app/static/uploads/` directory exists and is writable.

### 6. Email Configuration
**Problem**: Password reset emails not sending
**Solution**: Configure SMTP settings in environment variables.

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - Logout (blacklist JWT token)
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/reset-password-request` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token

### Tickets
- `GET /api/tickets` - List tickets (authenticated)
- `POST /api/tickets` - Create ticket (authenticated)
- `GET /api/tickets/<id>` - Get ticket details (authenticated)
- `PUT /api/tickets/<id>` - Update ticket (authenticated)
- `POST /api/tickets/<id>/reply` - Reply to ticket (authenticated)

### Client API (No authentication required)
- `POST /api/client/submit-ticket` - Submit client ticket
- `GET /api/client/ticket-status/<reference>` - Check ticket status

### Users (Admin only)
- `GET /api/users` - List users
- `GET /api/users/<id>` - Get user details
- `PUT /api/users/<id>` - Update user

## Ticketing System Recommendations

### Current Features
✅ User authentication and registration  
✅ JWT-based API authentication  
✅ Ticket creation and management  
✅ Status tracking (Open, In-Progress, Closed)  
✅ Priority levels (Low, Medium, High)  
✅ Admin user management  
✅ Client ticket submission portal  
✅ Email notifications for password reset  
✅ File upload support for tickets  
✅ Responsive React frontend  

### Recommended Enhancements

#### 1. **User Role Management**
- **Current**: Simple admin flag
- **Recommendation**: Implement role-based access control (RBAC)
  - Roles: Admin, Manager, Agent, Client
  - Permissions: Create, Read, Update, Delete tickets
  - Department-based access control

#### 2. **Ticket Assignment and Workflow**
- **Current**: Basic status tracking
- **Recommendation**: 
  - Automatic ticket assignment based on department/expertise
  - Escalation rules (auto-escalate after X hours)
  - SLA (Service Level Agreement) tracking
  - Ticket templates for common issues

#### 3. **Communication Enhancements**
- **Current**: Basic reply system
- **Recommendation**:
  - Real-time notifications (WebSocket/Server-Sent Events)
  - Email notifications for ticket updates
  - Internal notes vs public comments
  - @mention system for team collaboration

#### 4. **Reporting and Analytics**
- **Recommendation**:
  - Ticket volume reports
  - Response time analytics
  - Agent performance metrics
  - Customer satisfaction surveys
  - Dashboard with key metrics

#### 5. **Knowledge Base Integration**
- **Recommendation**:
  - FAQ system
  - Solution articles
  - Search functionality
  - Auto-suggest solutions based on ticket content

#### 6. **Advanced Features**
- **Recommendation**:
  - Ticket merging and splitting
  - Bulk operations
  - Custom fields
  - Automation rules
  - Integration with external tools (Slack, Teams)
  - Mobile app support

#### 7. **Security Enhancements**
- **Current**: JWT authentication, password hashing
- **Recommendation**:
  - Two-factor authentication (2FA)
  - Rate limiting
  - Audit logging
  - Data encryption at rest
  - GDPR compliance features

#### 8. **Performance Optimizations**
- **Recommendation**:
  - Database indexing
  - Caching (Redis)
  - Pagination for large datasets
  - Background job processing (Celery)
  - CDN for file uploads

### Deployment Recommendations

#### Production Setup
1. **Database**: PostgreSQL instead of SQLite
2. **Web Server**: Gunicorn + Nginx
3. **Environment**: Docker containers
4. **Monitoring**: Application logging and monitoring
5. **Backup**: Regular database backups
6. **SSL**: HTTPS with proper certificates

#### Environment Variables for Production
```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/omnidesk
REDIS_URL=redis://localhost:6379
SECRET_KEY=secure-random-key
JWT_SECRET_KEY=another-secure-key
```

## Testing
- Unit tests for API endpoints
- Integration tests for workflows
- Frontend component tests
- End-to-end testing

## Support
For issues and questions, check the logs in `backend/logs/omnidesk.log` and ensure all environment variables are properly configured.
