"""
Routes for role and permission management.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app.models.rbac import Role, Permission, UserPermission
from app.models.seeds import assign_user_role, user_has_higher_role
from app.auth.decorators import require_permission, require_admin, require_manager_or_above, Permissions
from app import db

rbac_bp = Blueprint('rbac', __name__)

@rbac_bp.route('/roles', methods=['GET'])
@require_permission(Permissions.USERS_READ)
def get_roles():
    """Get all available roles."""
    try:
        roles = Role.query.all()
        return jsonify({
            'roles': [role.to_dict() for role in roles]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching roles: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@rbac_bp.route('/permissions', methods=['GET'])
@require_permission(Permissions.USERS_READ)
def get_permissions():
    """Get all available permissions."""
    try:
        permissions = Permission.query.all()
        
        # Group permissions by resource
        grouped_permissions = {}
        for permission in permissions:
            resource = permission.resource
            if resource not in grouped_permissions:
                grouped_permissions[resource] = []
            grouped_permissions[resource].append(permission.to_dict())
        
        return jsonify({
            'permissions': grouped_permissions,
            'total': len(permissions)
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching permissions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@rbac_bp.route('/user/<int:user_id>/role', methods=['PUT'])
@require_permission(Permissions.USERS_MANAGE_ROLES)
def assign_role_to_user(user_id):
    """Assign a role to a user."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        target_user = User.query.get_or_404(user_id)
        
        data = request.get_json()
        role_name = data.get('role')
        
        if not role_name:
            return jsonify({'error': 'Role is required'}), 400
        
        # Check if role exists
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        
        # Check if current user can assign this role
        if not current_user.is_admin():
            # Non-admin users cannot assign admin roles
            if role_name == 'admin':
                return jsonify({'error': 'Cannot assign admin role'}), 403
            
            # Check role hierarchy
            if not user_has_higher_role(current_user, role_name):
                return jsonify({'error': 'Cannot assign role of equal or higher level'}), 403
        
        # Assign role
        if assign_user_role(target_user, role_name):
            return jsonify({
                'message': f'Role {role_name} assigned to user {target_user.username}',
                'user': target_user.to_dict(include_permissions=True)
            }), 200
        else:
            return jsonify({'error': 'Failed to assign role'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error assigning role: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@rbac_bp.route('/user/<int:user_id>/permissions', methods=['GET'])
@require_permission(Permissions.USERS_READ)
def get_user_permissions(user_id):
    """Get all permissions for a specific user."""
    try:
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'role': user.role_obj.name if user.role_obj else user.role,
            'permissions': user.get_permissions(),
            'role_permissions': [p.name for p in user.role_obj.permissions] if user.role_obj else [],
            'individual_permissions': [
                {
                    'permission': up.permission.name,
                    'granted': up.granted,
                    'granted_at': up.granted_at.isoformat() if up.granted_at else None,
                    'granted_by': up.granted_by_user.username if up.granted_by_user else None
                }
                for up in user.user_permissions
            ]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching user permissions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@rbac_bp.route('/user/<int:user_id>/permissions', methods=['POST'])
@require_admin
def grant_user_permission(user_id):
    """Grant or revoke a specific permission for a user."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        target_user = User.query.get_or_404(user_id)
        
        data = request.get_json()
        permission_name = data.get('permission')
        granted = data.get('granted', True)
        
        if not permission_name:
            return jsonify({'error': 'Permission name is required'}), 400
        
        # Check if permission exists
        permission = Permission.query.filter_by(name=permission_name).first()
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404
        
        # Check if user already has individual permission set
        user_permission = UserPermission.query.filter_by(
            user_id=user_id,
            permission_id=permission.id
        ).first()
        
        if user_permission:
            # Update existing permission
            user_permission.granted = granted
            user_permission.granted_at = datetime.utcnow()
            user_permission.granted_by = current_user_id
        else:
            # Create new user permission
            user_permission = UserPermission(
                user_id=user_id,
                permission_id=permission.id,
                granted=granted,
                granted_by=current_user_id
            )
            db.session.add(user_permission)
        
        db.session.commit()
        
        action = 'granted' if granted else 'revoked'
        return jsonify({
            'message': f'Permission {permission_name} {action} for user {target_user.username}',
            'user_permissions': target_user.get_permissions()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error managing user permission: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@rbac_bp.route('/role/<int:role_id>/permissions', methods=['GET'])
@require_permission(Permissions.USERS_READ)
def get_role_permissions(role_id):
    """Get all permissions for a specific role."""
    try:
        role = Role.query.get_or_404(role_id)
        
        return jsonify({
            'role_id': role_id,
            'role_name': role.name,
            'role_display': role.display_name,
            'permissions': [permission.to_dict() for permission in role.permissions]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching role permissions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@rbac_bp.route('/role/<int:role_id>/permissions', methods=['PUT'])
@require_admin
def update_role_permissions(role_id):
    """Update permissions for a role."""
    try:
        role = Role.query.get_or_404(role_id)
        
        data = request.get_json()
        permission_ids = data.get('permission_ids', [])
        
        # Clear existing permissions
        role.permissions.clear()
        
        # Add new permissions
        for permission_id in permission_ids:
            permission = Permission.query.get(permission_id)
            if permission:
                role.permissions.append(permission)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Permissions updated for role {role.name}',
            'role': role.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating role permissions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@rbac_bp.route('/check-permission', methods=['POST'])
@require_permission(Permissions.API_ACCESS)
def check_permission():
    """Check if current user has a specific permission."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        data = request.get_json()
        permission_name = data.get('permission')
        resource = data.get('resource')
        
        if not permission_name:
            return jsonify({'error': 'Permission name is required'}), 400
        
        has_permission = user.has_permission(permission_name, resource)
        
        return jsonify({
            'user_id': user.id,
            'permission': permission_name,
            'resource': resource,
            'has_permission': has_permission
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error checking permission: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
