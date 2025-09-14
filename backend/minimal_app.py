#!/usr/bin/env python
"""
Minimal test app for Azure deployment debugging
"""
from flask import Flask

# Create minimal Flask app without database dependencies
app = Flask(__name__)

@app.route('/')
def home():
    return {'status': 'ok', 'message': 'Minimal test app is working'}, 200

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
