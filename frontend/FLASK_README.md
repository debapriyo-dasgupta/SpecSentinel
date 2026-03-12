# SpecSentinel Frontend - Flask Application

Modern Flask-based web frontend for the SpecSentinel API Health Analyzer.

## 📋 Overview

This is a Flask application that serves the SpecSentinel web interface and acts as a proxy to the backend API. It provides a clean separation between frontend and backend, with proper routing and error handling.

## 🏗️ Architecture

```
frontend/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── templates/              # Jinja2 templates
│   └── index.html         # Main page template
├── static/                 # Static assets
│   ├── css/
│   │   └── styles.css     # Styles
│   └── js/
│       └── app.js         # Frontend JavaScript
├── README.md              # Original documentation
└── FLASK_README.md        # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

### 2. Start Backend API

In a separate terminal:
```bash
cd src/api
python app.py
```

Backend should be running at `http://localhost:8000`

### 3. Start Flask Frontend

```bash
cd frontend
python app.py
```

Frontend will be available at `http://localhost:5000`

### 4. Open Browser

Navigate to: `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# Backend API URL
BACKEND_API_URL=http://localhost:8000

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Production Configuration

For production deployment:

```env
BACKEND_API_URL=https://your-backend-api.com
FLASK_ENV=production
FLASK_DEBUG=False
```

## 📡 API Routes

The Flask app provides these routes:

### Frontend Routes
- `GET /` - Serve main page

### API Proxy Routes
- `GET /api/health` - Backend health check
- `GET /api/stats` - Backend statistics
- `POST /api/analyze` - Upload file for analysis
- `POST /api/analyze/text` - Analyze pasted spec
- `POST /api/refresh` - Trigger rule refresh

### Static Files
- `/static/<path>` - Serve CSS, JS, images

## 🎯 Features

### Proxy Benefits

1. **CORS Handling** - No cross-origin issues
2. **Error Handling** - Graceful error messages
3. **Request Forwarding** - Seamless backend integration
4. **Static Serving** - Efficient asset delivery
5. **Template Rendering** - Dynamic content with Jinja2

### Security

- Input validation on all endpoints
- Error sanitization
- Request size limits
- CORS protection

## 🚀 Deployment Options

### Option 1: Development Server

```bash
python app.py
```

### Option 2: Gunicorn (Production)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 3: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV BACKEND_API_URL=http://backend:8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t specsentinel-frontend .
docker run -p 5000:5000 -e BACKEND_API_URL=http://backend:8000 specsentinel-frontend
```

### Option 4: Docker Compose

Create `docker-compose.yml` in project root:
```yaml
version: '3.8'

services:
  backend:
    build: ./src/api
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "5000:5000"
    environment:
      - BACKEND_API_URL=http://backend:8000
    depends_on:
      - backend
```

Run:
```bash
docker-compose up
```

## 🔍 Troubleshooting

### Backend Connection Issues

**Error**: "Backend API error" or 503 responses

**Solution**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `BACKEND_API_URL` in environment
3. Check firewall/network settings

### Template Not Found

**Error**: "TemplateNotFound: index.html"

**Solution**:
1. Ensure `templates/` directory exists
2. Check `index.html` is in `templates/`
3. Run from `frontend/` directory

### Static Files Not Loading

**Error**: 404 on CSS/JS files

**Solution**:
1. Ensure `static/` directory structure is correct
2. Check file paths in `index.html`
3. Clear browser cache

### Port Already in Use

**Error**: "Address already in use"

**Solution**:
```bash
# Change port in app.py or use environment variable
export FLASK_RUN_PORT=5001
python app.py
```

## 📊 Performance

### Optimization Tips

1. **Enable Caching**
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

2. **Compress Responses**
   ```python
   from flask_compress import Compress
   Compress(app)
   ```

3. **Use CDN for Static Files**
   - Host CSS/JS on CDN
   - Update template URLs

4. **Production Server**
   - Use Gunicorn with multiple workers
   - Enable reverse proxy (Nginx)
   - Use HTTPS

## 🧪 Testing

### Test Backend Connection

```bash
curl http://localhost:5000/api/health
```

### Test File Upload

```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@../tests/sample_bad_spec.yaml"
```

### Test Text Analysis

```bash
curl -X POST http://localhost:5000/api/analyze/text \
  -H "Content-Type: application/json" \
  -d '{"spec": {"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0.0"}, "paths": {}}, "name": "test"}'
```

## 📝 Development

### Adding New Routes

```python
@app.route('/api/custom')
def custom_endpoint():
    try:
        response = requests.get(f'{BACKEND_API_URL}/custom')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 503
```

### Modifying Templates

Edit `templates/index.html` using Jinja2 syntax:
```html
<h1>{{ title }}</h1>
{% for item in items %}
  <p>{{ item }}</p>
{% endfor %}
```

### Adding Static Assets

Place files in `static/` directory:
- `static/css/` - Stylesheets
- `static/js/` - JavaScript
- `static/images/` - Images
- `static/fonts/` - Fonts

Reference in templates:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
<script src="{{ url_for('static', filename='js/custom.js') }}"></script>
```

## 🔒 Security Best Practices

1. **Never expose backend URL** to client
2. **Validate all inputs** before forwarding
3. **Sanitize error messages** before returning
4. **Use HTTPS** in production
5. **Set secure headers**:
   ```python
   @app.after_request
   def set_secure_headers(response):
       response.headers['X-Content-Type-Options'] = 'nosniff'
       response.headers['X-Frame-Options'] = 'DENY'
       response.headers['X-XSS-Protection'] = '1; mode=block'
       return response
   ```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [Gunicorn Deployment](https://gunicorn.org/)
- [Flask Best Practices](https://flask.palletsprojects.com/en/latest/patterns/)

## 🆚 Flask vs Static Serving

### Advantages of Flask

✅ **Proxy API requests** - No CORS issues
✅ **Server-side rendering** - Dynamic content
✅ **Error handling** - Graceful failures
✅ **Session management** - User state
✅ **Authentication** - Add login if needed
✅ **Logging** - Track usage
✅ **Caching** - Improve performance

### When to Use Static

- Simple deployment
- No backend proxy needed
- CDN hosting
- Minimal server resources

## 📞 Support

For issues or questions:
1. Check backend logs
2. Check Flask logs in terminal
3. Review browser console (F12)
4. Test API endpoints with curl
5. Refer to TROUBLESHOOTING.md

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-12  
**Status**: Production Ready ✅