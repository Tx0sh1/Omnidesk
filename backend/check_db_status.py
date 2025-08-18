#!/usr/bin/env python3
"""
Check current database schema status
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_status():
    try:
        from app import create_app, db
        import sqlalchemy as sa
        
        app = create_app()
        
        with app.app_context():
            print("=== Database Status Check ===")
            
            # Check if database file exists
            db_path = os.path.join(os.path.dirname(__file__), 'app.db')
            if os.path.exists(db_path):
                print(f"✅ Database file exists: {db_path}")
            else:
                print(f"❌ Database file not found: {db_path}")
                return
            
            # Check database connection
            try:
                inspector = sa.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"✅ Database connection successful")
                print(f"📋 Current tables: {tables}")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return
            
            # Check user table schema
            if 'user' in tables:
                print("\n=== User Table Analysis ===")
                user_columns = inspector.get_columns('user')
                existing_cols = [col['name'] for col in user_columns]
                print(f"Current columns: {existing_cols}")
                
                expected_cols = [
                    'id', 'username', 'email', 'password_hash', 'about_me', 
                    'last_seen', 'is_admin', 'is_active', 'created_at', 
                    'phone', 'department', 'job_title', 'timezone', 'email_notifications'
                ]
                
                missing_cols = [col for col in expected_cols if col not in existing_cols]
                extra_cols = [col for col in existing_cols if col not in expected_cols]
                
                if missing_cols:
                    print(f"❌ Missing columns: {missing_cols}")
                else:
                    print("✅ All expected columns present")
                
                if extra_cols:
                    print(f"ℹ️  Extra columns: {extra_cols}")
            else:
                print("❌ User table not found")
            
            # Check other important tables
            expected_tables = ['user', 'ticket', 'client_ticket', 'token_blacklist']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"\n❌ Missing tables: {missing_tables}")
            else:
                print(f"\n✅ All basic tables present")
            
            # Try to query user table to see what fails
            print("\n=== Testing User Query ===")
            try:
                from app.models import User
                user_count = db.session.scalar(sa.select(sa.func.count(User.id)))
                print(f"✅ User query successful. Found {user_count} users.")
            except Exception as e:
                print(f"❌ User query failed: {e}")
                print("This is likely the source of the login/registration failures.")
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_database_status()
