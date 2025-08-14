import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { LogOut, User, Ticket } from 'lucide-react';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-blue-600 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center">
              <Ticket className="h-8 w-8 text-white mr-2" />
              <span className="text-white text-xl font-bold">OmniDesk</span>
            </Link>
            <div className="hidden md:ml-6 md:flex md:space-x-8">
              <Link
                to="/tickets"
                className="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium"
              >
                My Tickets
              </Link>
              <Link
                to="/tickets/new"
                className="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium"
              >
                New Ticket
              </Link>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {user && (
              <>
                <Link
                  to="/profile"
                  className="text-white hover:text-blue-200 flex items-center space-x-1"
                >
                  <User className="h-5 w-5" />
                  <span className="hidden md:block">{user.username}</span>
                </Link>
                <button
                  onClick={logout}
                  className="text-white hover:text-blue-200 flex items-center space-x-1"
                >
                  <LogOut className="h-5 w-5" />
                  <span className="hidden md:block">Logout</span>
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;