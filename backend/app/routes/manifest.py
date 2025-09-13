"""
Routes for manifest processing API endpoints.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.services.manifest_parser import ManifestParser
from app.models.user import User
from app.models.order import Order
from app.models.manifest_email import ManifestEmail
from app.models.audit_log import AuditLog
from app.auth.decorators import require_permission, require_auth, Permissions
from app import db

manifest_bp = Blueprint('manifest', __name__)

ALLOWED_EXTENSIONS = {'docx', 'doc'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@manifest_bp.route('/upload', methods=['POST'])
@require_permission(Permissions.MANIFESTS_UPLOAD)
def upload_manifest():
    """Upload and process a manifest file."""
    try:
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .docx and .doc files are allowed'}), 400
        
        # Create upload directory if it doesn't exist
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file with secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Create manifest email record
        manifest_email = ManifestEmail(
            subject=f"Uploaded: {file.filename}",
            sender="manual_upload",
            received_at=datetime.utcnow(),
            file_path=file_path,
            original_filename=file.filename,
            processed_by_user_id=user.id
        )
        db.session.add(manifest_email)
        db.session.flush()
        
        # Parse the manifest
        parser = ManifestParser()
        services = parser.parse_manifest_file(file_path)
        
        # Process each service and create orders
        created_orders = []
        errors = []
        
        for service in services:
            try:
                # Create order from parsed service
                order = Order(
                    action=service.action,
                    service_date=service.service_date,
                    service_type=service.service_type,
                    description=service.description,
                    vehicle_model=service.vehicle_model,
                    vehicle_capacity=service.vehicle_capacity,
                    passenger_count_adults=service.passenger_count_adults,
                    passenger_count_children=service.passenger_count_children,
                    passenger_names=service.passenger_names,
                    contact_phone=service.contact_phone,
                    contact_email=service.contact_email,
                    pickup_location=service.pickup_location,
                    pickup_time=service.pickup_time,
                    dropoff_location=service.dropoff_location,
                    flight_number=service.flight_number,
                    comments=service.comments,
                    status='pending',
                    manifest_email_id=manifest_email.id,
                    created_by_user_id=user.id
                )
                
                # Set service ID if available
                if service.service_id:
                    order.external_service_id = service.service_id
                
                # Add missing data flags
                if service.missing_data_flags:
                    order.missing_data_flags = service.missing_data_flags
                
                db.session.add(order)
                created_orders.append({
                    'action': order.action,
                    'service_date': order.service_date.isoformat() if order.service_date else None,
                    'service_type': order.service_type,
                    'description': order.description[:100] + '...' if len(order.description) > 100 else order.description
                })
                
            except Exception as e:
                errors.append(f"Error creating order: {str(e)}")
        
        # Update manifest email with processing results
        manifest_email.services_found = len(services)
        manifest_email.orders_created = len(created_orders)
        manifest_email.processing_errors = errors
        manifest_email.processed_at = datetime.utcnow()
        manifest_email.status = 'processed' if created_orders else 'failed'
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            action='manifest_upload',
            resource_type='manifest',
            resource_id=manifest_email.id,
            details={
                'filename': file.filename,
                'services_found': len(services),
                'orders_created': len(created_orders),
                'errors': errors,
                'parser_errors': parser.get_errors(),
                'parser_warnings': parser.get_warnings()
            }
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        # Clean up temporary file
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify({
            'message': 'Manifest processed successfully',
            'manifest_id': manifest_email.id,
            'services_found': len(services),
            'orders_created': len(created_orders),
            'created_orders': created_orders,
            'errors': errors,
            'parser_warnings': parser.get_warnings()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing manifest: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@manifest_bp.route('/history', methods=['GET'])
@require_permission(Permissions.MANIFESTS_READ)
def get_manifest_history():
    """Get manifest processing history."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        manifests = ManifestEmail.query.order_by(
            ManifestEmail.received_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'manifests': [{
                'id': m.id,
                'subject': m.subject,
                'sender': m.sender,
                'received_at': m.received_at.isoformat(),
                'processed_at': m.processed_at.isoformat() if m.processed_at else None,
                'status': m.status,
                'services_found': m.services_found,
                'orders_created': m.orders_created,
                'original_filename': m.original_filename,
                'processing_errors': m.processing_errors
            } for m in manifests.items],
            'pagination': {
                'page': manifests.page,
                'pages': manifests.pages,
                'per_page': manifests.per_page,
                'total': manifests.total,
                'has_next': manifests.has_next,
                'has_prev': manifests.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting manifest history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@manifest_bp.route('/<int:manifest_id>/details', methods=['GET'])
@require_permission(Permissions.MANIFESTS_READ)
def get_manifest_details(manifest_id):
    """Get detailed information about a specific manifest."""
    try:
        manifest = ManifestEmail.query.get_or_404(manifest_id)
        
        # Get associated orders
        orders = Order.query.filter_by(manifest_email_id=manifest_id).all()
        
        return jsonify({
            'manifest': {
                'id': manifest.id,
                'subject': manifest.subject,
                'sender': manifest.sender,
                'received_at': manifest.received_at.isoformat(),
                'processed_at': manifest.processed_at.isoformat() if manifest.processed_at else None,
                'status': manifest.status,
                'services_found': manifest.services_found,
                'orders_created': manifest.orders_created,
                'original_filename': manifest.original_filename,
                'processing_errors': manifest.processing_errors,
                'processed_by': manifest.processed_by_user.email if manifest.processed_by_user else None
            },
            'orders': [{
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
                'pickup_location': order.pickup_location,
                'pickup_time': order.pickup_time,
                'flight_number': order.flight_number,
                'status': order.status,
                'missing_data_flags': order.missing_data_flags,
                'created_at': order.created_at.isoformat()
            } for order in orders]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting manifest details: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@manifest_bp.route('/test-parser', methods=['POST'])
@require_permission(Permissions.MANIFESTS_PARSE)
def test_parser():
    """Test the manifest parser without creating orders (for development)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save file temporarily
        upload_folder = os.path.join(current_app.root_path, 'temp')
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Parse the manifest
        parser = ManifestParser()
        services = parser.parse_manifest_file(file_path)
        
        # Clean up
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify({
            'services_found': len(services),
            'services': [{
                'action': s.action,
                'service_id': s.service_id,
                'service_date': s.service_date.isoformat() if s.service_date else None,
                'service_type': s.service_type,
                'description': s.description[:200] + '...' if len(s.description) > 200 else s.description,
                'vehicle_model': s.vehicle_model,
                'vehicle_capacity': s.vehicle_capacity,
                'passenger_count_adults': s.passenger_count_adults,
                'passenger_count_children': s.passenger_count_children,
                'passenger_names': s.passenger_names,
                'contact_phone': s.contact_phone,
                'pickup_location': s.pickup_location,
                'pickup_time': s.pickup_time,
                'flight_number': s.flight_number,
                'missing_data_flags': s.missing_data_flags
            } for s in services],
            'parser_errors': parser.get_errors(),
            'parser_warnings': parser.get_warnings()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error testing parser: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@manifest_bp.route('/stats', methods=['GET'])
@require_permission(Permissions.MANIFESTS_READ)
def get_manifest_stats():
    """Get manifest statistics for dashboard."""
    try:
        # Get basic counts
        total_manifests = ManifestEmail.query.count()
        processed_manifests = ManifestEmail.query.filter_by(status='processed').count()
        failed_manifests = ManifestEmail.query.filter_by(status='failed').count()
        pending_manifests = ManifestEmail.query.filter_by(status='pending').count()
        
        # Get monthly statistics for current year
        from sqlalchemy import func, extract
        current_year = datetime.now().year
        monthly_stats = db.session.query(
            func.extract('month', ManifestEmail.processed_at).label('month'),
            func.count(ManifestEmail.id).label('count')
        ).filter(
            extract('year', ManifestEmail.processed_at) == current_year
        ).group_by(
            func.extract('month', ManifestEmail.processed_at)
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
            'total_manifests': total_manifests,
            'processed_manifests': processed_manifests,
            'failed_manifests': failed_manifests,
            'pending_manifests': pending_manifests,
            'monthly_stats': monthly_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting manifest stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@manifest_bp.route('/emails', methods=['GET'])
@require_permission(Permissions.MANIFESTS_READ)
def get_manifest_emails():
    """Get list of manifest emails with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # Query with pagination
        paginated_manifests = ManifestEmail.query.order_by(
            ManifestEmail.processed_at.desc()
        ).paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        return jsonify({
            'manifests': [manifest.to_dict() for manifest in paginated_manifests.items],
            'pagination': {
                'page': page,
                'pages': paginated_manifests.pages,
                'per_page': limit,
                'total': paginated_manifests.total,
                'has_next': paginated_manifests.has_next,
                'has_prev': paginated_manifests.has_prev,
                'next_num': paginated_manifests.next_num,
                'prev_num': paginated_manifests.prev_num
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting manifest emails: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
