"""
Routes for user management (Admin panel).
Includes CRUD operations for users with proper authorization.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash
from sqlalchemy import or_, and_
from app.models.user import User
from app.models.rbac import Role, Permission, UserPermission
from app.models.seeds import assign_user_role, user_has_higher_role
from app.auth.decorators import require_permission, require_admin, require_manager_or_above, Permissions
from app import db
import re

users_bp = Blueprint('users', __name__)

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@users_bp.route('/users', methods=['GET'])
@require_permission(Permissions.USERS_READ)
def get_users():
    """Get all users with pagination and filtering."""
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
        
        # Filter parameters
        search = request.args.get('search', '').strip()
        role_filter = request.args.get('role', '').strip()
        status_filter = request.args.get('status', '').strip()  # active, inactive, locked, verified
        
        # Base query
        query = User.query
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            ))
        
        # Apply role filter
        if role_filter:
            query = query.join(Role, User.role_id == Role.id).filter(Role.name == role_filter)
        
        # Apply status filter
        if status_filter:
            if status_filter == 'active':
                query = query.filter(and_(User.is_active == True, User.is_locked == False))
            elif status_filter == 'inactive':
                query = query.filter(User.is_active == False)
            elif status_filter == 'locked':
                query = query.filter(User.is_locked == True)
            elif status_filter == 'verified':
                query = query.filter(User.is_verified == True)
            elif status_filter == 'unverified':
                query = query.filter(User.is_verified == False)
        
        # Order by creation date (newest first)
        query = query.order_by(User.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users = pagination.items
        
        # Convert to dict with role information
        users_data = []
        for user in users:
            user_dict = user.to_dict()
            # Add role information
            if user.role_obj:
                user_dict['role'] = {
                    'id': user.role_obj.id,
                    'name': user.role_obj.name,
                    'display_name': user.role_obj.display_name,
                    'description': user.role_obj.description
                }
            users_data.append(user_dict)
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'search': search,
                'role': role_filter,
                'status': status_filter
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@require_permission(Permissions.USERS_READ)
def get_user(user_id):
    """Get a specific user by ID."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        user = User.query.get_or_404(user_id)
        
        # Check if current user can view this user
        target_role = user.role_obj.name if user.role_obj else 'viewer'
        if not user_has_higher_role(current_user, target_role) and current_user.id != user.id:
            return jsonify({'error': 'Insufficient permissions to view this user'}), 403
        
        user_dict = user.to_dict()
        
        # Add role information
        if user.role_obj:
            user_dict['role'] = {
                'id': user.role_obj.id,
                'name': user.role_obj.name,
                'display_name': user.role_obj.display_name,
                'description': user.role_obj.description
            }
        
        # Add permissions information for admins
        if current_user.role_obj and current_user.role_obj.name == 'admin':
            permissions = []
            if user.role_obj:
                for permission in user.role_obj.permissions:
                    permissions.append({
                        'id': permission.id,
                        'name': permission.name,
                        'resource': permission.resource,
                        'action': permission.action,
                        'description': permission.description
                    })
            user_dict['permissions'] = permissions
        
        return jsonify({'user': user_dict}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/users', methods=['POST'])
@require_permission(Permissions.USERS_CREATE)
def create_user():
    """Create a new user."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            or_(User.username == data['username'], User.email == data['email'])
        ).first()
        
        if existing_user:
            if existing_user.username == data['username']:
                return jsonify({'error': 'Username already exists'}), 409
            else:
                return jsonify({'error': 'Email already exists'}), 409
        
        # Get current user for permission checking
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Validate role assignment
        role_id = data.get('role_id')
        if role_id:
            role = Role.query.get(role_id)
            if not role:
                return jsonify({'error': 'Invalid role ID'}), 400
            
            # Check if current user can assign this role
            current_user_role = current_user.role_obj.name if current_user.role_obj else current_user.role
            if not user_has_higher_role(current_user, role.name) or \
               (role.name == 'admin' and current_user_role != 'admin'):
                return jsonify({'error': 'Insufficient permissions to assign this role'}), 403
        else:
            # Default to viewer role
            role = Role.query.filter_by(name='viewer').first()
            if role:
                role_id = role.id
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            role_id=role_id,
            is_active=data.get('is_active', True),
            is_verified=data.get('is_verified', False),
            is_locked=data.get('is_locked', False),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f"User {user.username} created by {current_user.username}")
        
        # Return created user data
        user_dict = user.to_dict()
        if user.role_obj:
            user_dict['role'] = {
                'id': user.role_obj.id,
                'name': user.role_obj.name,
                'display_name': user.role_obj.display_name,
                'description': user.role_obj.description
            }
        
        return jsonify({
            'message': 'User created successfully',
            'user': user_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_permission(Permissions.USERS_UPDATE)
def update_user(user_id):
    """Update an existing user."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        user = User.query.get_or_404(user_id)
        
        # Check if current user can update this user
        target_role = user.role_obj.name if user.role_obj else 'viewer'
        if not user_has_higher_role(current_user, target_role) and current_user.id != user.id:
            return jsonify({'error': 'Insufficient permissions to update this user'}), 403
        
        data = request.get_json()
        
        # Validate email format if provided
        if 'email' in data and data['email'] != user.email:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if email already exists
            existing_user = User.query.filter(
                and_(User.email == data['email'], User.id != user.id)
            ).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 409
        
        # Validate username if provided
        if 'username' in data and data['username'] != user.username:
            existing_user = User.query.filter(
                and_(User.username == data['username'], User.id != user.id)
            ).first()
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 409
        
        # Validate password if provided
        if 'password' in data and data['password']:
            is_valid, message = validate_password(data['password'])
            if not is_valid:
                return jsonify({'error': message}), 400
        
        # Validate role change
        if 'role_id' in data and data['role_id'] != user.role_id:
            new_role = Role.query.get(data['role_id'])
            if not new_role:
                return jsonify({'error': 'Invalid role ID'}), 400
            
            # Check if current user can assign this role
            current_user_role = current_user.role_obj.name if current_user.role_obj else current_user.role
            target_role = user.role_obj.name if user.role_obj else 'viewer'
            if not user_has_higher_role(current_user, target_role) or \
               (new_role.name == 'admin' and current_user_role != 'admin'):
                return jsonify({'error': 'Insufficient permissions to assign this role'}), 403
        
        # Update user fields
        updatable_fields = [
            'username', 'email', 'first_name', 'last_name', 
            'is_active', 'is_verified', 'is_locked', 'role_id'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'password':
                    user.password_hash = generate_password_hash(data['password'])
                else:
                    setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"User {user.username} updated by {current_user.username}")
        
        # Return updated user data
        user_dict = user.to_dict()
        if user.role_obj:
            user_dict['role'] = {
                'id': user.role_obj.id,
                'name': user.role_obj.name,
                'display_name': user.role_obj.display_name,
                'description': user.role_obj.description
            }
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user_dict
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_permission(Permissions.USERS_DELETE)
def delete_user(user_id):
    """Delete a user (soft delete by deactivating)."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        user = User.query.get_or_404(user_id)
        
        # Prevent self-deletion
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Check if current user can delete this user
        target_role = user.role_obj.name if user.role_obj else 'viewer'
        if not user_has_higher_role(current_user, target_role):
            return jsonify({'error': 'Insufficient permissions to delete this user'}), 403
        
        # Soft delete: deactivate instead of hard delete
        user.is_active = False
        user.is_locked = True
        user.updated_at = datetime.utcnow()
        user.deleted_at = datetime.utcnow()
        
        # Optional: Add deleted suffix to username/email to allow reuse
        if not user.username.endswith('_deleted'):
            user.username = f"{user.username}_deleted_{user.id}"
        if not user.email.endswith('_deleted'):
            user.email = f"{user.email}_deleted_{user.id}"
        
        db.session.commit()
        
        current_app.logger.info(f"User {user.username} deleted by {current_user.username}")
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/users/<int:user_id>/toggle-status', methods=['PATCH'])
@require_permission(Permissions.USERS_UPDATE)
def toggle_user_status(user_id):
    """Toggle user active/inactive status."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        user = User.query.get_or_404(user_id)
        
        # Prevent self-modification
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot modify your own status'}), 400
        
        # Check permissions
        target_role = user.role_obj.name if user.role_obj else 'viewer'
        if not user_has_higher_role(current_user, target_role):
            return jsonify({'error': 'Insufficient permissions to modify this user'}), 403
        
        # Toggle status
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        status = "activated" if user.is_active else "deactivated"
        current_app.logger.info(f"User {user.username} {status} by {current_user.username}")
        
        return jsonify({
            'message': f'User {status} successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_active': user.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling user status {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@require_permission(Permissions.USERS_RESET_PASSWORD)
def reset_user_password(user_id):
    """Reset user password (admin function)."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        user = User.query.get_or_404(user_id)
        
        # Check permissions
        target_role = user.role_obj.name if user.role_obj else 'viewer'
        if not user_has_higher_role(current_user, target_role) and current_user.id != user.id:
            return jsonify({'error': 'Insufficient permissions to reset this user password'}), 403
        
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password:
            return jsonify({'error': 'New password is required'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Force password change on next login
        user.must_change_password = True
        
        db.session.commit()
        
        current_app.logger.info(f"Password reset for user {user.username} by {current_user.username}")
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error resetting password for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/users/stats', methods=['GET'])
@require_permission(Permissions.USERS_READ)
def get_user_stats():
    """Get user statistics for admin dashboard."""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        inactive_users = User.query.filter_by(is_active=False).count()
        locked_users = User.query.filter_by(is_locked=True).count()
        verified_users = User.query.filter_by(is_verified=True).count()
        
        # Users by role
        role_stats = {}
        roles = Role.query.all()
        for role in roles:
            count = User.query.filter_by(role_id=role.id).count()
            role_stats[role.name] = {
                'count': count,
                'display_name': role.display_name
            }
        
        # Recent users (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_users = User.query.filter(User.created_at >= thirty_days_ago).count()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'locked_users': locked_users,
            'verified_users': verified_users,
            'unverified_users': total_users - verified_users,
            'role_distribution': role_stats,
            'recent_users': recent_users
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching user stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
