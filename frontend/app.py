"""
SpecSentinel Frontend - Flask Application
Serves the web interface and proxies API requests to the backend
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, Response, stream_with_context
import requests
import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# NEW: Import centralized logging
from src.utils.logging_config import get_logger
from src.utils.logging_middleware import FlaskLoggingMiddleware

app = Flask(__name__)

# NEW: Use centralized logger
logger = get_logger(__name__)

# NEW: Add logging middleware
FlaskLoggingMiddleware(app)

# Configuration
BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://localhost:8000')

logger.info(f"Frontend initialized, backend URL: {BACKEND_API_URL}")

# Routes
@app.route('/')
def index():
    """Serve the main page"""
    logger.debug("Serving index page")
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Proxy health check to backend"""
    try:
        response = requests.get(f'{BACKEND_API_URL}/health')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Backend health check failed: {e}")
        return jsonify({'error': str(e), 'status': 'backend_unavailable'}), 503

@app.route('/api/stats')
def stats():
    """Proxy stats request to backend"""
    try:
        response = requests.get(f'{BACKEND_API_URL}/stats')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Backend stats request failed: {e}")
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
        logger.error(f"Backend analyze request failed: {e}")
        return jsonify({'error': str(e), 'detail': 'Backend API error'}), 503
    except Exception as e:
        logger.exception("Analyze request failed")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/stream', methods=['POST'])
def analyze_stream():
    """Proxy streaming analyze requests to backend API with Server-Sent Events"""
    try:
        if 'file' not in request.files:
            logger.warning("No file provided in streaming analyze request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename in streaming analyze request")
            return jsonify({'error': 'No file selected'}), 400
        
        logger.info(f"Proxying streaming analyze request for file: {file.filename}")
        
        # Forward to backend with streaming
        files = {'file': (file.filename, file.read(), file.content_type)}
        
        def generate():
            """Stream events from backend to frontend"""
            try:
                with requests.post(
                    f'{BACKEND_API_URL}/analyze/stream',
                    files=files,
                    stream=True
                ) as response:
                    logger.info(f"Backend streaming response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        for line in response.iter_lines():
                            if line:
                                yield line.decode('utf-8') + '\n'
                    else:
                        error_msg = f'{{"stage": "ERROR", "status": "error", "message": "Backend error: {response.status_code}"}}'
                        yield f'data: {error_msg}\n\n'
                        
            except requests.exceptions.ConnectionError:
                logger.error("Failed to connect to backend API for streaming")
                error_msg = '{"stage": "ERROR", "status": "error", "message": "Backend API unavailable"}'
                yield f'data: {error_msg}\n\n'
            except Exception as e:
                logger.exception("Error in streaming analyze")
                error_msg = f'{{"stage": "ERROR", "status": "error", "message": "{str(e)}"}}'
                yield f'data: {error_msg}\n\n'
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
            
    except Exception as e:
        logger.exception("Error setting up streaming analyze")
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
        logger.error(f"Backend analyze/text request failed: {e}")
        return jsonify({'error': str(e), 'detail': 'Backend API error'}), 503
    except Exception as e:
        logger.exception("Analyze text request failed")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh():
    """Proxy refresh request to backend"""
    try:
        response = requests.post(f'{BACKEND_API_URL}/refresh')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Backend refresh request failed: {e}")
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
    logger.info("Starting Flask development server on http://0.0.0.0:5000")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

# Made with Bob
