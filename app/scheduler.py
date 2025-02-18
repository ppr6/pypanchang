from flask_apscheduler import APScheduler
from datetime import datetime
from flask import current_app

scheduler = APScheduler()

def send_daily_panchang_emails():
    """Send daily panchang emails to all active subscribers"""
    from app.models import Subscription
    from app.panchang import get_panchang_data
    from app.email_service import send_panchang_email
    
    with scheduler.app.app_context():
        # Get all active subscriptions
        subscriptions = Subscription.query.filter_by(is_active=True).all()
        
        for subscription in subscriptions:
            try:
                # Get panchang data
                panchang_data = get_panchang_data(subscription.location_id)
                if not panchang_data:
                    current_app.logger.error(
                        f"Failed to fetch panchang data for location {subscription.location_id}"
                    )
                    continue
                
                # Send email to subscription email
                success = send_panchang_email(
                    subscription.email,
                    subscription.city_name,
                    panchang_data
                )
                
                if success:
                    # Update last_sent timestamp
                    subscription.last_sent = datetime.utcnow()
                    scheduler.app.db.session.commit()
                
            except Exception as e:
                current_app.logger.error(
                    f"Error processing subscription {subscription.id}: {str(e)}"
                )
                continue

def init_scheduler(app):
    """Initialize the scheduler with the Flask app"""
    scheduler.init_app(app)
    
    # Add job to send emails every minute (for testing)
    scheduler.add_job(
        id='send_daily_panchang',
        func=send_daily_panchang_emails,
        trigger='interval',
        minutes=1
    )
    
    scheduler.start() 