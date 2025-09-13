"""
Email configuration routes for IMAP monitoring.
Admin-only endpoints for managing email configurations.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.email_config import EmailConfig, EmailLog
from app.models.user import User
from app.auth.decorators import require_admin, get_current_user
from app.services.imap_monitor import imap_service
import imaplib
import ssl
import logging
from datetime import datetime

# Setup logger for IMAP monitoring
logger = logging.getLogger('imap_monitor')
logger.setLevel(logging.DEBUG)

# Create file handler for IMAP logs
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - IMAP_MONITOR - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

bp = Blueprint('email_config', __name__, url_prefix='/api/email-config')

@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
@jwt_required()
@require_admin
def get_email_configs():
    """Get all email configurations (admin only)."""
    try:
        current_user = get_current_user()
        logger.info(f"📧 IMAP Request - GET configs | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr}")
        
        configs = EmailConfig.query.all()
        logger.debug(f"📊 Retrieved {len(configs)} email configurations for user {current_user.username}")
        
        return jsonify({
            'success': True,
            'data': [config.to_dict(include_sensitive=True) for config in configs],
            'total': len(configs)
        })
    except Exception as e:
        logger.error(f"❌ IMAP Error - GET configs failed | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch email configurations',
            'message': str(e)
        }), 500


@bp.route('', methods=['POST'])
@bp.route('/', methods=['POST'])
@jwt_required()
@require_admin
def create_email_config():
    """Create new email configuration (admin only)."""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        logger.info(f"📧 IMAP Request - CREATE config | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr}")
        logger.debug(f"📝 Creating IMAP config: {data.get('name', 'Unknown')} for server {data.get('imap_server', 'Unknown')}")
        
        # Validate required fields
        required_fields = ['name', 'imap_server', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"⚠️ IMAP Validation - Missing field '{field}' | User: {current_user.username}")
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Check if name already exists
        existing_config = EmailConfig.query.filter_by(name=data['name']).first()
        if existing_config:
            logger.warning(f"⚠️ IMAP Conflict - Config name '{data['name']}' already exists | User: {current_user.username}")
            return jsonify({
                'success': False,
                'error': 'Configuration name already exists'
            }), 400
        
        # Create new configuration
        config = EmailConfig(
            name=data['name'],
            imap_server=data['imap_server'],
            imap_port=data.get('imap_port', 993),
            email=data['email'],
            use_ssl=data.get('use_ssl', True),
            use_starttls=data.get('use_starttls', False),
            folder=data.get('folder', 'INBOX'),
            subject_filter=data.get('subject_filter'),
            sender_filter=data.get('sender_filter'),
            attachment_filter=data.get('attachment_filter'),
            is_active=data.get('is_active', True),
            created_by=current_user.id
        )
        
        # Set password
        config.set_password(data['password'])
        
        db.session.add(config)
        db.session.commit()
        
        logger.info(f"✅ IMAP Success - Config '{config.name}' created | User: {current_user.username} | Server: {config.imap_server}:{config.imap_port}")
        
        return jsonify({
            'success': True,
            'message': 'Email configuration created successfully',
            'data': config.to_dict(include_sensitive=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ IMAP Error - Config creation failed | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create email configuration',
            'message': str(e)
        }), 500


@bp.route('/<int:config_id>', methods=['GET'])
@jwt_required()
@require_admin
def get_email_config(config_id):
    """Get specific email configuration (admin only)."""
    try:
        config = EmailConfig.query.get(config_id)
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': config.to_dict(include_sensitive=True)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch email configuration',
            'message': str(e)
        }), 500


@bp.route('/<int:config_id>', methods=['PUT'])
@jwt_required()
@require_admin
def update_email_config(config_id):
    """Update email configuration (admin only)."""
    try:
        config = EmailConfig.query.get(config_id)
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'name', 'imap_server', 'imap_port', 'email', 'use_ssl', 
            'use_starttls', 'folder', 'subject_filter', 'sender_filter', 
            'attachment_filter', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(config, field, data[field])
        
        # Update password if provided
        if 'password' in data and data['password']:
            config.set_password(data['password'])
        
        config.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Email configuration updated successfully',
            'data': config.to_dict(include_sensitive=True)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to update email configuration',
            'message': str(e)
        }), 500


@bp.route('/<int:config_id>', methods=['DELETE'])
@jwt_required()
@require_admin
def delete_email_config(config_id):
    """Delete email configuration (admin only)."""
    try:
        config = EmailConfig.query.get(config_id)
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            }), 404
        
        db.session.delete(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Email configuration deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to delete email configuration',
            'message': str(e)
        }), 500


@bp.route('/<int:config_id>/test', methods=['POST'])
@jwt_required()
@require_admin
def test_email_config(config_id):
    """Test email configuration connection (admin only)."""
    try:
        current_user = get_current_user()
        logger.info(f"🔍 IMAP Test - Starting connection test | User: {current_user.username} (ID: {current_user.id}) | Config ID: {config_id} | IP: {request.remote_addr}")
        
        config = EmailConfig.query.get(config_id)
        if not config:
            logger.warning(f"⚠️ IMAP Test - Config not found | User: {current_user.username} | Config ID: {config_id}")
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            }), 404
        
        logger.info(f"🔗 IMAP Test - Testing config '{config.name}' | Server: {config.imap_server}:{config.imap_port} | Email Account: {config.email} | Folder: {config.folder} | User: {current_user.username}")
        
        # Test IMAP connection
        try:
            # Create IMAP connection
            logger.debug(f"🌐 IMAP Connect - Attempting connection to {config.imap_server}:{config.imap_port} | Email Account: {config.email} | SSL: {config.use_ssl} | STARTTLS: {config.use_starttls}")
            
            if config.use_ssl:
                mail = imaplib.IMAP4_SSL(config.imap_server, config.imap_port)
                logger.debug(f"🔒 IMAP SSL - Connection established to {config.imap_server} for account {config.email}")
            else:
                mail = imaplib.IMAP4(config.imap_server, config.imap_port)
                if config.use_starttls:
                    mail.starttls()
                    logger.debug(f"🔒 IMAP STARTTLS - Secure connection established to {config.imap_server} for account {config.email}")
                else:
                    logger.debug(f"🔓 IMAP Plain - Connection established to {config.imap_server} for account {config.email}")
            
            # Try to login
            logger.debug(f"🔑 IMAP Auth - Attempting login for email account: {config.email}")
            mail.login(config.email, config.get_password())
            logger.info(f"✅ IMAP Auth - Login successful for email account: {config.email}")
            
            # Try to select folder
            logger.debug(f"📁 IMAP Folder - Selecting folder '{config.folder}' in mailbox {config.email}")
            status, messages = mail.select(config.folder)
            if status != 'OK':
                raise Exception(f"Cannot select folder '{config.folder}' in mailbox {config.email}")
            
            message_count = int(messages[0]) if messages and messages[0] else 0
            logger.info(f"📊 IMAP Folder - Selected '{config.folder}' in mailbox {config.email} with {message_count} messages")
            
            # Get folder info
            folder_info = {
                'folder': config.folder,
                'message_count': message_count,
                'email_account': config.email,
                'server': config.imap_server
            }
            
            # Close connection
            mail.close()
            mail.logout()
            logger.debug(f"🔚 IMAP Disconnect - Connection closed to {config.imap_server} for account {config.email}")
            
            # Update last success
            config.update_last_check(success=True)
            
            logger.info(f"✅ IMAP Test Success - Config '{config.name}' | Email Account: {config.email} | User: {current_user.username} | Messages: {message_count}")
            
            return jsonify({
                'success': True,
                'message': 'IMAP connection test successful',
                'data': {
                    'server': config.imap_server,
                    'port': config.imap_port,
                    'email': config.email,
                    'folder_info': folder_info,
                    'ssl': config.use_ssl,
                    'starttls': config.use_starttls
                }
            })
            
        except Exception as imap_error:
            # Update last error
            error_message = f"IMAP connection failed: {str(imap_error)}"
            config.update_last_check(success=False, error_message=error_message)
            
            logger.error(f"❌ IMAP Test Failed - Config '{config.name}' | Email Account: {config.email} | User: {current_user.username} | Server: {config.imap_server}:{config.imap_port} | Error: {str(imap_error)}")
            
            return jsonify({
                'success': False,
                'error': 'IMAP connection test failed',
                'message': str(imap_error)
            }), 400
            
    except Exception as e:
        logger.error(f"❌ IMAP Test Error - General failure | User: {getattr(get_current_user(), 'username', 'Unknown')} | Config ID: {config_id} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to test email configuration',
            'message': str(e)
        }), 500


@bp.route('/<int:config_id>/logs', methods=['GET'])
@jwt_required()
@require_admin
def get_email_logs(config_id):
    """Get email monitoring logs for a configuration (admin only)."""
    try:
        current_user = get_current_user()
        logger.info(f"📋 IMAP Logs - Config logs requested | User: {current_user.username} (ID: {current_user.id}) | Config ID: {config_id} | IP: {request.remote_addr}")
        
        config = EmailConfig.query.get(config_id)
        if not config:
            logger.warning(f"⚠️ IMAP Logs - Config not found | User: {current_user.username} | Config ID: {config_id}")
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            }), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        logger.debug(f"📊 IMAP Logs - Query params: page={page}, limit={limit} | Config: '{config.name}' | User: {current_user.username}")
        
        # Query logs with pagination
        logs_query = EmailLog.query.filter_by(config_id=config_id).order_by(EmailLog.created_at.desc())
        logs_paginated = logs_query.paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        logger.info(f"✅ IMAP Logs - Retrieved {len(logs_paginated.items)} logs for config '{config.name}' | User: {current_user.username} | Total: {logs_paginated.total}")
        
        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs_paginated.items],
            'pagination': {
                'page': page,
                'pages': logs_paginated.pages,
                'per_page': limit,
                'total': logs_paginated.total,
                'has_next': logs_paginated.has_next,
                'has_prev': logs_paginated.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Logs Error - Failed to get config logs | User: {getattr(get_current_user(), 'username', 'Unknown')} | Config ID: {config_id} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch email logs',
            'message': str(e)
        }), 500


@bp.route('/logs', methods=['GET'])
@jwt_required()
@require_admin
def get_all_email_logs():
    """Get all email monitoring logs (admin only)."""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        status_filter = request.args.get('status')  # Filter by status
        
        # Build query
        logs_query = EmailLog.query.order_by(EmailLog.created_at.desc())
        
        if status_filter:
            logs_query = logs_query.filter_by(status=status_filter)
        
        # Paginate
        logs_paginated = logs_query.paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        # Include config info in response
        logs_with_config = []
        for log in logs_paginated.items:
            log_dict = log.to_dict()
            log_dict['config_name'] = log.config.name if log.config else 'Unknown'
            logs_with_config.append(log_dict)
        
        return jsonify({
            'success': True,
            'data': logs_with_config,
            'pagination': {
                'page': page,
                'pages': logs_paginated.pages,
                'per_page': limit,
                'total': logs_paginated.total,
                'has_next': logs_paginated.has_next,
                'has_prev': logs_paginated.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch email logs',
            'message': str(e)
        }), 500


@bp.route('/status', methods=['GET'])
@jwt_required()
@require_admin
def get_monitoring_status():
    """Get overall email monitoring status (admin only)."""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        current_user = get_current_user()
        logger.info(f"📊 IMAP Status - Monitoring status requested | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr}")
        
        configs = EmailConfig.query.all()
        
        # Calculate today's date for filtering
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Get email statistics from logs
        total_logs_today = EmailLog.query.filter(
            EmailLog.created_at >= today_start
        ).count()
        
        processed_logs_today = EmailLog.query.filter(
            EmailLog.created_at >= today_start,
            EmailLog.action.in_(['downloaded', 'processed'])
        ).count()
        
        # Get unread emails (errors or ignored)
        unread_logs_today = EmailLog.query.filter(
            EmailLog.created_at >= today_start,
            EmailLog.action.in_(['error', 'ignored'])
        ).count()
        
        # Get last email time
        last_email_log = EmailLog.query.filter(
            EmailLog.email_date.isnot(None)
        ).order_by(EmailLog.email_date.desc()).first()
        
        # Calculate average processing time (rough estimate based on log frequency)
        avg_processing_time = None
        if processed_logs_today > 0:
            # Simple estimate: assume processing happens every hour on average
            avg_processing_time = 60 * 60 / max(processed_logs_today, 1)  # seconds
        
        status_summary = {
            'total_configs': len(configs),
            'active_configs': len([c for c in configs if c.is_active]),
            'inactive_configs': len([c for c in configs if not c.is_active]),
            'configs_with_errors': len([c for c in configs if c.last_error]),
            'emails_today': total_logs_today,
            'emails_processed': processed_logs_today,
            'emails_unread': unread_logs_today,
            'last_email_time': last_email_log.email_date.isoformat() if last_email_log and last_email_log.email_date else None,
            'average_processing_time': avg_processing_time,
            'last_check_times': []
        }
        
        for config in configs:
            if config.last_check:
                status_summary['last_check_times'].append({
                    'config_name': config.name,
                    'last_check': config.last_check.isoformat(),
                    'last_success': config.last_success.isoformat() if config.last_success else None,
                    'has_error': bool(config.last_error),
                    'error_message': config.last_error
                })
        
        logger.info(f"✅ IMAP Status - Status summary sent | User: {current_user.username} | Configs: {len(configs)} | Today's emails: {total_logs_today}")
        
        return jsonify({
            'success': True,
            'data': status_summary
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Status Error - Failed to get monitoring status | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch monitoring status',
            'message': str(e)
        }), 500


@bp.route('/realtime-logs', methods=['GET'])
@bp.route('/realtime-logs/', methods=['GET'])
@jwt_required()
@require_admin
def get_realtime_logs():
    """Get recent email logs for real-time monitoring (admin only)."""
    try:
        from datetime import datetime, timedelta
        
        current_user = get_current_user()
        limit = min(int(request.args.get('limit', 50)), 200)  # Max 200 logs
        since_timestamp = request.args.get('since')  # Unix timestamp
        
        logger.info(f"📡 IMAP Monitor - Realtime logs requested | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr} | Limit: {limit}")
        
        # Get logs from the last 24 hours, ordered by most recent
        since = datetime.now() - timedelta(hours=24)
        
        # Build query
        logs_query = EmailLog.query.filter(EmailLog.created_at >= since)
        
        # If since timestamp provided, get only logs after that time
        if since_timestamp:
            try:
                since_dt = datetime.fromtimestamp(float(since_timestamp))
                logs_query = logs_query.filter(EmailLog.created_at > since_dt)
                logger.debug(f"📊 IMAP Monitor - Filtering logs since {since_dt} | User: {current_user.username}")
            except (ValueError, TypeError):
                logger.warning(f"⚠️ IMAP Monitor - Invalid timestamp '{since_timestamp}' | User: {current_user.username}")
                pass
        
        # Get logs with config info
        logs = logs_query.join(EmailConfig).add_columns(
            EmailConfig.name.label('config_name'),
            EmailConfig.email.label('config_email')
        ).order_by(EmailLog.created_at.desc()).limit(limit).all()
        
        logger.debug(f"📊 IMAP Monitor - Retrieved {len(logs)} logs | User: {current_user.username}")
        
        # Format logs
        formatted_logs = []
        for log, config_name, config_email in logs:
            log_dict = log.to_dict()
            log_dict['config_name'] = config_name
            log_dict['config_email'] = config_email
            
            # Add filter reason for ignored emails
            if log.action == 'ignored':
                log_dict['filter_reason'] = log.message or 'Email filtered out'
            
            # Add processing details
            log_dict['timestamp'] = log.created_at.timestamp()
            
            formatted_logs.append(log_dict)
        
        logger.info(f"✅ IMAP Monitor - Realtime logs sent | User: {current_user.username} | Count: {len(formatted_logs)}")
        
        return jsonify({
            'success': True,
            'data': {
                'logs': formatted_logs,
                'count': len(formatted_logs),
                'server_time': datetime.now().timestamp()
            }
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Monitor Error - Realtime logs failed | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch realtime logs',
            'message': str(e)
        }), 500


@bp.route('/simulate-email', methods=['POST'])
@bp.route('/simulate-email/', methods=['POST'])
@jwt_required()
@require_admin 
def simulate_email():
    """Simulate an incoming email for testing real-time monitoring (admin only)."""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        config_id = data.get('config_id')
        email_subject = data.get('subject', 'Test Email Subject')
        email_sender = data.get('sender', 'test@example.com')
        action = data.get('action', 'processed')  # 'processed', 'ignored', 'error'
        
        logger.info(f"🧪 IMAP Simulate - Email simulation requested | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr}")
        logger.debug(f"📧 IMAP Simulate - Details: Config ID: {config_id}, Subject: '{email_subject}', Sender: {email_sender}, Action: {action}")
        
        if not config_id:
            logger.warning(f"⚠️ IMAP Simulate - Missing config_id | User: {current_user.username}")
            return jsonify({
                'success': False,
                'error': 'config_id is required'
            }), 400
        
        # Verify config exists
        config = EmailConfig.query.get(config_id)
        if not config:
            logger.warning(f"⚠️ IMAP Simulate - Config not found | User: {current_user.username} | Config ID: {config_id}")
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            }), 404
        
        # Create simulated log entry
        status = 'success' if action == 'processed' else 'warning' if action == 'ignored' else 'error'
        message = None
        
        if action == 'ignored':
            message = data.get('filter_reason', 'Email does not match filters')
        elif action == 'error':
            message = data.get('error_message', 'Processing error occurred')
        
        log = EmailLog.log_activity(
            config_id=config_id,
            action=action,
            status=status,
            message=message,
            email_subject=email_subject,
            email_sender=email_sender,
            email_date=datetime.now()
        )
        
        logger.info(f"✅ IMAP Simulate - Email simulation created | User: {current_user.username} | Config: '{config.name}' | Log ID: {log.id} | Action: {action}")
        
        return jsonify({
            'success': True,
            'data': {
                'log_id': log.id,
                'message': 'Email simulation created successfully'
            }
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Simulate Error - Simulation failed | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to simulate email',
            'message': str(e)
        }), 500


@bp.route('/monitor/start', methods=['POST'])
@bp.route('/monitor/start/', methods=['POST'])
@jwt_required()
@require_admin
def start_monitoring():
    """Start background email monitoring (admin only)."""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        interval = data.get('interval_seconds', 300)  # Default 5 minutes
        
        logger.info(f"🚀 IMAP Monitor - Start requested | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr} | Interval: {interval}s")
        
        # Start the monitoring service
        imap_service.start_monitoring(interval_seconds=interval)
        
        logger.info(f"✅ IMAP Monitor - Started successfully | User: {current_user.username} | Interval: {interval}s")
        
        return jsonify({
            'success': True,
            'message': 'Email monitoring started successfully',
            'data': {
                'interval_seconds': interval,
                'monitoring_active': imap_service.monitoring_active
            }
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Monitor Error - Failed to start monitoring | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to start email monitoring',
            'message': str(e)
        }), 500


@bp.route('/monitor/stop', methods=['POST'])
@bp.route('/monitor/stop/', methods=['POST'])
@jwt_required()
@require_admin
def stop_monitoring():
    """Stop background email monitoring (admin only)."""
    try:
        current_user = get_current_user()
        logger.info(f"🛑 IMAP Monitor - Stop requested | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr}")
        
        # Stop the monitoring service
        imap_service.stop_monitoring()
        
        logger.info(f"✅ IMAP Monitor - Stopped successfully | User: {current_user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Email monitoring stopped successfully',
            'data': {
                'monitoring_active': imap_service.monitoring_active
            }
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Monitor Error - Failed to stop monitoring | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to stop email monitoring',
            'message': str(e)
        }), 500


@bp.route('/monitor/status', methods=['GET'])
@bp.route('/monitor/status/', methods=['GET'])
@jwt_required()
@require_admin
def get_monitor_status():
    """Get current monitoring status (admin only)."""
    try:
        current_user = get_current_user()
        logger.debug(f"📊 IMAP Monitor - Status requested | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr}")
        
        return jsonify({
            'success': True,
            'data': {
                'monitoring_active': imap_service.monitoring_active,
                'check_interval': imap_service.check_interval,
                'thread_alive': imap_service.monitor_thread.is_alive() if imap_service.monitor_thread else False
            }
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Monitor Error - Failed to get status | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get monitoring status',
            'message': str(e)
        }), 500


@bp.route('/<int:config_id>/check', methods=['POST'])
@jwt_required()
@require_admin
def manual_email_check(config_id):
    """Manually check emails for a specific configuration (admin only)."""
    try:
        current_user = get_current_user()
        logger.info(f"🔍 IMAP Manual - Check requested | User: {current_user.username} (ID: {current_user.id}) | Config ID: {config_id} | IP: {request.remote_addr}")
        
        config = EmailConfig.query.get(config_id)
        if not config:
            logger.warning(f"⚠️ IMAP Manual - Config not found | User: {current_user.username} | Config ID: {config_id}")
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            }), 404
        
        logger.info(f"📧 IMAP Manual - Starting check for config '{config.name}' | Email Account: {config.email} | Server: {config.imap_server}:{config.imap_port} | User: {current_user.username}")
        
        # Perform manual check using the monitoring service
        result = imap_service.check_config_emails(config)
        
        logger.info(f"✅ IMAP Manual - Check completed | User: {current_user.username} | Config: '{config.name}' | Email Account: {config.email} | New emails: {result.get('new_emails', 0)} | Processed: {result.get('processed', 0)}")
        
        return jsonify({
            'success': True,
            'message': 'Email check completed successfully',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Manual Error - Check failed | User: {getattr(get_current_user(), 'username', 'Unknown')} | Config ID: {config_id} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to check emails',
            'message': str(e)
        }), 500


@bp.route('/monitor/continuous/start', methods=['POST'])
@bp.route('/monitor/continuous/start/', methods=['POST'])
@jwt_required()
@require_admin
def start_continuous_monitoring():
    """Start continuous email monitoring every 5 seconds (admin only)."""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        interval = data.get('interval_seconds', 5)  # Default 5 seconds like user's script
        
        logger.info(f"🚀 IMAP Continuous - Start requested | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr} | Interval: {interval}s")
        
        # Start the continuous monitoring service
        imap_service.start_continuous_monitoring(interval_seconds=interval)
        
        logger.info(f"✅ IMAP Continuous - Started successfully | User: {current_user.username} | Interval: {interval}s | Mode: Real-time")
        
        return jsonify({
            'success': True,
            'message': 'Continuous email monitoring started successfully',
            'data': {
                'interval_seconds': interval,
                'continuous_monitoring_active': imap_service.continuous_monitoring,
                'mode': 'real_time'
            }
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Continuous Error - Failed to start | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to start continuous email monitoring',
            'message': str(e)
        }), 500


@bp.route('/monitor/continuous/stop', methods=['POST'])
@bp.route('/monitor/continuous/stop/', methods=['POST'])
@jwt_required()
@require_admin
def stop_continuous_monitoring():
    """Stop continuous email monitoring (admin only)."""
    try:
        current_user = get_current_user()
        logger.info(f"🛑 IMAP Continuous - Stop requested | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr}")
        
        # Stop the continuous monitoring service
        imap_service.stop_continuous_monitoring()
        
        logger.info(f"✅ IMAP Continuous - Stopped successfully | User: {current_user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Continuous email monitoring stopped successfully',
            'data': {
                'continuous_monitoring_active': imap_service.continuous_monitoring
            }
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Continuous Error - Failed to stop | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to stop continuous email monitoring',
            'message': str(e)
        }), 500


@bp.route('/monitor/continuous/status', methods=['GET'])
@bp.route('/monitor/continuous/status/', methods=['GET'])
@jwt_required()
@require_admin
def get_continuous_monitor_status():
    """Get current continuous monitoring status (admin only)."""
    try:
        current_user = get_current_user()
        logger.debug(f"📊 IMAP Continuous - Status requested | User: {current_user.username} (ID: {current_user.id}) | IP: {request.remote_addr}")
        
        return jsonify({
            'success': True,
            'data': {
                'continuous_monitoring_active': imap_service.continuous_monitoring,
                'regular_monitoring_active': imap_service.monitoring_active,
                'check_interval': imap_service.check_interval,
                'continuous_thread_alive': imap_service.continuous_thread.is_alive() if imap_service.continuous_thread else False,
                'regular_thread_alive': imap_service.monitor_thread.is_alive() if imap_service.monitor_thread else False
            }
        })
        
    except Exception as e:
        logger.error(f"❌ IMAP Continuous Error - Failed to get status | User: {getattr(get_current_user(), 'username', 'Unknown')} | Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get continuous monitoring status',
            'message': str(e)
        }), 500
