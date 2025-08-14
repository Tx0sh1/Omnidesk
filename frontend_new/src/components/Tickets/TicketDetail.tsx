import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ticketsAPI, usersAPI, Ticket, User } from '../../services/api';
import { 
  ArrowLeft, 
  Edit, 
  Save, 
  X, 
  Send,
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  User as UserIcon,
  Mail,
  Phone,
  Calendar
} from 'lucide-react';

const TicketDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    title: '',
    description: '',
    status: '',
    priority: '',
    assigned_to_id: '',
  });
  const [replyMessage, setReplyMessage] = useState('');
  const [sendingReply, setSendingReply] = useState(false);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (id) {
      fetchTicketAndUsers();
    }
  }, [id]);

  const fetchTicketAndUsers = async () => {
    try {
      setLoading(true);
      const [ticketResponse, usersResponse] = await Promise.all([
        ticketsAPI.getTicket(parseInt(id!)),
        usersAPI.getUsers()
      ]);
      
      const ticketData = ticketResponse.data;
      setTicket(ticketData);
      setUsers(usersResponse.data.users);
      
      // Initialize edit data
      setEditData({
        title: ticketData.title,
        description: ticketData.description,
        status: ticketData.status,
        priority: ticketData.priority,
        assigned_to_id: ticketData.assigned_to?.id?.toString() || '',
      });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch ticket details');
    } finally {
      setLoading(false);
    }
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setEditData({
      ...editData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSaveEdit = async () => {
    if (!ticket) return;

    setUpdating(true);
    try {
      const updateData = {
        title: editData.title,
        description: editData.description,
        status: editData.status,
        priority: editData.priority,
        assigned_to_id: editData.assigned_to_id ? parseInt(editData.assigned_to_id) : 0,
      };

      await ticketsAPI.updateTicket(ticket.id, updateData);
      await fetchTicketAndUsers(); // Refresh data
      setIsEditing(false);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update ticket');
    } finally {
      setUpdating(false);
    }
  };

  const handleCancelEdit = () => {
    if (!ticket) return;
    
    setEditData({
      title: ticket.title,
      description: ticket.description,
      status: ticket.status,
      priority: ticket.priority,
      assigned_to_id: ticket.assigned_to?.id?.toString() || '',
    });
    setIsEditing(false);
  };

  const handleSendReply = async () => {
    if (!ticket || !replyMessage.trim()) return;

    setSendingReply(true);
    try {
      await ticketsAPI.replyToTicket(ticket.id, replyMessage.trim());
      setReplyMessage('');
      // Show success message or refresh data
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to send reply');
    } finally {
      setSendingReply(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'in progress':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'resolved':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'closed':
        return <XCircle className="h-5 w-5 text-gray-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'bg-red-100 text-red-800';
      case 'in progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'closed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading ticket details...</p>
        </div>
      </div>
    );
  }

  if (error && !ticket) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/tickets')}
            className="btn btn-primary"
          >
            Back to Tickets
          </button>
        </div>
      </div>
    );
  }

  if (!ticket) {
    return null;
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/tickets')}
            className="mr-4 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Ticket #{ticket.id}</h1>
            <p className="text-gray-600 mt-2">Created {new Date(ticket.created_at).toLocaleDateString()}</p>
          </div>
        </div>
        
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Edit className="h-5 w-5" />
            <span>Edit</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Ticket Details */}
          <div className="card">
            {isEditing ? (
              <div className="space-y-4">
                <div>
                  <label className="form-label">Title</label>
                  <input
                    type="text"
                    name="title"
                    className="form-input"
                    value={editData.title}
                    onChange={handleEditChange}
                  />
                </div>
                
                <div>
                  <label className="form-label">Description</label>
                  <textarea
                    name="description"
                    rows={6}
                    className="form-input"
                    value={editData.description}
                    onChange={handleEditChange}
                  />
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={handleCancelEdit}
                    className="btn btn-secondary flex items-center space-x-2"
                    disabled={updating}
                  >
                    <X className="h-4 w-4" />
                    <span>Cancel</span>
                  </button>
                  <button
                    onClick={handleSaveEdit}
                    className="btn btn-primary flex items-center space-x-2"
                    disabled={updating}
                  >
                    {updating ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    <span>Save Changes</span>
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">{ticket.title}</h2>
                <div className="prose max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
                </div>
              </div>
            )}
          </div>

          {/* Client Information */}
          {ticket.client_info && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Client Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">Name</p>
                  <p className="text-gray-900">{ticket.client_info.name} {ticket.client_info.surname}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Email</p>
                  <p className="text-gray-900 flex items-center">
                    <Mail className="h-4 w-4 mr-2 text-gray-400" />
                    {ticket.client_info.email}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Phone</p>
                  <p className="text-gray-900 flex items-center">
                    <Phone className="h-4 w-4 mr-2 text-gray-400" />
                    {ticket.client_info.phone}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Reply Section */}
          {ticket.client_info && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Send Reply to Client</h3>
              <div className="space-y-4">
                <textarea
                  rows={4}
                  className="form-input"
                  placeholder="Type your reply message..."
                  value={replyMessage}
                  onChange={(e) => setReplyMessage(e.target.value)}
                />
                <div className="flex justify-end">
                  <button
                    onClick={handleSendReply}
                    className="btn btn-primary flex items-center space-x-2"
                    disabled={sendingReply || !replyMessage.trim()}
                  >
                    {sendingReply ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                    <span>Send Reply</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status and Priority */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Ticket Status</h3>
            
            {isEditing ? (
              <div className="space-y-4">
                <div>
                  <label className="form-label">Status</label>
                  <select
                    name="status"
                    className="form-input"
                    value={editData.status}
                    onChange={handleEditChange}
                  >
                    <option value="Open">Open</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Resolved">Resolved</option>
                    <option value="Closed">Closed</option>
                  </select>
                </div>
                
                <div>
                  <label className="form-label">Priority</label>
                  <select
                    name="priority"
                    className="form-input"
                    value={editData.priority}
                    onChange={handleEditChange}
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                  </select>
                </div>
                
                <div>
                  <label className="form-label">Assigned To</label>
                  <select
                    name="assigned_to_id"
                    className="form-input"
                    value={editData.assigned_to_id}
                    onChange={handleEditChange}
                  >
                    <option value="">Unassigned</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.username}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Status</p>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(ticket.status)}`}>
                    {getStatusIcon(ticket.status)}
                    <span className="ml-2">{ticket.status}</span>
                  </span>
                </div>
                
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">Priority</p>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(ticket.priority)}`}>
                    {ticket.priority}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Assignment */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Assignment</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-500">Created By</p>
                <div className="flex items-center mt-1">
                  {ticket.created_by ? (
                    <>
                      <UserIcon className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-gray-900">{ticket.created_by.username}</span>
                    </>
                  ) : (
                    <span className="text-gray-500 italic">Client Submission</span>
                  )}
                </div>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500">Assigned To</p>
                <div className="flex items-center mt-1">
                  {ticket.assigned_to ? (
                    <>
                      <UserIcon className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-gray-900">{ticket.assigned_to.username}</span>
                    </>
                  ) : (
                    <span className="text-gray-500 italic">Unassigned</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Timestamps */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Created</p>
                  <p className="text-sm text-gray-500">
                    {new Date(ticket.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 rounded-md p-4 max-w-sm">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-sm text-red-600">{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default TicketDetail;
