import os
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from app.models import User, Ticket, ClientTicket
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're in the backend directory and all dependencies are installed.")
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
