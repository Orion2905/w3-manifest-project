"""
Authorization decorators and utilities for Flask routes.
"""
from functools import wraps
from flask import current_app, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User
from app.models.rbac import Permission

def require_auth(f):
    """Decorator to require valid JWT authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
    return decorated_function

def require_permission(permission_name, resource=None):
    """Decorator to require specific permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user = get_current_user()
                
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                
                if not user.is_active:
                    return jsonify({'error': 'Account is deactivated'}), 403
                
                if user.is_locked:
                    return jsonify({'error': 'Account is locked'}), 403
                
                # Check if user has the required permission
                if not user.has_permission(permission_name, resource):
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required_permission': permission_name,
                        'resource': resource
                    }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Authorization failed', 'message': str(e)}), 401
        return decorated_function
    return decorator

def require_role(role_name):
    """Decorator to require specific role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user = get_current_user()
                
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                
                if not user.is_active:
                    return jsonify({'error': 'Account is deactivated'}), 403
                
                if not user.has_role(role_name):
                    return jsonify({
                        'error': 'Insufficient role',
                        'required_role': role_name,
                        'current_role': user.role_obj.name if user.role_obj else user.role
                    }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Authorization failed', 'message': str(e)}), 401
        return decorated_function
    return decorator

def require_admin(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user = get_current_user()
            
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            if not user.is_admin():
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authorization failed', 'message': str(e)}), 401
    return decorated_function

def require_manager_or_above(f):
    """Decorator to require manager role or higher."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user = get_current_user()
            
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            if not user.is_manager():
                return jsonify({'error': 'Manager access or higher required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authorization failed', 'message': str(e)}), 401
    return decorated_function

def require_resource_access(resource):
    """Decorator to require access to a specific resource."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user = get_current_user()
                
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                
                if not user.can_access_resource(resource):
                    return jsonify({
                        'error': 'Access denied to resource',
                        'resource': resource
                    }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Authorization failed', 'message': str(e)}), 401
        return decorated_function
    return decorator

def get_current_user():
    """Get the current authenticated user."""
    try:
        current_user_id = get_jwt_identity()
        if current_user_id:
            return User.query.get(int(current_user_id))
        return None
    except:
        return None

def get_current_user_id():
    """Get the current authenticated user ID as integer."""
    current_user_id = get_jwt_identity()
    return int(current_user_id) if current_user_id else None

def check_permission_middleware():
    """Middleware to check permissions for API endpoints."""
    # This can be used as a before_request handler
    # to automatically check permissions based on endpoint
    pass

class PermissionChecker:
    """Utility class for permission checking."""
    
    @staticmethod
    def can_user_access_user(current_user, target_user_id):
        """Check if current user can access another user's data."""
        if current_user.is_admin():
            return True
        
        if current_user.is_manager():
            target_user = User.query.get(target_user_id)
            if target_user:
                # Managers can access non-admin users
                return not target_user.is_admin()
        
        # Users can only access their own data
        return current_user.id == target_user_id
    
    @staticmethod
    def can_user_modify_user(current_user, target_user_id):
        """Check if current user can modify another user."""
        if current_user.is_admin():
            return True
        
        # Only admins can modify other users
        return False
    
    @staticmethod
    def filter_data_by_permissions(current_user, data, resource_type):
        """Filter data based on user permissions."""
        if current_user.is_admin():
            return data
        
        # Add filtering logic based on resource type and user permissions
        # This is a placeholder for more complex filtering logic
        return data

# Permission constants for easy reference
class Permissions:
    # Dashboard
    DASHBOARD_VIEW = 'dashboard.view'
    DASHBOARD_ANALYTICS = 'dashboard.analytics'
    
    # Users
    USERS_CREATE = 'users.create'
    USERS_READ = 'users.read'
    USERS_UPDATE = 'users.update'
    USERS_DELETE = 'users.delete'
    USERS_MANAGE_ROLES = 'users.manage_roles'
    USERS_RESET_PASSWORD = 'users.reset_password'
    
    # Orders
    ORDERS_CREATE = 'orders.create'
    ORDERS_READ = 'orders.read'
    ORDERS_UPDATE = 'orders.update'
    ORDERS_DELETE = 'orders.delete'
    ORDERS_EXPORT = 'orders.export'
    ORDERS_ASSIGN = 'orders.assign'
    
    # Manifests
    MANIFESTS_UPLOAD = 'manifests.upload'
    MANIFESTS_READ = 'manifests.read'
    MANIFESTS_UPDATE = 'manifests.update'
    MANIFESTS_DELETE = 'manifests.delete'
    MANIFESTS_PARSE = 'manifests.parse'
    MANIFESTS_APPROVE = 'manifests.approve'
    MANIFESTS_EXPORT = 'manifests.export'
    
    # System
    SYSTEM_LOGS = 'system.logs'
    SYSTEM_SETTINGS = 'system.settings'
    SYSTEM_BACKUP = 'system.backup'
    SYSTEM_MAINTENANCE = 'system.maintenance'
    
    # Reports
    REPORTS_VIEW = 'reports.view'
    REPORTS_CREATE = 'reports.create'
    REPORTS_EXPORT = 'reports.export'
    REPORTS_SCHEDULE = 'reports.schedule'
    
    # API
    API_ACCESS = 'api.access'
    API_ADMIN = 'api.admin'
