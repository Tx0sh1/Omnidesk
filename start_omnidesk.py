#!/usr/bin/env python3
"""
OmniDesk Quick Start Script
Run this from the project root to set up and start OmniDesk
"""

import os
import sys
import subprocess
import time
import threading
import argparse
import shutil
from pathlib import Path

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}")

def print_step(text):
    print(f"\n🔧 {text}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def run_command(command, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, cwd=cwd, shell=shell, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def check_python():
    """Check if Python 3.8+ is available"""
    print_step("Checking Python version...")
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print_success(f"Python {version.major}.{version.minor} detected")
            return True
        else:
            print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
            return False
    except:
        print_error("Python not found")
        return False

def check_node():
    """Check if Node.js is available"""
    print_step("Checking Node.js...")
    success, output = run_command("node --version")
    if success:
        print_success(f"Node.js detected: {output.strip()}")
        return True
    else:
        print_error("Node.js not found. Please install Node.js 14+")
        return False

def setup_backend():
    """Set up the backend"""
    print_header("BACKEND SETUP")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_error("Backend directory not found")
        return False
    
    # Check if virtual environment exists
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print_step("Creating virtual environment...")
        success, output = run_command("python -m venv venv", cwd=backend_dir)
        if not success:
            print_error(f"Failed to create virtual environment: {output}")
            return False
        print_success("Virtual environment created")
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        activate_script = venv_dir / "Scripts" / "activate"
        pip_cmd = str(venv_dir / "Scripts" / "pip")
        python_cmd = str(venv_dir / "Scripts" / "python")
    else:  # Unix-like
        activate_script = venv_dir / "bin" / "activate"
        pip_cmd = str(venv_dir / "bin" / "pip")
        python_cmd = str(venv_dir / "bin" / "python")
    
    # Install requirements
    print_step("Installing Python dependencies...")
    success, output = run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir)
    if not success:
        print_error(f"Failed to install dependencies: {output}")
        return False
    print_success("Dependencies installed")
    
    # Run migrations
    print_step("Setting up database...")
    success, output = run_command(f"{python_cmd} run_migrations.py", cwd=backend_dir)
    if success:
        print_success("Database migrations completed")
    else:
        print_warning(f"Migration script had issues: {output}")
        print_step("Trying Flask CLI migration...")
        success, output = run_command(f"{python_cmd} -m flask db upgrade", cwd=backend_dir)
        if success:
            print_success("Database migrations completed via Flask CLI")
        else:
            print_error(f"Database migration failed: {output}")
            return False
    
    # Test backend setup
    print_step("Testing backend setup...")
    success, output = run_command(f"{python_cmd} test_setup.py", cwd=backend_dir)
    if success:
        print_success("Backend setup verification passed")
    else:
        print_warning(f"Backend setup test had issues: {output}")
    
    return True

def setup_frontend(force_reinstall=False):
    """Set up the frontend"""
    print_header("FRONTEND SETUP")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_error("Frontend directory not found")
        return False
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    package_lock = frontend_dir / "package-lock.json"
    
    should_install = False
    
    if not node_modules.exists():
        print_step("Installing Node.js dependencies...")
        should_install = True
    elif force_reinstall:
        print_step("Force reinstalling Node.js dependencies...")
        should_install = True
    else:
        # Check if critical Tailwind packages are correctly installed
        tailwind_postcss_path = node_modules / "@tailwindcss" / "postcss"
        old_tailwind_path = node_modules / "tailwindcss"
        
        if old_tailwind_path.exists() and tailwind_postcss_path.exists():
            print_warning("Detected conflicting Tailwind CSS packages. Cleaning up...")
            should_install = True
        elif not tailwind_postcss_path.exists():
            print_warning("@tailwindcss/postcss not found. Reinstalling dependencies...")
            should_install = True
        else:
            print_success("Node.js dependencies already installed and verified")
    
    if should_install:
        # Clean install to avoid conflicts
        if node_modules.exists():
            print_step("Cleaning existing node_modules...")
            try:
                shutil.rmtree(node_modules)
                print_success("Cleaned node_modules directory")
            except Exception as e:
                print_warning(f"Could not clean node_modules: {e}")
        
        if package_lock.exists():
            print_step("Removing package-lock.json for clean install...")
            try:
                package_lock.unlink()
                print_success("Removed package-lock.json")
            except Exception as e:
                print_warning(f"Could not remove package-lock.json: {e}")
        
        success, output = run_command("npm install", cwd=frontend_dir)
        if not success:
            print_error(f"Failed to install Node dependencies: {output}")
            if "tailwindcss" in output.lower() and "postcss" in output.lower():
                print_warning("This appears to be a Tailwind CSS PostCSS configuration issue.")
                print_warning("Try running: npm install --force")
            return False
        print_success("Node.js dependencies installed")
        
        # Verify critical packages are installed
        tailwind_postcss_path = node_modules / "@tailwindcss" / "postcss"
        if not tailwind_postcss_path.exists():
            print_error("@tailwindcss/postcss was not installed correctly")
            return False
        
        old_tailwind_path = node_modules / "tailwindcss"
        if old_tailwind_path.exists():
            print_warning("Warning: Old tailwindcss package is still present")
            print_warning("This may cause PostCSS plugin conflicts")
    
    # Check if .env exists
    env_file = frontend_dir / ".env"
    if not env_file.exists():
        print_step("Creating frontend .env file...")
        with open(env_file, 'w') as f:
            f.write("REACT_APP_API_URL=http://localhost:5000/api\n")
        print_success("Frontend .env file created")
    
    return True

def start_backend():
    """Start the backend server"""
    print_step("Starting backend server...")
    
    backend_dir = Path("backend")
    venv_dir = backend_dir / "venv"
    
    if os.name == 'nt':  # Windows
        python_cmd = str(venv_dir / "Scripts" / "python")
    else:  # Unix-like
        python_cmd = str(venv_dir / "bin" / "python")
    
    # Start Flask server
    env = os.environ.copy()
    env['FLASK_APP'] = 'omnidesk.py'
    env['FLASK_ENV'] = 'development'
    
    process = subprocess.Popen(
        [python_cmd, '-m', 'flask', 'run'],
        cwd=backend_dir,
        env=env
    )
    
    print_success("Backend server starting on http://localhost:5000")
    return process

def start_frontend():
    """Start the frontend server"""
    print_step("Starting frontend server...")
    
    frontend_dir = Path("frontend")
    
    process = subprocess.Popen(
        ['npm', 'start'],
        cwd=frontend_dir
    )
    
    print_success("Frontend server starting on http://localhost:3000")
    return process

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description='OmniDesk Quick Start Script')
    parser.add_argument('--force-frontend-reinstall', action='store_true', 
                       help='Force reinstall frontend dependencies')
    args = parser.parse_args()
    
    print_header("OMNIDESK QUICK START")
    
    # Check prerequisites
    if not check_python():
        sys.exit(1)
    
    if not check_node():
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print_error("Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend(force_reinstall=args.force_frontend_reinstall):
        print_error("Frontend setup failed")
        print_warning("Try running with --force-frontend-reinstall flag")
        sys.exit(1)
    
    print_header("STARTING SERVERS")
    
    # Start backend
    backend_process = start_backend()
    time.sleep(3)  # Give backend time to start
    
    # Start frontend
    frontend_process = start_frontend()
    
    print_header("OMNIDESK IS STARTING!")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:5000")
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Wait for processes
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print_error("Backend server stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print_error("Frontend server stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for clean shutdown
        backend_process.wait(timeout=5)
        frontend_process.wait(timeout=5)
        
        print_success("Servers stopped successfully")

if __name__ == '__main__':
    main()
