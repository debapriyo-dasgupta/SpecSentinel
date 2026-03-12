# SpecSentinel Frontend

Modern web-based frontend for the SpecSentinel API Health Analyzer.

## 📋 Overview

This frontend provides an intuitive interface to analyze OpenAPI specifications using the SpecSentinel backend API. Users can upload specification files or paste them directly to receive comprehensive health reports with security, design, error handling, documentation, and governance analysis.

## 🎨 Features

- **Dual Input Methods**
  - 📁 File Upload (drag & drop or browse)
  - 📝 Direct Paste (YAML or JSON)

- **Interactive Results**
  - 🎯 Visual health score with animated ring chart
  - 📊 Category breakdown with progress bars
  - 🔍 Filterable findings by severity
  - 💡 Priority recommendations

- **Export Options**
  - 📄 JSON format
  - 📝 Text report

- **Modern UI/UX**
  - Responsive design
  - Smooth animations
  - Clean, professional interface
  - Real-time feedback

## 🚀 Quick Start

### Prerequisites

1. **Backend Server Running**
   ```bash
   # From project root
   cd src/api
   python app.py
   ```
   The backend should be running at `http://localhost:8000`

2. **Modern Web Browser**
   - Chrome, Firefox, Safari, or Edge (latest versions)

### Running the Frontend

#### Option 1: Simple HTTP Server (Python)

```bash
# Navigate to frontend directory
cd frontend

# Python 3
python -m http.server 8080

# Open browser
# Navigate to: http://localhost:8080
```

#### Option 2: Node.js HTTP Server

```bash
# Install http-server globally (one time)
npm install -g http-server

# Navigate to frontend directory
cd frontend

# Start server
http-server -p 8080

# Open browser
# Navigate to: http://localhost:8080
```

#### Option 3: VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

#### Option 4: Direct File Access

Simply open `frontend/index.html` in your browser. Note: Some features may be limited due to CORS restrictions.

## 📁 Project Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   └── styles.css      # All styles and animations
├── js/
│   └── app.js          # Application logic and API integration
├── assets/             # Images and other assets (optional)
└── README.md           # This file
```

## 🔧 Configuration

### API Endpoint

The frontend connects to the backend API at `http://localhost:8000` by default.

To change this, edit `frontend/js/app.js`:

```javascript
// Line 7
const API_BASE_URL = 'http://localhost:8000';

// Change to your backend URL, e.g.:
const API_BASE_URL = 'https://your-backend-url.com';
```

### CORS Configuration

If you encounter CORS issues, ensure the backend has CORS enabled (already configured in `src/api/app.py`):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📖 Usage Guide

### 1. Upload File Method

1. Click the "Upload File" tab (default)
2. Drag and drop your OpenAPI spec file, or click "Choose File"
3. Supported formats: `.yaml`, `.yml`, `.json`
4. Click "Analyze Specification"
5. Wait for analysis to complete
6. Review results and recommendations

### 2. Paste Spec Method

1. Click the "Paste Spec" tab
2. Paste your OpenAPI specification (YAML or JSON format)
3. Optionally provide a name for your spec
4. Click "Analyze Specification"
5. Wait for analysis to complete
6. Review results and recommendations

### 3. Understanding Results

#### Health Score
- **86-100 (Excellent ✅)**: Best practices followed
- **71-85 (Good 🟢)**: Minor issues, mostly compliant
- **41-70 (Moderate 🟡)**: Some issues, needs improvement
- **0-40 (Poor 🔴)**: Critical issues, major gaps

#### Severity Levels
- **Critical**: Immediate action required
- **High**: Should be addressed soon
- **Medium**: Important but not urgent
- **Low**: Nice to have improvements

#### Category Breakdown
- **Security (35%)**: Authentication, authorization, data protection
- **Design (20%)**: RESTful practices, versioning, naming
- **Error Handling (15%)**: Standardized errors, RFC 7807
- **Documentation (15%)**: Descriptions, examples, clarity
- **Governance (15%)**: Metadata, licensing, deprecation

### 4. Filtering Findings

Use the filter buttons to view findings by severity:
- **All**: Show all findings
- **Critical**: Show only critical issues
- **High**: Show only high-priority issues
- **Medium**: Show only medium-priority issues
- **Low**: Show only low-priority issues

### 5. Exporting Reports

- **Export JSON**: Download full report in JSON format
- **Export Text Report**: Download human-readable text report
- **Analyze New Spec**: Clear results and start over

## 🎨 Customization

### Changing Colors

Edit `frontend/css/styles.css` to customize the color scheme:

```css
:root {
    --primary-color: #0f62fe;      /* Main brand color */
    --success-color: #24a148;      /* Success/Excellent */
    --warning-color: #f1c21b;      /* Warning/Moderate */
    --danger-color: #da1e28;       /* Danger/Poor */
    /* ... more colors ... */
}
```

### Modifying Layout

The layout uses CSS Grid and Flexbox for responsiveness. Key breakpoint:

```css
@media (max-width: 768px) {
    /* Mobile styles */
}
```

## 🐛 Troubleshooting

### Backend Connection Issues

**Problem**: "Failed to analyze specification. Please check if the backend server is running."

**Solution**:
1. Ensure backend is running: `python src/api/app.py`
2. Check backend is accessible at `http://localhost:8000`
3. Test backend health: `curl http://localhost:8000/health`
4. Check browser console for CORS errors

### File Upload Not Working

**Problem**: File upload doesn't trigger analysis

**Solution**:
1. Check file format (must be `.yaml`, `.yml`, or `.json`)
2. Ensure file is valid OpenAPI specification
3. Check browser console for errors
4. Try the "Paste Spec" method instead

### Results Not Displaying

**Problem**: Analysis completes but results don't show

**Solution**:
1. Check browser console for JavaScript errors
2. Ensure backend returned valid JSON response
3. Try refreshing the page
4. Clear browser cache

### CORS Errors

**Problem**: Browser blocks API requests due to CORS

**Solution**:
1. Ensure backend CORS middleware is enabled
2. Use a proper HTTP server (not file:// protocol)
3. Check browser console for specific CORS error
4. In development, use `allow_origins=["*"]` in backend

## 🔒 Security Notes

### Production Deployment

When deploying to production:

1. **Update CORS Settings**
   ```python
   # In src/api/app.py
   allow_origins=["https://your-frontend-domain.com"]
   ```

2. **Use HTTPS**
   - Serve frontend over HTTPS
   - Ensure backend API uses HTTPS

3. **API Authentication**
   - Consider adding API key authentication
   - Implement rate limiting

4. **Input Validation**
   - Backend validates all inputs
   - Frontend provides user-friendly error messages

## 📱 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🚀 Performance

- **Initial Load**: < 1 second
- **Analysis Time**: 2-15 seconds (depends on spec size)
- **File Size Limit**: Determined by backend (typically 10MB)

## 📝 API Endpoints Used

The frontend interacts with these backend endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check backend status |
| `/analyze` | POST | Upload file for analysis |
| `/analyze/text` | POST | Send spec as JSON body |

## 🎓 Development

### Adding New Features

1. **HTML**: Add markup to `index.html`
2. **CSS**: Add styles to `css/styles.css`
3. **JavaScript**: Add logic to `js/app.js`

### Code Structure

```javascript
// js/app.js structure
- Configuration (API_BASE_URL)
- State Management (currentReport, currentFile)
- DOM Elements (cached references)
- Event Listeners (initialization)
- Core Functions (analyze, display, export)
- Utility Functions (helpers)
```

## 📄 License

Part of the SpecSentinel project - IBM Hackathon 2026

## 🤝 Contributing

This is a hackathon project. For improvements:
1. Test thoroughly
2. Follow existing code style
3. Update documentation
4. Ensure backward compatibility

## 📞 Support

For issues or questions:
- Check backend logs: `src/api/app.py` console output
- Check browser console: F12 → Console tab
- Review backend API documentation
- Test backend endpoints directly with curl/Postman

---

**Last Updated**: 2026-03-12  
**Version**: 1.0.0  
**Status**: Production Ready ✅