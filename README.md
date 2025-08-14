# OmniDesk - Complete Ticketing System

OmniDesk is a modern, full-stack ticketing system designed to help manage user requests and support issues efficiently. Built with Flask (Python) backend and React (TypeScript) frontend, this project demonstrates real-world development practices and provides a fully functional support desk solution.

## 🚀 Tech Stack

<<<<<<< HEAD
- Python (Flask)
- JavaScript (React + TailwindCSS)
- SQLite (planned for database)
- Git & GitHub for version control
=======
### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **Flask-Migrate** - Database migrations
- **Flask-JWT-Extended** - JWT authentication
- **Flask-Mail** - Email functionality
- **SQLite/PostgreSQL** - Database
>>>>>>> aa6b7104 (Day11: feat: Complete frontend rewrite with enhanced features and resolved tailwind CSS issues)

### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Router** - Client-side routing

## ✨ Features

### ✅ Implemented Features
- **User Authentication** - Registration, login, logout with JWT tokens
- **Ticket Management** - Create, view, update, and track tickets
- **Status Tracking** - Open, In-Progress, Closed status workflow
- **Priority Levels** - Low, Medium, High priority classification
- **Admin Dashboard** - User management and ticket oversight
- **Client Portal** - Public ticket submission without registration
- **File Uploads** - Attach files to tickets
- **Email Notifications** - Password reset functionality
- **Responsive Design** - Mobile-friendly interface
- **API Documentation** - RESTful API endpoints
- **Token Blacklisting** - Secure logout functionality
- **Role-based Access** - Admin and regular user permissions

### 🔄 In Progress
- Real-time notifications
- Ticket assignment system
- Advanced reporting

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
Run the quick start script from the project root:

```bash
python start_omnidesk.py
```

This will automatically:
- Check prerequisites (Python 3.8+, Node.js)
- Set up virtual environment
- Install all dependencies
- Run database migrations
- Start both backend and frontend servers

### Option 2: Manual Setup

#### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run_migrations.py  # or: flask db upgrade
python setup_admin.py     # Create admin user
flask run                 # Start backend server
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start                 # Start frontend server
```

## 🌐 Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Admin Dashboard**: Login with admin credentials

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration  
- `POST /api/auth/logout` - Secure logout (blacklist token)
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user info

### Ticket Management
- `GET /api/tickets` - List user tickets
- `POST /api/tickets` - Create new ticket
- `GET /api/tickets/<id>` - Get ticket details
- `PUT /api/tickets/<id>` - Update ticket

### Client Portal (No Auth Required)
- `POST /api/client/submit-ticket` - Submit support ticket
- `GET /api/client/ticket-status/<ref>` - Check ticket status

### Admin Endpoints
- `GET /api/users` - List all users
- `PUT /api/users/<id>` - Update user details

## 🔧 Configuration

### Environment Variables

**Backend** (`backend/.env`):
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
JWT_SECRET_KEY=your-jwt-secret
MAIL_SERVER=your-smtp-server
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password
```

**Frontend** (`frontend/.env`):
```env
REACT_APP_API_URL=http://localhost:5000
```

## 🐛 Troubleshooting

### Common Issues

**"Could not import 'omnidesk'" Error**
- Ensure you're in the correct directory
- Activate virtual environment: `source venv/bin/activate`
- Use standalone migration: `python run_migrations.py`

**Database Issues**
- Run: `python run_migrations.py`
- Or: `flask db upgrade` from backend directory

**CORS Errors**
- Backend is configured for `localhost:3000`
- Check frontend is running on correct port

**Port Already in Use**
- Backend: Change port with `flask run --port 5001`
- Frontend: React will prompt for alternative port

## 🧪 Testing

Run the setup verification:
```bash
cd backend
python test_setup.py
```

## 📁 Project Structure

```
omnidesk/
├── backend/                 # Flask backend
│   ├── app/                # Application package
│   │   ├── api/           # API blueprints
│   │   ├── models.py      # Database models
│   │   └── __init__.py    # App factory
│   ├── migrations/         # Database migrations
│   ├── requirements.txt    # Python dependencies
│   ├── omnidesk.py        # Application entry point
│   └── run_migrations.py  # Migration helper
├── frontend/               # React frontend
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   └── services/      # API services
│   └── package.json       # Node dependencies
├── start_omnidesk.py      # Quick start script
└── README.md              # This file
```

## 🚀 Deployment

### Production Recommendations
- Use PostgreSQL instead of SQLite
- Set up proper environment variables
- Use Gunicorn + Nginx for backend
- Build React app: `npm run build`
- Enable HTTPS with SSL certificates

### Docker Support (Coming Soon)
Docker configurations for easy deployment will be added.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🎯 Future Enhancements

- Real-time chat/notifications
- Advanced reporting and analytics
- Mobile app
- Integration with external tools (Slack, Teams)
- Knowledge base system
- SLA tracking
- Multi-language support

---

**Built with dedication by @Tx0sh1** | A journey of continuous learning and improvement.

For detailed setup instructions, see [Backend Setup Guide](backend/README_SETUP.md).
