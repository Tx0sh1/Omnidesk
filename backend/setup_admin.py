#!/usr/bin/env python3
"""
Setup script to create an initial admin user for OmniDesk
Run this script after setting up the database to create your first admin user.
"""

from app import create_app, db
from app.models import User
import sys

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        print("=== OmniDesk Admin User Setup ===")
        
        # Check if any admin users exist
        existing_admin = db.session.query(User).filter_by(is_admin=True).first()
        if existing_admin:
            print(f"Admin user '{existing_admin.username}' already exists.")
            response = input("Do you want to create another admin user? (y/N): ")
            if response.lower() != 'y':
                print("Setup cancelled.")
                return
        
        # Get user input
        while True:
            username = input("Enter admin username: ").strip()
            if username:
                existing_user = db.session.query(User).filter_by(username=username).first()
                if existing_user:
                    print("Username already exists. Please choose another.")
                    continue
                break
            print("Username cannot be empty.")
        
        while True:
            email = input("Enter admin email: ").strip()
            if email and '@' in email:
                existing_email = db.session.query(User).filter_by(email=email).first()
                if existing_email:
                    print("Email already exists. Please choose another.")
                    continue
                break
            print("Please enter a valid email address.")
        
        while True:
            password = input("Enter admin password: ").strip()
            if len(password) >= 6:
                break
            print("Password must be at least 6 characters long.")
        
        # Create admin user
        try:
            admin_user = User(
                username=username,
                email=email,
                is_admin=True
            )
            admin_user.set_password(password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"\n✅ Admin user '{username}' created successfully!")
            print(f"Email: {email}")
            print("You can now log in to the system with these credentials.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating admin user: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    create_admin_user()
