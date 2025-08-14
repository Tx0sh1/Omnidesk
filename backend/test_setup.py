#!/usr/bin/env python3
"""
Comprehensive test script to verify OmniDesk setup
Run this script to check if everything is properly configured.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        from flask_sqlalchemy import SQLAlchemy
        print("✅ Flask-SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ Flask-SQLAlchemy import failed: {e}")
        return False
    
    try:
        from flask_migrate import Migrate
        print("✅ Flask-Migrate imported successfully")
    except ImportError as e:
        print(f"❌ Flask-Migrate import failed: {e}")
        return False
    
    try:
        from flask_jwt_extended import JWTManager
        print("✅ Flask-JWT-Extended imported successfully")
    except ImportError as e:
        print(f"❌ Flask-JWT-Extended import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test Flask app creation"""
    print("\n🔍 Testing Flask app creation...")
    
    try:
        from app import create_app, db
        app = create_app()
        print("✅ Flask app created successfully")
        
        with app.app_context():
            print("✅ App context working")
            
            # Test database connection
            try:
                db.engine.connect()
                print("✅ Database connection successful")
            except Exception as e:
                print(f"⚠️  Database connection issue: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def test_models():
    """Test database models"""
    print("\n🔍 Testing database models...")
    
    try:
        from app import create_app, db
        from app.models import User, Ticket, ClientTicket, TokenBlacklist
        
        app = create_app()
        with app.app_context():
            # Test model creation
            print("✅ User model imported")
            print("✅ Ticket model imported")
            print("✅ ClientTicket model imported")
            print("✅ TokenBlacklist model imported")
            
            # Test table creation
            db.create_all()
            print("✅ Database tables created/verified")
            
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def test_jwt_config():
    """Test JWT configuration"""
    print("\n🔍 Testing JWT configuration...")
    
    try:
        from app import create_app
        from flask_jwt_extended import create_access_token
        
        app = create_app()
        with app.app_context():
            # Test token creation
            token = create_access_token(identity=1)
            print("✅ JWT token creation successful")
            
        return True
    except Exception as e:
        print(f"❌ JWT configuration test failed: {e}")
        return False

def test_api_blueprints():
    """Test API blueprint registration"""
    print("\n🔍 Testing API blueprints...")
    
    try:
        from app import create_app
        app = create_app()
        
        # Check if blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        if 'api' in blueprint_names:
            print("✅ API blueprint registered")
        else:
            print("❌ API blueprint not found")
            return False
            
        if 'main' in blueprint_names:
            print("✅ Main blueprint registered")
        else:
            print("❌ Main blueprint not found")
            return False
            
        if 'errors' in blueprint_names:
            print("✅ Errors blueprint registered")
        else:
            print("❌ Errors blueprint not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Blueprint test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment configuration...")
    
    try:
        from config import Config
        
        # Check required config values
        config = Config()
        
        if hasattr(config, 'SECRET_KEY') and config.SECRET_KEY:
            print("✅ SECRET_KEY configured")
        else:
            print("❌ SECRET_KEY not configured")
            
        if hasattr(config, 'SQLALCHEMY_DATABASE_URI') and config.SQLALCHEMY_DATABASE_URI:
            print("✅ Database URI configured")
        else:
            print("❌ Database URI not configured")
            
        if hasattr(config, 'JWT_SECRET_KEY') and config.JWT_SECRET_KEY:
            print("✅ JWT_SECRET_KEY configured")
        else:
            print("❌ JWT_SECRET_KEY not configured")
        
        return True
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== OmniDesk Setup Verification ===\n")
    
    tests = [
        test_imports,
        test_environment,
        test_app_creation,
        test_models,
        test_jwt_config,
        test_api_blueprints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! OmniDesk is properly configured.")
        print("\nNext steps:")
        print("1. Run database migrations: python run_migrations.py")
        print("2. Create admin user: python setup_admin.py")
        print("3. Start the server: flask run")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
