# Civic Issues Reporter - Frontend

A simple web application for citizens to report civic issues in their community.

## 🌟 Features

- **Phone-based Authentication**: Login using phone number + OTP verification
- **Issue Reporting**: Report civic issues with photos, categories, and locations
- **Issue Management**: View and track your reported issues
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Live status updates for reported issues

## 🏗️ Structure

```
frontend/
├── index.html          # Login page with phone/OTP authentication
├── css/
│   ├── style.css       # Main styling and layout
│   └── auth.css        # Authentication-specific styles
├── js/
│   └── app.js          # Main application logic
├── pages/
│   ├── dashboard.html  # User dashboard with issue reporting
│   └── test.html       # API testing interface
└── assets/            # Images and other static assets
```

## 🚀 Getting Started

### Prerequisites

1. **Backend Running**: Make sure the FastAPI backend is running on port 8002
2. **Python**: For serving static files

### Running the Frontend

1. **Start HTTP Server**:
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```

2. **Open in Browser**:
   - Main App: http://localhost:3000
   - API Testing: http://localhost:3000/pages/test.html

### For Development

If you want to use a different backend URL, update the `baseURL` in:
- `/js/app.js` (line 4)
- `/pages/test.html` (line 119)

## 📱 User Flow

### 1. Authentication
1. Enter 10-digit phone number
2. Receive OTP via SMS (Twilio)
3. Enter 6-digit OTP to login
4. Automatic redirect to dashboard

### 2. Reporting Issues
1. Fill out issue form:
   - Title (required)
   - Description (required)
   - Category (Roads, Water, etc.)
   - Priority (Low, Medium, High)
   - Location (required)
   - Photo (optional, max 5MB)
2. Submit to create issue
3. View in "My Issues" section

### 3. Issue Management
- View all your reported issues
- See status updates (Pending, In Progress, Resolved, Rejected)
- Access uploaded photos
- Track submission dates

## 🎨 Styling

### CSS Architecture
- **style.css**: Main layout, components, responsive design
- **auth.css**: Authentication flow specific styles

### Design System
- **Colors**: Green primary (#4CAF50), professional grays
- **Typography**: System fonts, clean hierarchy
- **Components**: Cards, buttons, forms with consistent styling
- **Responsive**: Mobile-first approach with flexbox/grid

## 🧪 Testing

Use the **Test Page** (`/pages/test.html`) to:

1. **Backend Health**: Test server connectivity
2. **S3 Health**: Verify file upload service
3. **Send OTP**: Test SMS functionality
4. **Verify OTP**: Test authentication flow
5. **Create Issue**: Test issue creation
6. **List Issues**: Test data retrieval

## 🔧 Configuration

### Backend URL
Update these files if backend URL changes:
```javascript
// js/app.js
this.baseURL = 'http://localhost:8002';

// pages/test.html
const BASE_URL = 'http://localhost:8002';
```

### File Upload Limits
- Maximum file size: 5MB
- Supported formats: Images (jpg, png, gif, etc.)
- Storage: AWS S3

## 📊 API Integration

The frontend communicates with these backend endpoints:

### Authentication
- `POST /auth/send-otp` - Send OTP to phone
- `POST /auth/verify-otp` - Verify OTP and get token

### Issues
- `POST /users/issues` - Create new issue
- `GET /users/my-issues` - Get user's issues

### Health Checks
- `GET /health` - Backend health
- `GET /s3/health` - S3 service health

## 🔐 Security

- **JWT Tokens**: Stored in localStorage
- **Authorization Headers**: Bearer token for API calls
- **Input Validation**: Client-side form validation
- **File Security**: Size limits and type checking

## 📱 Browser Compatibility

- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile**: iOS Safari, Chrome Mobile
- **Features**: ES6+, Fetch API, FormData, localStorage

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure backend allows frontend origin
2. **OTP Not Received**: Check Twilio configuration
3. **File Upload Fails**: Verify S3 credentials and bucket permissions
4. **Login Issues**: Clear localStorage and try again

### Debug Mode

Open browser dev tools and check:
- Console for JavaScript errors
- Network tab for API responses
- Application tab for localStorage data

## 🚀 Deployment

For production deployment:

1. **Build Process**: Minify CSS/JS files
2. **CDN**: Serve static assets from CDN
3. **HTTPS**: Use secure connections
4. **Environment**: Update API URLs for production
5. **Caching**: Configure proper cache headers

## 📞 Support

For issues or questions:
1. Check the test page for API connectivity
2. Verify backend logs for errors
3. Check browser console for frontend issues
4. Ensure all environment variables are set correctly
