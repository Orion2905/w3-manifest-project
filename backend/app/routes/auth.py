from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from flask_cors import cross_origin
from werkzeug.security import check_password_hash
from app.models.user import User
from app.models.audit_log import AuditLog
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://127.0.0.1:3000'], supports_credentials=True)
def login():
    """User login endpoint."""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            # Log failed login attempt
            AuditLog.log_system_event(
                action='login_failed',
                description=f'Failed login attempt for: {username}',
                metadata={
                    'username': username,
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent')
                },
                status='warning'
            )
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create tokens
        additional_claims = {
            'role': user.role,
            'role_name': user.role_obj.name if user.role_obj else user.role,
            'full_name': user.full_name,
            'email': user.email,
            'permissions': user.get_permissions()
        }
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Update last login
        user.update_last_login()
        
        # Log successful login
        AuditLog.log_user_action(
            action='login',
            user=user,
            description='User logged in successfully',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(include_permissions=True),
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or deactivated'}), 401
        
        additional_claims = {
            'role': user.role,
            'full_name': user.full_name,
            'email': user.email
        }
        
        new_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )
        
        return jsonify({
            'access_token': new_token,
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user:
            # Log logout
            AuditLog.log_user_action(
                action='logout',
                user=user,
                description='User logged out',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
        
        # In a production environment, you might want to blacklist the token
        # For now, we just return success
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'User account is deactivated'}), 401
        
        return jsonify(user.to_dict(include_permissions=True)), 200
        
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters long'}), 400
        
        # Update password
        old_password_hash = user.password_hash
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log password change
        AuditLog.log_user_action(
            action='password_changed',
            user=user,
            description='User changed password',
            old_values={'password_hash': old_password_hash[:20] + '...'},  # Partial hash for security
            new_values={'password_hash': user.password_hash[:20] + '...'},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Change password error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/validate', methods=['GET'])
@jwt_required()
def validate_token():
    """Validate if the current token is still valid."""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({'valid': False, 'error': 'User not found or deactivated'}), 401
        
        return jsonify({
            'valid': True,
            'user_id': current_user_id,
            'role': claims.get('role'),
            'expires_at': datetime.fromtimestamp(claims['exp']).isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token validation error: {str(e)}")
        return jsonify({'valid': False, 'error': 'Token validation failed'}), 401
