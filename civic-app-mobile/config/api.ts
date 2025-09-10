// API Configuration for Civic App
// Connects to FastAPI backend

// Get your local IP address by running: ip addr show | grep inet
const API_BASE_URL = __DEV__ 
  ? 'http://192.168.1.38:8000'  // Development - your local IP
  : 'https://your-production-api.com';  // Production URL

console.log('API_BASE_URL:', API_BASE_URL); // Debug log

export default API_BASE_URL;

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  REQUEST_OTP: '/auth/login',  // Updated to match backend
  SEND_OTP: '/auth/send-otp',  // Alternative endpoint
  VERIFY_OTP: '/auth/verify-otp',
  LOGOUT: '/auth/logout',
  
  // User endpoints
  USER_PROFILE: '/users/profile',
  REPORT_ISSUE: '/users/report-issue',
  UPLOAD_FILE: '/users/upload-file',
  USER_ISSUES: '/users/issues',
  
  // Admin endpoints (if user is admin)
  ADMIN_ISSUES: '/admin/issues',
  ADMIN_USERS: '/admin/users',
  ADMIN_ISSUE_DETAIL: '/admin/issues', // /{issue_id}
  ADMIN_UPDATE_STATUS: '/admin/issues', // /{issue_id}/status
};

// HTTP client configuration
export const API_CONFIG = {
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};
