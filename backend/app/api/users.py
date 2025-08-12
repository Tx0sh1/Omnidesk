from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models import User
from app import db
import sqlalchemy as sa

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (for assignment dropdown)"""
    users = db.session.scalars(sa.select(User)).all()
    
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })
    
    return jsonify({'users': users_data}), 200

@bp.route('/users/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'about_me': getattr(user, 'about_me', ''),
        'last_seen': user.last_seen.isoformat() if user.last_seen else None
    }), 200

@bp.route('/users/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    data = request.get_json()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if 'username' in data:
        # Check if username is already taken
        existing_user = db.session.scalar(sa.select(User).where(User.username == data['username']))
        if existing_user and existing_user.id != user.id:
            return jsonify({'message': 'Username already exists'}), 400
        user.username = data['username']
    
    if 'email' in data:
        # Check if email is already taken
        existing_user = db.session.scalar(sa.select(User).where(User.email == data['email']))
        if existing_user and existing_user.id != user.id:
            return jsonify({'message': 'Email already exists'}), 400
        user.email = data['email']
    
    if 'about_me' in data:
        user.about_me = data['about_me']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'about_me': getattr(user, 'about_me', '')
        }
    }), 200

@bp.route('/users/<username>', methods=['GET'])
@jwt_required()
def get_user_by_username(username):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'about_me': getattr(user, 'about_me', ''),
        'last_seen': user.last_seen.isoformat() if user.last_seen else None
    }), 200