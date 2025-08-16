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
        {/* Enhanced Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-2xl shadow-lg hover-scale">
              <Search className="h-12 w-12" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Track Your Ticket
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Enter your reference number to check the status of your support ticket and get real-time updates.
          </p>
          <div className="flex justify-center mt-6 space-x-8 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Real-time Updates</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Instant Status</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>24/7 Tracking</span>
            </div>
          </div>
        </div>

        {/* Enhanced Search Form */}
        <div className="card shadow-xl mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="referenceNumber" className="form-label flex items-center space-x-2">
                <Ticket className="h-4 w-4" />
                <span>Reference Number</span>
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="referenceNumber"
                  className="form-input pl-12 text-lg font-mono tracking-wider"
                  placeholder="CT000001"
                  value={referenceNumber}
                  onChange={(e) => {
                    setReferenceNumber(e.target.value.toUpperCase());
                    if (error) setError('');
                  }}
                  required
                />
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Ticket className="h-5 w-5 text-gray-400" />
                </div>
              </div>
              <p className="form-help">
                The reference number was provided when you submitted your ticket (e.g., CT000001)
              </p>
            </div>

            {error && (
              <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-4 rounded-lg border border-red-200 animate-fade-in">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full text-lg py-3 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Searching...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <Search className="h-5 w-5" />
                  <span>Check Status</span>
                </div>
              )}
            </button>
          </form>
        </div>

        {/* Enhanced Ticket Status */}
        {ticketStatus && (
          <div className="card shadow-xl animate-fade-in">
            <div className="text-center mb-8">
              <div className="flex justify-center mb-6">
                <div className="bg-white p-4 rounded-full shadow-lg border-4 border-gray-100 hover-scale">
                  {getStatusIcon(ticketStatus.status)}
                </div>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Ticket #{ticketStatus.reference_number}
              </h2>
              <div className={`inline-flex items-center px-6 py-3 rounded-full text-lg font-semibold border-2 shadow-sm ${getStatusColor(ticketStatus.status)}`}>
                {ticketStatus.status.toUpperCase()}
              </div>
            </div>

            <div className="space-y-8">
              {/* Enhanced Status Message */}
              <div className="text-center bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
                <p className="text-lg text-gray-700 font-medium">
                  {getStatusMessage(ticketStatus.status)}
                </p>
              </div>

              {/* Enhanced Ticket Details */}
              <div className="border-t border-gray-200 pt-8">
                <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                  <FileText className="h-5 w-5" />
                  <span>Ticket Details</span>
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 p-4 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="bg-blue-100 p-2 rounded-lg">
                        <Calendar className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">Submitted</p>
                        <p className="text-sm text-gray-600">{formatDate(ticketStatus.submitted_at)}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="bg-green-100 p-2 rounded-lg">
                        <Ticket className="h-5 w-5 text-green-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">Reference</p>
                        <p className="text-sm text-gray-600 font-mono">{ticketStatus.reference_number}</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6 bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <div className="bg-purple-100 p-2 rounded-lg flex-shrink-0 mt-1">
                      <FileText className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 mb-2">Issue Description</p>
                      <p className="text-gray-700 leading-relaxed">{ticketStatus.description}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Enhanced Status Timeline */}
              <div className="border-t border-gray-200 pt-8">
                <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                  <Clock className="h-5 w-5" />
                  <span>Status Timeline</span>
                </h3>
                
                <div className="flow-root">
                  <ul className="-mb-8">
                    <li>
                      <div className="relative pb-8">
                        <div className="absolute top-5 left-5 -ml-px h-full w-0.5 bg-gray-200"></div>
                        <div className="relative flex items-start space-x-3">
                          <div>
                            <span className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white shadow-lg">
                              <Ticket className="h-5 w-5 text-white" />
                            </span>
                          </div>
                          <div className="min-w-0 flex-1 py-0">
                            <div className="text-sm text-gray-500">
                              <div className="font-medium text-gray-900">Ticket Submitted</div>
                              <div className="mt-1">Your support request was received and logged into our system.</div>
                            </div>
                            <div className="mt-2 text-sm text-gray-500">
                              <time>{formatDate(ticketStatus.submitted_at)}</time>
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                    
                    {ticketStatus.status.toLowerCase() !== 'open' && (
                      <li>
                        <div className="relative pb-8">
                          <div className="relative flex items-start space-x-3">
                            <div>
                              <span className={`h-10 w-10 rounded-full flex items-center justify-center ring-8 ring-white shadow-lg ${
                                ticketStatus.status.toLowerCase() === 'in progress' ? 'bg-yellow-500' :
                                ticketStatus.status.toLowerCase() === 'resolved' ? 'bg-green-500' :
                                'bg-gray-500'
                              }`}>
                                {React.cloneElement(getStatusIcon(ticketStatus.status), { className: 'h-5 w-5 text-white' })}
                              </span>
                            </div>
                            <div className="min-w-0 flex-1 py-0">
                              <div className="text-sm text-gray-500">
                                <div className="font-medium text-gray-900">Status Updated</div>
                                <div className="mt-1">
                                  {ticketStatus.status.toLowerCase() === 'in progress' && 'A team member has been assigned and is working on your ticket.'}
                                  {ticketStatus.status.toLowerCase() === 'resolved' && 'Your issue has been resolved by our support team.'}
                                  {ticketStatus.status.toLowerCase() === 'closed' && 'Your ticket has been closed.'}
                                </div>
                              </div>
                              <div className="mt-2 text-sm text-gray-500">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(ticketStatus.status)}`}>
                                  {ticketStatus.status}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    )}
                  </ul>
                </div>
              </div>

              {/* Next Steps */}
              <div className="border-t border-gray-200 pt-8">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
                  <h4 className="font-bold text-gray-900 mb-3 flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-blue-600" />
                    <span>What's Next?</span>
                  </h4>
                  <div className="space-y-2 text-sm text-gray-700">
                    {ticketStatus.status.toLowerCase() === 'open' && (
                      <>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <span>Your ticket is in queue and will be assigned to a team member soon</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <span>You'll receive email updates when the status changes</span>
                        </div>
                      </>
                    )}
                    {ticketStatus.status.toLowerCase() === 'in progress' && (
                      <>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                          <span>Our team is actively working on your issue</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                          <span>You'll be notified once a solution is found</span>
                        </div>
                      </>
                    )}
                    {(ticketStatus.status.toLowerCase() === 'resolved' || ticketStatus.status.toLowerCase() === 'closed') && (
                      <>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span>If you need further assistance, please submit a new ticket</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span>Thank you for using our support system!</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Help Links */}
        <div className="text-center mt-12 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link 
              to="/client/submit" 
              className="card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 group text-center"
            >
              <div className="bg-blue-100 p-3 rounded-lg w-fit mx-auto mb-3 group-hover:scale-110 transition-transform duration-300">
                <Ticket className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Submit New Ticket</h3>
              <p className="text-sm text-gray-600">Need help with a different issue?</p>
            </Link>
            
            <Link 
              to="/login" 
              className="card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 group text-center"
            >
              <div className="bg-green-100 p-3 rounded-lg w-fit mx-auto mb-3 group-hover:scale-110 transition-transform duration-300">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Staff Login</h3>
              <p className="text-sm text-gray-600">Access the admin dashboard</p>
            </Link>
          </div>
          
          <div className="pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Need immediate assistance? Contact us at{' '}
              <a href="mailto:support@omnidesk.com" className="font-medium text-blue-600 hover:text-blue-800">
                support@omnidesk.com
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClientStatus;
