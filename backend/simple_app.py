#!/usr/bin/env python
"""
Simple test app for Azure deployment
"""
from flask import Flask

# Create a simple test app
app = Flask(__name__)

@app.route('/')
def home():
    return {'status': 'success', 'message': 'Backend API is running!'}, 200

@app.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': '2025-09-14'}, 200

@app.route('/api/test')
def test():
    return {'message': 'Test endpoint working'}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
