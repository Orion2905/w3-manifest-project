import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def create_app(config_name=None):
    """Application factory pattern."""
    
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Enhanced CORS configuration using config
    cors.init_app(app, 
                  origins=app.config['CORS_ORIGINS'],
                  methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                  allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
                  supports_credentials=True,
                  expose_headers=['Content-Type', 'Authorization'])
    
    # Import models (needed for migrations)
    from app.models import user, order, manifest_email, audit_log, rbac, email_config
    
    # Register CLI commands
    from app import cli
    cli.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.manifest import manifest_bp
    from app.routes.orders import orders_bp
    from app.routes.rbac import rbac_bp
    from app.routes.email_config import bp as email_config_bp
    from app.routes.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(manifest_bp, url_prefix='/api/manifest')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(rbac_bp, url_prefix='/api/rbac')
    app.register_blueprint(email_config_bp)
    app.register_blueprint(users_bp, url_prefix='/api/admin')
    
    # Additional CORS handling
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in app.config['CORS_ORIGINS']:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'w3-manifest-api'}, 200
    
    # Root endpoint
    @app.route('/')
    def root():
        return {
            'message': 'W3 Manifest Management System API',
            'version': '1.0.0',
            'status': 'active',
            'endpoints': {
                'auth': '/api/auth',
                'orders': '/api/orders',
                'manifest': '/api/manifest',
                'rbac': '/api/rbac',
                'email-config': '/api/email-config',
                'admin-users': '/api/admin/users',
                'health': '/health'
            }
        }, 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return {'error': 'Bad request'}, 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden'}, 403
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization token is required'}, 401
    
    return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
