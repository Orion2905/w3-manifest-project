"""
Routes for order management API endpoints.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from sqlalchemy import and_, or_

from app.models.user import User
from app.models.order import Order
from app.models.audit_log import AuditLog
from app.auth.decorators import require_permission, require_auth, Permissions
from app import db

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('', methods=['GET'])
@orders_bp.route('/', methods=['GET'])
@require_permission(Permissions.ORDERS_READ)
def get_orders():
    """Get list of orders with filtering and pagination."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filters
        status = request.args.get('status')
        action = request.args.get('action')
        service_type = request.args.get('service_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search = request.args.get('search')
        
        # Build query
        query = Order.query
        
        # Apply filters
        if status:
            query = query.filter(Order.status == status)
        
        if action:
            query = query.filter(Order.action == action)
        
        if service_type:
            query = query.filter(Order.service_type.ilike(f'%{service_type}%'))
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Order.service_date >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Order.service_date <= date_to_obj)
            except ValueError:
                pass
        
        if search:
            search_filter = or_(
                Order.description.ilike(f'%{search}%'),
                Order.contact_phone.ilike(f'%{search}%'),
                Order.pickup_location.ilike(f'%{search}%'),
                Order.passenger_names.any(lambda name: search.lower() in name.lower())
            )
            query = query.filter(search_filter)
        
        # Order by service date (newest first)
        query = query.order_by(Order.service_date.desc().nullslast(), Order.created_at.desc())
        
        # Apply pagination
        orders = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'orders': [{
                'id': order.id,
                'action': order.action,
                'service_date': order.service_date.isoformat() if order.service_date else None,
                'service_type': order.service_type,
                'description': order.description[:100] + '...' if len(order.description) > 100 else order.description,
                'vehicle_model': order.vehicle_model,
                'vehicle_capacity': order.vehicle_capacity,
                'passenger_count_total': order.passenger_count_adults + order.passenger_count_children,
                'contact_phone': order.contact_phone,
                'pickup_location': order.pickup_location,
                'pickup_time': order.pickup_time,
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'missing_data_flags': order.missing_data_flags,
                'has_missing_data': bool(order.missing_data_flags)
            } for order in orders.items],
            'pagination': {
                'page': orders.page,
                'pages': orders.pages,
                'per_page': orders.per_page,
                'total': orders.total,
                'has_next': orders.has_next,
                'has_prev': orders.has_prev
            },
            'summary': {
                'total_orders': orders.total,
                'pending_orders': Order.query.filter_by(status='pending').count(),
                'approved_orders': Order.query.filter_by(status='approved').count(),
                'completed_orders': Order.query.filter_by(status='completed').count(),
                'cancelled_orders': Order.query.filter_by(status='cancelled').count()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting orders: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@require_permission(Permissions.ORDERS_READ)
def get_order_details(order_id):
    """Get detailed information about a specific order."""
    try:
        order = Order.query.get_or_404(order_id)
        
        return jsonify({
            'id': order.id,
            'action': order.action,
            'service_date': order.service_date.isoformat() if order.service_date else None,
            'service_type': order.service_type,
            'description': order.description,
            'vehicle_model': order.vehicle_model,
            'vehicle_capacity': order.vehicle_capacity,
            'passenger_count_adults': order.passenger_count_adults,
            'passenger_count_children': order.passenger_count_children,
            'passenger_names': order.passenger_names,
            'contact_phone': order.contact_phone,
            'contact_email': order.contact_email,
            'pickup_location': order.pickup_location,
            'pickup_time': order.pickup_time,
            'dropoff_location': order.dropoff_location,
            'flight_number': order.flight_number,
            'comments': order.comments,
            'status': order.status,
            'external_service_id': order.external_service_id,
            'confirmation_number': order.confirmation_number,
            'missing_data_flags': order.missing_data_flags,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
            'created_by': order.created_by_user.email if order.created_by_user else None,
            'approved_by': order.approved_by_user.email if order.approved_by_user else None,
            'approved_at': order.approved_at.isoformat() if order.approved_at else None,
            'manifest_email': {
                'id': order.manifest_email.id,
                'subject': order.manifest_email.subject,
                'sender': order.manifest_email.sender,
                'received_at': order.manifest_email.received_at.isoformat()
            } if order.manifest_email else None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting order details: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@require_permission(Permissions.ORDERS_UPDATE)
def update_order_status(order_id):
    """Update order status."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        new_status = data['status']
        valid_statuses = ['pending', 'approved', 'completed', 'cancelled']
        
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Valid options: {valid_statuses}'}), 400
        
        # Check permissions for status changes
        if new_status == 'approved' and user.role not in ['admin', 'operator']:
            return jsonify({'error': 'Insufficient permissions to approve orders'}), 403
        
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Set approval info if approving
        if new_status == 'approved' and old_status != 'approved':
            order.approved_by_user_id = user.id
            order.approved_at = datetime.utcnow()
        
        # Add confirmation number if provided
        if 'confirmation_number' in data:
            order.confirmation_number = data['confirmation_number']
        
        # Add comments if provided
        if 'comments' in data and data['comments']:
            if order.comments:
                order.comments += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] {data['comments']}"
            else:
                order.comments = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] {data['comments']}"
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            action='order_status_update',
            resource_type='order',
            resource_id=order.id,
            details={
                'old_status': old_status,
                'new_status': new_status,
                'confirmation_number': data.get('confirmation_number'),
                'comments': data.get('comments')
            }
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated successfully',
            'order_id': order.id,
            'old_status': old_status,
            'new_status': new_status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating order status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@orders_bp.route('/<int:order_id>', methods=['PUT'])
@require_permission(Permissions.ORDERS_UPDATE)
def update_order(order_id):
    """Update order details."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        # Only allow updates to certain fields
        updatable_fields = [
            'pickup_location', 'pickup_time', 'dropoff_location',
            'contact_phone', 'contact_email', 'comments',
            'confirmation_number', 'flight_number'
        ]
        
        changes = {}
        for field in updatable_fields:
            if field in data and getattr(order, field) != data[field]:
                changes[field] = {
                    'old': getattr(order, field),
                    'new': data[field]
                }
                setattr(order, field, data[field])
        
        if not changes:
            return jsonify({'message': 'No changes detected'}), 200
        
        order.updated_at = datetime.utcnow()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            action='order_update',
            resource_type='order',
            resource_id=order.id,
            details={'changes': changes}
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order updated successfully',
            'order_id': order.id,
            'changes': changes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating order: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@orders_bp.route('/bulk-action', methods=['POST'])
@require_permission(Permissions.ORDERS_UPDATE)
def bulk_order_action():
    """Perform bulk actions on multiple orders."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data or 'order_ids' not in data or 'action' not in data:
            return jsonify({'error': 'order_ids and action are required'}), 400
        
        order_ids = data['order_ids']
        action = data['action']
        
        if not isinstance(order_ids, list) or not order_ids:
            return jsonify({'error': 'order_ids must be a non-empty list'}), 400
        
        # Get orders
        orders = Order.query.filter(Order.id.in_(order_ids)).all()
        
        if len(orders) != len(order_ids):
            return jsonify({'error': 'Some orders not found'}), 404
        
        results = []
        
        if action == 'approve':
            if user.role not in ['admin', 'operator']:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            for order in orders:
                if order.status == 'pending':
                    order.status = 'approved'
                    order.approved_by_user_id = user.id
                    order.approved_at = datetime.utcnow()
                    order.updated_at = datetime.utcnow()
                    results.append({'id': order.id, 'status': 'approved'})
                else:
                    results.append({'id': order.id, 'status': 'skipped', 'reason': 'not pending'})
        
        elif action == 'cancel':
            for order in orders:
                if order.status not in ['completed', 'cancelled']:
                    order.status = 'cancelled'
                    order.updated_at = datetime.utcnow()
                    results.append({'id': order.id, 'status': 'cancelled'})
                else:
                    results.append({'id': order.id, 'status': 'skipped', 'reason': 'already completed/cancelled'})
        
        else:
            return jsonify({'error': f'Invalid action: {action}'}), 400
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            action=f'bulk_{action}',
            resource_type='order',
            details={
                'order_ids': order_ids,
                'action': action,
                'results': results
            }
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Bulk {action} completed',
            'results': results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error performing bulk action: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@orders_bp.route('/dashboard', methods=['GET'])
@require_permission(Permissions.DASHBOARD_VIEW)
def get_orders_dashboard():
    """Get dashboard statistics for orders."""
    try:
        # Get date range for filtering (default: last 30 days)
        days = request.args.get('days', 30, type=int)
        date_from = datetime.utcnow().date() - datetime.timedelta(days=days)
        
        # Basic counts
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        approved_orders = Order.query.filter_by(status='approved').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        cancelled_orders = Order.query.filter_by(status='cancelled').count()
        
        # Recent orders (last 30 days by default)
        recent_orders = Order.query.filter(
            Order.created_at >= datetime.combine(date_from, datetime.min.time())
        ).count()
        
        # Orders by action type
        new_orders = Order.query.filter_by(action='new').count()
        change_orders = Order.query.filter_by(action='change').count()
        cancel_orders = Order.query.filter_by(action='cancel').count()
        
        # Orders by service type
        service_types = db.session.query(
            Order.service_type,
            db.func.count(Order.id).label('count')
        ).filter(
            Order.service_type.isnot(None)
        ).group_by(Order.service_type).all()
        
        # Orders with missing data
        missing_data_orders = Order.query.filter(
            Order.missing_data_flags.isnot(None)
        ).count()
        
        # Recent activity (last 7 days)
        recent_activity = db.session.query(
            db.func.date(Order.created_at).label('date'),
            db.func.count(Order.id).label('count')
        ).filter(
            Order.created_at >= datetime.utcnow() - datetime.timedelta(days=7)
        ).group_by(
            db.func.date(Order.created_at)
        ).order_by('date').all()
        
        return jsonify({
            'summary': {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'approved_orders': approved_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'recent_orders': recent_orders,
                'missing_data_orders': missing_data_orders
            },
            'by_action': {
                'new': new_orders,
                'change': change_orders,
                'cancel': cancel_orders
            },
            'by_service_type': [
                {'service_type': st[0], 'count': st[1]} 
                for st in service_types
            ],
            'recent_activity': [
                {'date': activity[0].isoformat(), 'count': activity[1]}
                for activity in recent_activity
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@orders_bp.route('/stats', methods=['GET'])
@require_permission(Permissions.ORDERS_READ)
def get_orders_stats():
    """Get order statistics for dashboard."""
    try:
        # Get basic counts
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        cancelled_orders = Order.query.filter_by(status='cancelled').count()
        
        # Get monthly statistics for current year
        from sqlalchemy import func, extract
        current_year = datetime.now().year
        monthly_stats = db.session.query(
            func.extract('month', Order.created_at).label('month'),
            func.count(Order.id).label('count')
        ).filter(
            extract('year', Order.created_at) == current_year
        ).group_by(
            func.extract('month', Order.created_at)
        ).all()
        
        # Format monthly stats
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_data = []
        for month_num, count in monthly_stats:
            monthly_data.append({
                'month': months[int(month_num) - 1],
                'count': count
            })
        
        return jsonify({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'monthly_stats': monthly_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting order stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
