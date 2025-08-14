import axios, { AxiosResponse } from 'axios';

// Get API URL from environment variable
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` },
          });
          
          const newToken = response.data.access_token;
          localStorage.setItem('access_token', newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          
          return api.request(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Types for API responses
export interface User {
  id: number;
  username: string;
  email: string;
  about_me?: string;
  last_seen?: string;
  is_admin?: boolean;
}

export interface Ticket {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
  created_by?: {
    id: number;
    username: string;
  };
  assigned_to?: {
    id: number;
    username: string;
  };
  client_info?: {
    name: string;
    surname: string;
    email: string;
    phone: string;
    images: string[];
  };
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface TicketsResponse {
  tickets: Ticket[];
}

export interface UsersResponse {
  users: User[];
}

// Authentication API
export const authAPI = {
  login: (username: string, password: string): Promise<AxiosResponse<LoginResponse>> =>
    api.post('/auth/login', { username, password }),
    
  register: (username: string, email: string, password: string): Promise<AxiosResponse<LoginResponse>> =>
    api.post('/auth/register', { username, email, password }),
    
  logout: (): Promise<AxiosResponse<{ message: string }>> =>
    api.post('/auth/logout'),
    
  getCurrentUser: (): Promise<AxiosResponse<User>> =>
    api.get('/auth/me'),
    
  refreshToken: (): Promise<AxiosResponse<{ access_token: string }>> =>
    api.post('/auth/refresh'),
};

// Tickets API
export const ticketsAPI = {
  getTickets: (): Promise<AxiosResponse<TicketsResponse>> =>
    api.get('/tickets'),
    
  createTicket: (ticketData: {
    title: string;
    description: string;
    priority?: string;
    assigned_to_id?: number;
  }): Promise<AxiosResponse<{ message: string; ticket: Ticket }>> =>
    api.post('/tickets', ticketData),
    
  getTicket: (id: number): Promise<AxiosResponse<Ticket>> =>
    api.get(`/tickets/${id}`),
    
  updateTicket: (id: number, ticketData: {
    title?: string;
    description?: string;
    status?: string;
    priority?: string;
    assigned_to_id?: number;
  }): Promise<AxiosResponse<{ message: string; ticket: Ticket }>> =>
    api.put(`/tickets/${id}`, ticketData),
    
  replyToTicket: (id: number, message: string): Promise<AxiosResponse<{ message: string }>> =>
    api.post(`/tickets/${id}/reply`, { message }),
};

// Users API
export const usersAPI = {
  getUsers: (): Promise<AxiosResponse<UsersResponse>> =>
    api.get('/users'),
    
  getProfile: (): Promise<AxiosResponse<User>> =>
    api.get('/users/profile'),
    
  updateProfile: (profileData: {
    username?: string;
    email?: string;
    about_me?: string;
  }): Promise<AxiosResponse<{ message: string; user: User }>> =>
    api.put('/users/profile', profileData),
    
  getUserByUsername: (username: string): Promise<AxiosResponse<User>> =>
    api.get(`/users/${username}`),
};

// Client API (public endpoints)
export const clientAPI = {
  submitTicket: (ticketData: FormData): Promise<AxiosResponse<{
    message: string;
    ticket_id: number;
    reference_number: string;
  }>> =>
    axios.post(`${API_BASE_URL}/client/submit-ticket`, ticketData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
    
  getTicketStatus: (referenceNumber: string): Promise<AxiosResponse<{
    reference_number: string;
    status: string;
    submitted_at: string;
    description: string;
  }>> =>
    axios.get(`${API_BASE_URL}/client/ticket-status/${referenceNumber}`),
};

export default api;
