import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { clientAPI } from '../../services/api';
import { 
  Send, 
  Paperclip, 
  X, 
  AlertCircle, 
  CheckCircle,
  Ticket,
  Upload
} from 'lucide-react';

const ClientSubmit: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    surname: '',
    phone: '',
    email: '',
    description: '',
  });
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [referenceNumber, setReferenceNumber] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear messages when user starts typing
    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      const validFiles = droppedFiles.filter(file => {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['image/', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        
        if (file.size > maxSize) {
          setError(`File ${file.name} is too large. Maximum size is 10MB.`);
          return false;
        }
        
        if (!allowedTypes.some(type => file.type.startsWith(type))) {
          setError(`File ${file.name} is not supported. Please use images, PDF, or Word documents.`);
          return false;
        }
        
        return true;
      });
      
      setFiles(prev => [...prev, ...validFiles]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      const validFiles = selectedFiles.filter(file => {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['image/', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        
        if (file.size > maxSize) {
          setError(`File ${file.name} is too large. Maximum size is 10MB.`);
          return false;
        }
        
        if (!allowedTypes.some(type => file.type.startsWith(type))) {
          setError(`File ${file.name} is not supported. Please use images, PDF, or Word documents.`);
          return false;
        }
        
        return true;
      });
      
      setFiles(prev => [...prev, ...validFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const validateForm = () => {
    const requiredFields = ['name', 'surname', 'phone', 'email', 'description'];
    for (const field of requiredFields) {
      if (!formData[field as keyof typeof formData].trim()) {
        setError(`${field.charAt(0).toUpperCase() + field.slice(1)} is required`);
        return false;
      }
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }

    const phoneRegex = /^[\+]?[\d\s\-\(\)]{10,}$/;
    if (!phoneRegex.test(formData.phone)) {
      setError('Please enter a valid phone number');
      return false;
    }

    if (formData.description.length < 20) {
      setError('Description must be at least 20 characters long');
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
    setSuccess('');

    try {
      const formDataToSend = new FormData();
      
      // Add form fields
      Object.entries(formData).forEach(([key, value]) => {
        formDataToSend.append(key, value);
      });
      
      // Add files
      files.forEach((file, index) => {
        formDataToSend.append(`file_${index}`, file);
      });

      const response = await clientAPI.submitTicket(formDataToSend);
      
      setSuccess('Ticket submitted successfully!');
      setReferenceNumber(response.data.reference_number);
      
      // Reset form
      setFormData({
        name: '',
        surname: '',
        phone: '',
        email: '',
        description: '',
      });
      setFiles([]);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to submit ticket');
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Enhanced Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-2xl shadow-lg animate-bounce-gentle">
              <Ticket className="h-12 w-12" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Submit Support Ticket
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Need help? Submit a support ticket and we'll get back to you as soon as possible. 
            Our team typically responds within 24 hours.
          </p>
          <div className="flex justify-center mt-6 space-x-8 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>24/7 Support</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Quick Response</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Expert Team</span>
            </div>
          </div>
        </div>

        {success && referenceNumber ? (
          /* Enhanced Success Message */
          <div className="card shadow-xl animate-fade-in">
            <div className="text-center">
              <div className="bg-green-100 rounded-full p-4 w-fit mx-auto mb-6">
                <CheckCircle className="h-16 w-16 text-green-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Ticket Submitted Successfully!
              </h2>
              <p className="text-lg text-gray-600 mb-6 max-w-md mx-auto">
                Your support ticket has been created and assigned to our team. 
                Please save your reference number for tracking.
              </p>
              
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-8 border border-blue-200">
                <p className="text-sm font-medium text-gray-700 mb-2">Reference Number</p>
                <div className="flex items-center justify-center space-x-2">
                  <p className="text-3xl font-bold text-blue-600">{referenceNumber}</p>
                  <button
                    onClick={() => navigator.clipboard.writeText(referenceNumber)}
                    className="text-blue-600 hover:text-blue-800 p-1 rounded"
                    title="Copy to clipboard"
                  >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  Keep this number safe - you'll need it to track your ticket
                </p>
              </div>
              
              <div className="space-y-4">
                <Link
                  to="/client/status"
                  className="btn btn-primary w-full text-lg py-3 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
                >
                  Track Your Ticket
                </Link>
                <button
                  onClick={() => {
                    setSuccess('');
                    setReferenceNumber('');
                  }}
                  className="btn btn-secondary w-full text-lg py-3"
                >
                  Submit Another Ticket
                </button>
              </div>
              
              <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">What happens next?</h4>
                <div className="text-left space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span>Our team will review your ticket within 2 hours</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span>You'll receive updates via email</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span>Track progress using your reference number</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Form */
          <div className="card">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Personal Information */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="name" className="form-label">
                      First Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      required
                      className="form-input"
                      value={formData.name}
                      onChange={handleChange}
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="surname" className="form-label">
                      Last Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      id="surname"
                      name="surname"
                      required
                      className="form-input"
                      value={formData.surname}
                      onChange={handleChange}
                    />
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="email" className="form-label">
                      Email Address <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      required
                      className="form-input"
                      value={formData.email}
                      onChange={handleChange}
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="phone" className="form-label">
                      Phone Number <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="tel"
                      id="phone"
                      name="phone"
                      required
                      className="form-input"
                      value={formData.phone}
                      onChange={handleChange}
                    />
                  </div>
                </div>
              </div>

              {/* Issue Description */}
              <div>
                <label htmlFor="description" className="form-label">
                  Describe Your Issue <span className="text-red-500">*</span>
                </label>
                <textarea
                  id="description"
                  name="description"
                  rows={6}
                  required
                  className="form-input"
                  placeholder="Please provide a detailed description of your issue..."
                  value={formData.description}
                  onChange={handleChange}
                />
                <p className="mt-1 text-sm text-gray-500">
                  Minimum 20 characters. Current: {formData.description.length}
                </p>
              </div>

              {/* Enhanced File Attachments */}
              <div>
                <label className="form-label flex items-center space-x-2">
                  <Paperclip className="h-4 w-4" />
                  <span>Attachments (Optional)</span>
                </label>
                <div 
                  className={`mt-2 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-xl transition-all duration-200 ${
                    dragActive 
                      ? 'border-blue-400 bg-blue-50' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <div className="space-y-2 text-center">
                    <div className={`mx-auto h-16 w-16 rounded-full flex items-center justify-center transition-colors duration-200 ${
                      dragActive ? 'bg-blue-100' : 'bg-gray-100'
                    }`}>
                      <Upload className={`h-8 w-8 transition-colors duration-200 ${
                        dragActive ? 'text-blue-600' : 'text-gray-400'
                      }`} />
                    </div>
                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="file-upload"
                        className="relative cursor-pointer bg-white rounded-md font-semibold text-blue-600 hover:text-blue-800 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500 px-2 py-1 transition-colors duration-200"
                      >
                        <span>Upload files</span>
                        <input
                          id="file-upload"
                          name="file-upload"
                          type="file"
                          className="sr-only"
                          multiple
                          accept="image/*,.pdf,.doc,.docx"
                          onChange={handleFileChange}
                        />
                      </label>
                      <p className="pl-1">or drag and drop here</p>
                    </div>
                    <p className="text-xs text-gray-500">
                      Images, PDF, Word documents up to 10MB each
                    </p>
                    {files.length > 0 && (
                      <p className="text-xs text-blue-600 font-medium">
                        {files.length} file{files.length > 1 ? 's' : ''} selected
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Enhanced File List */}
                {files.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Selected Files:</h4>
                    {files.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-gradient-to-r from-gray-50 to-gray-100 px-4 py-3 rounded-lg border border-gray-200 hover:shadow-sm transition-shadow duration-200">
                        <div className="flex items-center space-x-3">
                          <div className="bg-blue-100 p-2 rounded-lg">
                            <Paperclip className="h-4 w-4 text-blue-600" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{file.name}</p>
                            <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFile(index)}
                          className="text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded-full transition-colors duration-200"
                          title="Remove file"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Messages */}
              {error && (
                <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-md">
                  <AlertCircle className="h-5 w-5" />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              {/* Submit Button */}
              <div className="pt-6 border-t border-gray-200">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full btn btn-primary flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Send className="h-5 w-5" />
                      <span>Submit Ticket</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Footer Links */}
        <div className="text-center mt-8">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
              Sign in here
            </Link>
          </p>
          <p className="text-sm text-gray-600 mt-2">
            Want to check your ticket status?{' '}
            <Link to="/client/status" className="font-medium text-blue-600 hover:text-blue-500">
              Track your ticket
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ClientSubmit;
