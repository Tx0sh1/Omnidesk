#!/usr/bin/env python3
"""
Standalone database migration script for OmniDesk
Use this if you're having issues with Flask CLI commands.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_migrations():
    try:
        from app import create_app, db
        from flask_migrate import upgrade, init, migrate
        import sqlalchemy as sa
        
        app = create_app()
        
        with app.app_context():
            # Check if migrations directory exists
            migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
            
            if not os.path.exists(migrations_dir):
                print("Initializing migrations...")
                init()
                print("✅ Migrations initialized")
            
            # Check current database state
            print("Checking current database schema...")
            inspector = sa.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Current tables: {tables}")
            
            if 'user' in tables:
                user_columns = [col['name'] for col in inspector.get_columns('user')]
                print(f"Current user table columns: {user_columns}")
                
                missing_columns = []
                expected_columns = ['is_active', 'phone', 'department', 'job_title', 'timezone', 'email_notifications', 'created_at']
                for col in expected_columns:
                    if col not in user_columns:
                        missing_columns.append(col)
                
                if missing_columns:
                    print(f"Missing user columns: {missing_columns}")
                else:
                    print("All expected user columns are present")
            
            print("\nRunning database upgrade...")
            upgrade()
            print("✅ Database upgraded successfully")
            
            # Verify the upgrade worked
            print("\nVerifying database schema after upgrade...")
            inspector = sa.inspect(db.engine)
            if 'user' in inspector.get_table_names():
                user_columns = [col['name'] for col in inspector.get_columns('user')]
                print(f"User table columns after upgrade: {user_columns}")
                
                # Check if is_active column now exists
                if 'is_active' in user_columns:
                    print("✅ is_active column successfully added")
                else:
                    print("❌ is_active column still missing")
            
            # Create tables if they don't exist
            db.create_all()
            print("✅ All database tables created/verified")
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Make sure you're in the backend directory")
        print("2. Ensure virtual environment is activated")
        print("3. Verify all dependencies are installed: pip install -r requirements.txt")
        print("4. Check if the database file has proper permissions")
        sys.exit(1)

if __name__ == '__main__':
    print("=== OmniDesk Database Migration ===")
    run_migrations()
