from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import db, Subscription, User
from app.panchang import get_panchang_data
from app.auth import token_required
from datetime import datetime
import requests

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify({'message': 'Welcome to Panchang API'})

@main.route('/api/panchang')
def get_panchang():
    """Get panchang data for a specific location and date"""
    location_id = request.args.get('location_id')
    date_str = request.args.get('date')
    
    if not location_id:
        return jsonify({'error': 'location_id is required'}), 400
    
    try:
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date = None
            
        data = get_panchang_data(location_id, date)
        if data is None:
            return jsonify({'error': 'Failed to fetch panchang data'}), 500
            
        return jsonify(data)
        
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

@main.route('/api/subscribe', methods=['POST'])
@token_required
def subscribe():
    """Subscribe to daily panchang emails for a location"""
    data = request.get_json()
    location_id = data.get('location_id')
    city_name = data.get('city_name')
    email = data.get('email')
    
    if not location_id or not city_name or not email:
        return jsonify({'error': 'location_id, city_name, and email are required'}), 400
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Get user from token
    token = request.headers.get('X-API-Token')
    user = User.verify_api_token(token)
    
    # Check if subscription already exists
    existing_sub = Subscription.query.filter_by(
        user_id=user.id,
        location_id=location_id,
        email=email,
        is_active=True
    ).first()
    
    if existing_sub:
        return jsonify({'message': 'Already subscribed to this location with this email'}), 400
    
    # Create new subscription
    subscription = Subscription(
        user_id=user.id,
        location_id=location_id,
        city_name=city_name,
        email=email
    )
    
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({
        'message': 'Successfully subscribed',
        'subscription_id': subscription.id
    })

@main.route('/api/subscriptions', methods=['GET'])
@token_required
def get_subscriptions():
    """Get user's active subscriptions"""
    token = request.headers.get('X-API-Token')
    user = User.verify_api_token(token)
    
    subscriptions = Subscription.query.filter_by(
        user_id=user.id,
        is_active=True
    ).all()
    
    return jsonify([{
        'id': sub.id,
        'location_id': sub.location_id,
        'city_name': sub.city_name,
        'email': sub.email,
        'created_at': sub.created_at.isoformat()
    } for sub in subscriptions])

@main.route('/api/subscriptions/<int:subscription_id>', methods=['DELETE'])
@token_required
def unsubscribe(subscription_id):
    """Unsubscribe from daily panchang emails"""
    token = request.headers.get('X-API-Token')
    user = User.verify_api_token(token)
    
    subscription = Subscription.query.filter_by(
        id=subscription_id,
        user_id=user.id
    ).first_or_404()
    
    subscription.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Successfully unsubscribed'})

@main.route('/api/locations')
def get_location_id():
    """Get location ID for a given city name"""
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'city parameter is required'}), 400
        
    try:
        response = requests.get(
            'https://mypanchang.com/newsite/placequery.php',
            params={'place': city}
        )
        response.raise_for_status()
        
        # Handle empty response
        if not response.text.strip():
            return jsonify([]), 200
            
        try:
            return jsonify(response.json())
        except ValueError:
            # If JSON parsing fails, return empty list
            return jsonify([]), 200
            
    except requests.RequestException as e:
        current_app.logger.error(f"Error fetching location data: {str(e)}")
        return jsonify({'error': 'Failed to fetch location data'}), 500 