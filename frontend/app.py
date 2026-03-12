"""
SpecSentinel Frontend - Flask Application
Serves the web interface and proxies API requests to the backend
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

# Configuration
BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://localhost:8000')

# Routes
@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Proxy health check to backend"""
    try:
        response = requests.get(f'{BACKEND_API_URL}/health')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e), 'status': 'backend_unavailable'}), 503

@app.route('/api/stats')
def stats():
    """Proxy stats request to backend"""
    try:
        response = requests.get(f'{BACKEND_API_URL}/stats')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Proxy file upload analysis to backend"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get format parameter
        format_type = request.args.get('format', 'json')
        
        # Forward file to backend
        files = {'file': (file.filename, file.stream, file.content_type)}
        response = requests.post(
            f'{BACKEND_API_URL}/analyze',
            files=files,
            params={'format': format_type}
        )
        
        if format_type == 'text':
            return response.text, response.status_code, {'Content-Type': 'text/plain'}
        else:
            return jsonify(response.json()), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e), 'detail': 'Backend API error'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """Proxy text analysis to backend"""
    try:
        data = request.get_json()
        if not data or 'spec' not in data:
            return jsonify({'error': 'No spec provided'}), 400
        
        # Get format parameter
        format_type = request.args.get('format', 'json')
        
        # Forward to backend
        response = requests.post(
            f'{BACKEND_API_URL}/analyze/text',
            json=data,
            params={'format': format_type},
            headers={'Content-Type': 'application/json'}
        )
        
        if format_type == 'text':
            return response.text, response.status_code, {'Content-Type': 'text/plain'}
        else:
            return jsonify(response.json()), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e), 'detail': 'Backend API error'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh():
    """Proxy refresh request to backend"""
    try:
        response = requests.post(f'{BACKEND_API_URL}/refresh')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 503

# Static files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

# Made with Bob
