import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { clientAPI } from '../../services/api';
import { 
  Search, 
  AlertCircle, 
  CheckCircle,
  Clock,
  XCircle,
  Ticket,
  Calendar,
  FileText
} from 'lucide-react';

interface TicketStatus {
  reference_number: string;
  status: string;
  submitted_at: string;
  description: string;
}

const ClientStatus: React.FC = () => {
  const [referenceNumber, setReferenceNumber] = useState('');
  const [ticketStatus, setTicketStatus] = useState<TicketStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!referenceNumber.trim()) {
      setError('Please enter a reference number');
      return;
    }

    setLoading(true);
    setError('');
    setTicketStatus(null);

    try {
      const response = await clientAPI.getTicketStatus(referenceNumber.trim());
      setTicketStatus(response.data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Ticket not found. Please check your reference number.');
      } else {
        setError(err.response?.data?.message || 'Failed to fetch ticket status');
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return <AlertCircle className="h-6 w-6 text-red-500" />;
      case 'in progress':
        return <Clock className="h-6 w-6 text-yellow-500" />;
      case 'resolved':
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case 'closed':
        return <XCircle className="h-6 w-6 text-gray-500" />;
      default:
        return <AlertCircle className="h-6 w-6 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'in progress':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'resolved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'closed':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusMessage = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'Your ticket has been received and is waiting to be assigned to a team member.';
      case 'in progress':
        return 'A team member is currently working on your ticket.';
      case 'resolved':
        return 'Your ticket has been resolved. If you need further assistance, please submit a new ticket.';
      case 'closed':
        return 'Your ticket has been closed. If you need further assistance, please submit a new ticket.';
      default:
        return 'Your ticket is being processed.';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-600 text-white p-3 rounded-full">
              <Search className="h-8 w-8" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Track Your Ticket</h1>
          <p className="text-gray-600 mt-2">
            Enter your reference number to check the status of your support ticket.
          </p>
        </div>

        {/* Search Form */}
        <div className="card mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="referenceNumber" className="form-label">
                Reference Number
              </label>
              <input
                type="text"
                id="referenceNumber"
                className="form-input"
                placeholder="Enter your reference number (e.g., CT000001)"
                value={referenceNumber}
                onChange={(e) => setReferenceNumber(e.target.value.toUpperCase())}
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                The reference number was provided when you submitted your ticket.
              </p>
            </div>

            {error && (
              <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-md">
                <AlertCircle className="h-5 w-5" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary flex items-center justify-center space-x-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <Search className="h-5 w-5" />
                  <span>Check Status</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Ticket Status */}
        {ticketStatus && (
          <div className="card">
            <div className="text-center mb-6">
              <div className="flex justify-center mb-4">
                {getStatusIcon(ticketStatus.status)}
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Ticket {ticketStatus.reference_number}
              </h2>
              <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${getStatusColor(ticketStatus.status)}`}>
                {ticketStatus.status}
              </div>
            </div>

            <div className="space-y-6">
              {/* Status Message */}
              <div className="text-center">
                <p className="text-gray-600">
                  {getStatusMessage(ticketStatus.status)}
                </p>
              </div>

              {/* Ticket Details */}
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Ticket Details</h3>
                
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <Calendar className="h-5 w-5 text-gray-400 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Submitted</p>
                      <p className="text-sm text-gray-600">{formatDate(ticketStatus.submitted_at)}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <FileText className="h-5 w-5 text-gray-400 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Description</p>
                      <p className="text-sm text-gray-600">{ticketStatus.description}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Status Timeline */}
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Status Timeline</h3>
                
                <div className="flow-root">
                  <ul className="-mb-8">
                    <li>
                      <div className="relative pb-8">
                        <div className="relative flex space-x-3">
                          <div>
                            <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                              <Ticket className="h-4 w-4 text-white" />
                            </span>
                          </div>
                          <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                            <div>
                              <p className="text-sm text-gray-500">Ticket submitted</p>
                            </div>
                            <div className="text-right text-sm whitespace-nowrap text-gray-500">
                              {formatDate(ticketStatus.submitted_at)}
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                    
                    {ticketStatus.status.toLowerCase() !== 'open' && (
                      <li>
                        <div className="relative pb-8">
                          <div className="relative flex space-x-3">
                            <div>
                              <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                                ticketStatus.status.toLowerCase() === 'in progress' ? 'bg-yellow-500' :
                                ticketStatus.status.toLowerCase() === 'resolved' ? 'bg-green-500' :
                                'bg-gray-500'
                              }`}>
                                {getStatusIcon(ticketStatus.status)}
                              </span>
                            </div>
                            <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                              <div>
                                <p className="text-sm text-gray-500">Status updated to {ticketStatus.status}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Help Links */}
        <div className="text-center mt-8 space-y-2">
          <p className="text-sm text-gray-600">
            Need to submit a new ticket?{' '}
            <Link to="/client/submit" className="font-medium text-blue-600 hover:text-blue-500">
              Submit a ticket
            </Link>
          </p>
          <p className="text-sm text-gray-600">
            Have an account?{' '}
            <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ClientStatus;
