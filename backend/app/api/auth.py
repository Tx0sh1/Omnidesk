from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from werkzeug.security import check_password_hash
from app.api import bp
from app.models import User
from app import db
import sqlalchemy as sa
from app.email import send_password_reset_email

@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400
    
    user = db.session.scalar(sa.select(User).where(User.username == data['username']))
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Update last seen
        user.last_seen = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': getattr(user, 'is_admin', False)
            }
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'message': 'Username, email, and password required'}), 400
    
    if db.session.scalar(sa.select(User).where(User.username == data['username'])):
        return jsonify({'message': 'Username already exists'}), 400
    
    if db.session.scalar(sa.select(User).where(User.email == data['email'])):
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'User created successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': getattr(user, 'is_admin', False)
        }
    }), 201

@bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_token}), 200

@bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'about_me': getattr(user, 'about_me', ''),
        'last_seen': user.last_seen.isoformat() if user.last_seen else None,
        'is_admin': getattr(user, 'is_admin', False)
    }), 200

@bp.route('/auth/reset-password-request', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'message': 'Email required'}), 400
    
    user = db.session.scalar(sa.select(User).where(User.email == data['email']))
    if user:
        send_password_reset_email(user)
    
    # Always return success for security
    return jsonify({'message': 'If your email is registered, you will receive reset instructions'}), 200

@bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    if not data or not data.get('token') or not data.get('password'):
        return jsonify({'message': 'Token and new password required'}), 400
    
    user = User.verify_reset_password_token(data['token'])
    if not user:
        return jsonify({'message': 'Invalid or expired token'}), 400
    
    user.set_password(data['password'])
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'}), 200
