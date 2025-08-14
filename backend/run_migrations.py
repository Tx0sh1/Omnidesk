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
        
        app = create_app()
        
        with app.app_context():
            # Check if migrations directory exists
            migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
            
            if not os.path.exists(migrations_dir):
                print("Initializing migrations...")
                init()
                print("✅ Migrations initialized")
            
            print("Running database upgrade...")
            upgrade()
            print("✅ Database upgraded successfully")
            
            # Create tables if they don't exist
            db.create_all()
            print("✅ All database tables created/verified")
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the backend directory")
        print("2. Ensure virtual environment is activated")
        print("3. Verify all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == '__main__':
    print("=== OmniDesk Database Migration ===")
    run_migrations()
