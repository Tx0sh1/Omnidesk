import React, { useState, useEffect } from 'react';
import { 
  Tag, 
  Plus, 
  Edit2, 
  Trash2, 
  Save, 
  X, 
  Clock, 
  AlertCircle,
  CheckCircle,
  TrendingUp,
  Settings,
  Eye,
  BarChart3
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface Category {
  id: number;
  name: string;
  description?: string;
  color: string;
  is_active: boolean;
  sla_response_hours: number;
  sla_resolution_hours: number;
  ticket_counts?: {
    total: number;
    open: number;
    in_progress: number;
    resolved: number;
    closed: number;
  };
  detailed_stats?: {
    status_counts: Record<string, number>;
    priority_counts: Record<string, number>;
    total_tickets: number;
  };
  recent_tickets?: Array<{
    id: number;
    title: string;
    status: string;
    priority: string;
    created_at: string;
    created_by: string;
  }>;
}

const CategoryManager: React.FC = () => {
  const { user } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#3B82F6',
    sla_response_hours: 24,
    sla_resolution_hours: 72,
    is_active: true
  });

  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/categories', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCategories(data.categories || []);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to load categories');
      }
    } catch (err) {
      setError('Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategoryDetails = async (categoryId: number) => {
    try {
      const response = await fetch(`/api/categories/${categoryId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const category = await response.json();
        setSelectedCategory(category);
      }
    } catch (err) {
      console.error('Failed to fetch category details:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Category name is required');
      return;
    }

    try {
      setSubmitting(true);
      setError('');

      const url = editingId ? `/api/categories/${editingId}` : '/api/categories';
      const method = editingId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const data = await response.json();
        
        if (editingId) {
          setCategories(categories.map(c => c.id === editingId ? data.category : c));
          setEditingId(null);
        } else {
          setCategories([...categories, data.category]);
          setShowCreateForm(false);
        }
        
        resetForm();
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to save category');
      }
    } catch (err) {
      setError('Failed to save category');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (categoryId: number) => {
    if (!confirm('Are you sure you want to deactivate this category?')) return;

    try {
      const response = await fetch(`/api/categories/${categoryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        setCategories(categories.map(c => 
          c.id === categoryId ? { ...c, is_active: false } : c
        ));
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to delete category');
      }
    } catch (err) {
      setError('Failed to delete category');
    }
  };

  const startEdit = (category: Category) => {
    setFormData({
      name: category.name,
      description: category.description || '',
      color: category.color,
      sla_response_hours: category.sla_response_hours,
      sla_resolution_hours: category.sla_resolution_hours,
      is_active: category.is_active
    });
    setEditingId(category.id);
    setShowCreateForm(false);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      color: '#3B82F6',
      sla_response_hours: 24,
      sla_resolution_hours: 72,
      is_active: true
    });
    setEditingId(null);
    setShowCreateForm(false);
  };

  const colorOptions = [
    { value: '#3B82F6', name: 'Blue' },
    { value: '#EF4444', name: 'Red' },
    { value: '#10B981', name: 'Green' },
    { value: '#F59E0B', name: 'Yellow' },
    { value: '#8B5CF6', name: 'Purple' },
    { value: '#EC4899', name: 'Pink' },
    { value: '#14B8A6', name: 'Teal' },
    { value: '#F97316', name: 'Orange' }
  ];

  if (!user?.is_admin) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Access Denied</h3>
          <p className="text-gray-600">You need admin privileges to manage categories.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
          <span className="ml-4 text-gray-600">Loading categories...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
            <div className="bg-gradient-to-r from-purple-500 to-indigo-500 text-white p-2 rounded-lg">
              <Tag className="h-6 w-6" />
            </div>
            <span>Category Management</span>
          </h1>
          <p className="text-gray-600 mt-2">Organize tickets and configure SLA settings</p>
        </div>
        
        <button
          onClick={() => {
            resetForm();
            setShowCreateForm(true);
          }}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>New Category</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-sm text-red-600">{error}</span>
            <button
              onClick={() => setError('')}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Categories List */}
        <div className="lg:col-span-2">
          {/* Create/Edit Form */}
          {(showCreateForm || editingId) && (
            <div className="card mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">
                  {editingId ? 'Edit Category' : 'Create Category'}
                </h3>
                <button
                  onClick={resetForm}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Name *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="form-input"
                      placeholder="Category name"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="form-label">Color</label>
                    <div className="flex items-center space-x-2">
                      <select
                        value={formData.color}
                        onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                        className="form-input"
                      >
                        {colorOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.name}
                          </option>
                        ))}
                      </select>
                      <div
                        className="w-8 h-8 rounded border-2 border-gray-300"
                        style={{ backgroundColor: formData.color }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="form-label">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="form-input"
                    rows={3}
                    placeholder="Category description (optional)"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">SLA Response Hours</label>
                    <input
                      type="number"
                      min="1"
                      max="8760"
                      value={formData.sla_response_hours}
                      onChange={(e) => setFormData({ ...formData, sla_response_hours: parseInt(e.target.value) || 24 })}
                      className="form-input"
                    />
                    <p className="text-sm text-gray-500 mt-1">Time to first response</p>
                  </div>
                  
                  <div>
                    <label className="form-label">SLA Resolution Hours</label>
                    <input
                      type="number"
                      min="1"
                      max="8760"
                      value={formData.sla_resolution_hours}
                      onChange={(e) => setFormData({ ...formData, sla_resolution_hours: parseInt(e.target.value) || 72 })}
                      className="form-input"
                    />
                    <p className="text-sm text-gray-500 mt-1">Time to resolution</p>
                  </div>
                </div>

                <div className="flex items-center">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      className="form-checkbox"
                    />
                    <span className="ml-2 text-sm text-gray-700">Active</span>
                  </label>
                </div>

                <div className="flex items-center space-x-3 pt-4">
                  <button
                    type="submit"
                    className="btn btn-primary flex items-center space-x-2"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    <span>{submitting ? 'Saving...' : 'Save Category'}</span>
                  </button>
                  
                  <button
                    type="button"
                    onClick={resetForm}
                    className="btn btn-secondary"
                    disabled={submitting}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Categories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {categories.map((category) => (
              <div
                key={category.id}
                className={`card hover:shadow-md transition-shadow duration-200 ${
                  !category.is_active ? 'opacity-60' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: category.color }}
                    ></div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{category.name}</h4>
                      {!category.is_active && (
                        <span className="text-xs text-gray-500">Inactive</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => fetchCategoryDetails(category.id)}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded"
                      title="View details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => startEdit(category)}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded"
                      title="Edit category"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    {category.is_active && (
                      <button
                        onClick={() => handleDelete(category.id)}
                        className="p-1 text-gray-400 hover:text-red-600 rounded"
                        title="Deactivate category"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>

                {category.description && (
                  <p className="text-sm text-gray-600 mb-3">{category.description}</p>
                )}

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Response SLA:</span>
                    <div className="flex items-center mt-1">
                      <Clock className="h-3 w-3 text-gray-400 mr-1" />
                      <span className="font-medium">{category.sla_response_hours}h</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500">Resolution SLA:</span>
                    <div className="flex items-center mt-1">
                      <Clock className="h-3 w-3 text-gray-400 mr-1" />
                      <span className="font-medium">{category.sla_resolution_hours}h</span>
                    </div>
                  </div>
                </div>

                {category.ticket_counts && (
                  <div className="mt-4 pt-3 border-t border-gray-200">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Total Tickets:</span>
                      <span className="font-medium">{category.ticket_counts.total}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-red-600">Open:</span>
                        <span>{category.ticket_counts.open}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-yellow-600">In Progress:</span>
                        <span>{category.ticket_counts.in_progress}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {categories.length === 0 && (
            <div className="text-center py-12">
              <Tag className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No categories found</h3>
              <p className="text-gray-600 mb-4">Create your first category to get started</p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="btn btn-primary"
              >
                Create Category
              </button>
            </div>
          )}
        </div>

        {/* Category Details Sidebar */}
        <div className="lg:col-span-1">
          {selectedCategory ? (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Category Details</h3>
                <button
                  onClick={() => setSelectedCategory(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-6 h-6 rounded-full"
                    style={{ backgroundColor: selectedCategory.color }}
                  ></div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{selectedCategory.name}</h4>
                    {selectedCategory.description && (
                      <p className="text-sm text-gray-600">{selectedCategory.description}</p>
                    )}
                  </div>
                </div>

                {selectedCategory.detailed_stats && (
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2 flex items-center">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Statistics
                    </h5>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Total Tickets:</span>
                        <span className="font-medium">{selectedCategory.detailed_stats.total_tickets}</span>
                      </div>
                      
                      {Object.entries(selectedCategory.detailed_stats.status_counts).map(([status, count]) => (
                        <div key={status} className="flex justify-between pl-4">
                          <span className="text-gray-600">{status}:</span>
                          <span>{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedCategory.recent_tickets && selectedCategory.recent_tickets.length > 0 && (
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2">Recent Tickets</h5>
                    <div className="space-y-2">
                      {selectedCategory.recent_tickets.slice(0, 5).map((ticket) => (
                        <div key={ticket.id} className="p-2 bg-gray-50 rounded text-sm">
                          <div className="font-medium text-gray-900 truncate">{ticket.title}</div>
                          <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
                            <span>{ticket.created_by}</span>
                            <span className={`px-2 py-1 rounded ${
                              ticket.status === 'Open' ? 'bg-red-100 text-red-800' :
                              ticket.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {ticket.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="card">
              <div className="text-center py-8">
                <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Select a category to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CategoryManager;
