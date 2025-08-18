import re
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from flask import request, current_app
from werkzeug.utils import secure_filename
import bleach
from email_validator import validate_email, EmailNotValidError

# Security constants
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'documents': {'pdf', 'doc', 'docx', 'txt', 'rtf'},
    'archives': {'zip', 'rar', '7z'},
    'spreadsheets': {'xls', 'xlsx', 'csv'}
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES_PER_UPLOAD = 5

# HTML sanitization settings
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'hr', 'table', 'thead', 'tbody', 'tr', 'td', 'th'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'table': ['class'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan']
}

class ValidationError(Exception):
    """Custom validation error"""
    pass

class SecurityError(Exception):
    """Custom security error"""
    pass

def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks"""
    if not content:
        return ""
    
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

def validate_email_address(email: str) -> bool:
    """Validate email address format and domain"""
    try:
        valid = validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's between 10-15 digits (international format)
    return 10 <= len(digits_only) <= 15

def validate_password_strength(password: str) -> Dict[str, Union[bool, List[str]]]:
    """Validate password strength and return detailed feedback"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # Check for common patterns
    if password.lower() in ['password', '12345678', 'qwerty', 'admin', 'user']:
        errors.append("Password is too common")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)

def hash_file_content(file_path: str) -> str:
    """Generate SHA-256 hash of file content"""
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""

def allowed_file(filename: str, file_type: str = 'all') -> bool:
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'all':
        all_extensions = set()
        for exts in ALLOWED_EXTENSIONS.values():
            all_extensions.update(exts)
        return extension in all_extensions
    
    return extension in ALLOWED_EXTENSIONS.get(file_type, set())

def validate_file_upload(file) -> Dict[str, Union[bool, str]]:
    """Comprehensive file upload validation"""
    if not file:
        return {'is_valid': False, 'error': 'No file provided'}
    
    if not file.filename:
        return {'is_valid': False, 'error': 'No filename provided'}
    
    # Check file extension
    if not allowed_file(file.filename):
        return {'is_valid': False, 'error': 'File type not allowed'}
    
    # Check file size (if we can determine it)
    try:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return {'is_valid': False, 'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}
        
        if file_size == 0:
            return {'is_valid': False, 'error': 'File is empty'}
            
    except Exception:
        pass  # If we can't determine size, continue
    
    return {'is_valid': True, 'error': None}

def secure_upload_filename(filename: str) -> str:
    """Create a secure filename for uploaded files"""
    if not filename:
        return f"file_{secrets.token_hex(8)}"
    
    # Get the file extension
    name, ext = os.path.splitext(filename)
    
    # Create a secure base name
    secure_name = secure_filename(name) or "file"
    
    # Add timestamp and random suffix to prevent conflicts
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    random_suffix = secrets.token_hex(4)
    
    return f"{secure_name}_{timestamp}_{random_suffix}{ext.lower()}"

def get_client_ip() -> str:
    """Get client IP address from request, handling proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or 'unknown'

def get_user_agent() -> str:
    """Get user agent from request"""
    return request.headers.get('User-Agent', 'unknown')

def validate_ticket_data(data: Dict[str, Any]) -> Dict[str, Union[bool, List[str]]]:
    """Validate ticket creation/update data"""
    errors = []
    
    # Title validation
    title = data.get('title', '').strip()
    if not title:
        errors.append("Title is required")
    elif len(title) < 5:
        errors.append("Title must be at least 5 characters long")
    elif len(title) > 150:
        errors.append("Title must be less than 150 characters")
    
    # Description validation
    description = data.get('description', '').strip()
    if not description:
        errors.append("Description is required")
    elif len(description) < 10:
        errors.append("Description must be at least 10 characters long")
    elif len(description) > 5000:
        errors.append("Description must be less than 5000 characters")
    
    # Priority validation
    priority = data.get('priority', '').strip()
    if priority and priority not in ['Low', 'Medium', 'High', 'Critical']:
        errors.append("Invalid priority value")
    
    # Status validation
    status = data.get('status', '').strip()
    if status and status not in ['Open', 'In Progress', 'Pending', 'Resolved', 'Closed', 'Cancelled']:
        errors.append("Invalid status value")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def validate_client_ticket_data(data: Dict[str, Any]) -> Dict[str, Union[bool, List[str]]]:
    """Validate client ticket submission data"""
    errors = []
    
    # Name validation
    name = data.get('name', '').strip()
    if not name:
        errors.append("Name is required")
    elif len(name) < 2:
        errors.append("Name must be at least 2 characters long")
    elif len(name) > 64:
        errors.append("Name must be less than 64 characters")
    
    # Surname validation
    surname = data.get('surname', '').strip()
    if not surname:
        errors.append("Surname is required")
    elif len(surname) < 2:
        errors.append("Surname must be at least 2 characters long")
    elif len(surname) > 64:
        errors.append("Surname must be less than 64 characters")
    
    # Email validation
    email = data.get('email', '').strip()
    if not email:
        errors.append("Email is required")
    elif not validate_email_address(email):
        errors.append("Invalid email address")
    
    # Phone validation
    phone = data.get('phone', '').strip()
    if not phone:
        errors.append("Phone is required")
    elif not validate_phone(phone):
        errors.append("Invalid phone number")
    
    # Description validation
    description = data.get('description', '').strip()
    if not description:
        errors.append("Description is required")
    elif len(description) < 10:
        errors.append("Description must be at least 10 characters long")
    elif len(description) > 2000:
        errors.append("Description must be less than 2000 characters")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def rate_limit_key(identifier: str, endpoint: str) -> str:
    """Generate rate limiting key"""
    return f"rate_limit:{endpoint}:{identifier}"

def calculate_sla_dates(created_at: datetime, response_hours: int = None, resolution_hours: int = None) -> Dict[str, Optional[datetime]]:
    """Calculate SLA due dates"""
    result = {
        'response_due': None,
        'resolution_due': None
    }
    
    if response_hours:
        result['response_due'] = created_at + timedelta(hours=response_hours)
    
    if resolution_hours:
        result['resolution_due'] = created_at + timedelta(hours=resolution_hours)
    
    return result

def format_time_ago(dt: datetime) -> str:
    """Format datetime as 'time ago' string"""
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 2592000:  # 30 days
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return dt.strftime("%Y-%m-%d")

def paginate_query(query, page: int = 1, per_page: int = 20, max_per_page: int = 100):
    """Paginate SQLAlchemy query with validation"""
    # Validate parameters
    page = max(1, int(page))
    per_page = min(max_per_page, max(1, int(per_page)))
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    items = query.offset(offset).limit(per_page).all()
    
    # Calculate pagination info
    has_prev = page > 1
    has_next = offset + per_page < total
    total_pages = (total + per_page - 1) // per_page
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_page': page - 1 if has_prev else None,
        'next_page': page + 1 if has_next else None
    }

def clean_search_term(term: str) -> str:
    """Clean and sanitize search terms"""
    if not term:
        return ""
    
    # Remove special characters that could be used for SQL injection
    cleaned = re.sub(r'[^\w\s-.]', '', term.strip())
    
    # Limit length
    return cleaned[:100]

def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """Mask sensitive data like email addresses or phone numbers"""
    if not data or len(data) <= visible_chars:
        return data
    
    if '@' in data:  # Email
        username, domain = data.split('@', 1)
        if len(username) > visible_chars:
            masked_username = username[:2] + mask_char * (len(username) - visible_chars) + username[-2:]
        else:
            masked_username = username
        return f"{masked_username}@{domain}"
    else:  # Phone or other
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)

def generate_ticket_number() -> str:
    """Generate a unique ticket number"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_part = secrets.token_hex(3).upper()
    return f"TKT-{timestamp}-{random_part}"
