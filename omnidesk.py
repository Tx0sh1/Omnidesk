import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

try:
    from app import create_app, db
    from app.models import User, Ticket, ClientTicket
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed all dependencies and the backend directory contains the Flask app.")
    sys.exit(1)

try:
    app = create_app()
except Exception as e:
    print(f"Error creating Flask app: {e}")
    sys.exit(1)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Ticket': Ticket,
        'ClientTicket': ClientTicket
    }

if __name__ == '__main__':
    app.run(debug=True)
