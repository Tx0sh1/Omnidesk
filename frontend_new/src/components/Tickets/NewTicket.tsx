import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ticketsAPI, usersAPI, User } from '../../services/api';
import { ArrowLeft, Save, AlertCircle } from 'lucide-react';

const NewTicket: React.FC = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'Medium',
    assigned_to_id: '',
  });
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await usersAPI.getUsers();
      setUsers(response.data.users);
    } catch (err: any) {
      console.error('Failed to fetch users:', err);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    // Clear messages when user starts typing
    if (error) setError('');
    if (success) setSuccess('');
  };

  const validateForm = () => {
    if (!formData.title.trim()) {
      setError('Title is required');
      return false;
    }
    if (!formData.description.trim()) {
      setError('Description is required');
      return false;
    }
    if (formData.title.length < 5) {
      setError('Title must be at least 5 characters long');
      return false;
    }
    if (formData.description.length < 10) {
      setError('Description must be at least 10 characters long');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const ticketData = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        priority: formData.priority,
        assigned_to_id: formData.assigned_to_id ? parseInt(formData.assigned_to_id) : undefined,
      };

      const response = await ticketsAPI.createTicket(ticketData);
      setSuccess('Ticket created successfully!');
      
      // Redirect to ticket list after a short delay
      setTimeout(() => {
        navigate('/tickets');
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create ticket');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/tickets');
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center mb-8">
        <button
          onClick={handleBack}
          className="mr-4 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create New Ticket</h1>
          <p className="text-gray-600 mt-2">Fill out the form below to create a new support ticket</p>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="title" className="form-label">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              name="title"
              required
              className="form-input"
              placeholder="Enter a descriptive title for your ticket"
              value={formData.title}
              onChange={handleChange}
            />
            {formData.title.length > 0 && formData.title.length < 5 && (
              <p className="mt-1 text-sm text-red-600">Title must be at least 5 characters</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="form-label">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              id="description"
              name="description"
              rows={6}
              required
              className="form-input"
              placeholder="Provide a detailed description of the issue or request"
              value={formData.description}
              onChange={handleChange}
            />
            {formData.description.length > 0 && formData.description.length < 10 && (
              <p className="mt-1 text-sm text-red-600">Description must be at least 10 characters</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              Characters: {formData.description.length}
            </p>
          </div>

          {/* Priority and Assignment Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Priority */}
            <div>
              <label htmlFor="priority" className="form-label">
                Priority
              </label>
              <select
                id="priority"
                name="priority"
                className="form-input"
                value={formData.priority}
                onChange={handleChange}
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>

            {/* Assigned To */}
            <div>
              <label htmlFor="assigned_to_id" className="form-label">
                Assign To (Optional)
              </label>
              <select
                id="assigned_to_id"
                name="assigned_to_id"
                className="form-input"
                value={formData.assigned_to_id}
                onChange={handleChange}
              >
                <option value="">Unassigned</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.username} ({user.email})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Messages */}
          {error && (
            <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-md">
              <AlertCircle className="h-5 w-5" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {success && (
            <div className="flex items-center space-x-2 text-green-600 bg-green-50 p-3 rounded-md">
              <AlertCircle className="h-5 w-5" />
              <span className="text-sm">{success}</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handleBack}
              className="btn btn-secondary"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary flex items-center space-x-2"
              disabled={loading}
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <Save className="h-5 w-5" />
                  <span>Create Ticket</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Tips */}
      <div className="mt-6 card bg-blue-50 border-blue-200">
        <h3 className="text-lg font-medium text-blue-900 mb-2">Tips for Creating Effective Tickets</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Use a clear, descriptive title that summarizes the issue</li>
          <li>• Provide step-by-step details in the description</li>
          <li>• Include any error messages or screenshots if applicable</li>
          <li>• Set the appropriate priority based on urgency and impact</li>
          <li>• Assign to a specific team member if you know who should handle it</li>
        </ul>
      </div>
    </div>
  );
};

export default NewTicket;
