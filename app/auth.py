from flask import Blueprint, current_app, url_for, redirect, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app.models import User, db
from app import oauth

auth = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token:
            return jsonify({'error': 'API token is missing'}), 401
            
        user = User.verify_api_token(token)
        if not user:
            return jsonify({'error': 'Invalid API token'}), 401
            
        return f(*args, **kwargs)
    return decorated

@auth.route('/api/token', methods=['GET', 'POST'])
@login_required
def generate_token():
    """Generate a new API token for the authenticated user"""
    token = current_user.generate_api_token()
    return jsonify({'token': token})

@auth.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    return github.authorize_redirect(url_for('auth.login_github_callback', _external=True))

@auth.route('/login/github/callback')
def login_github_callback():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    # Get user profile
    resp = github.get('user', token=token)
    profile = resp.json()
    
    # Get user email
    emails_resp = github.get('user/emails', token=token)
    emails = emails_resp.json()
    primary_email = next(email['email'] for email in emails if email['primary'])
    
    user = User.query.filter_by(oauth_id=str(profile['id']), oauth_provider='github').first()
    if not user:
        user = User(
            email=primary_email,
            name=profile.get('name', profile.get('login')),
            oauth_provider='github',
            oauth_id=str(profile['id'])
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('main.index'))

@auth.route('/login/linkedin')
def linkedin_login():
    linkedin = oauth.create_client('linkedin')
    return linkedin.authorize_redirect(url_for('auth.login_linkedin_callback', _external=True))

@auth.route('/login/linkedin/callback')
def login_linkedin_callback():
    linkedin = oauth.create_client('linkedin')
    token = linkedin.authorize_access_token()
    resp = linkedin.get('me')
    user_info = resp.json()
    
    # Get email from separate endpoint
    email_resp = linkedin.get('emailAddress', params={'q': 'members', 'projection': '(elements*(handle~))'})
    email_info = email_resp.json()
    email = email_info['elements'][0]['handle~']['emailAddress']
    
    user = User.query.filter_by(oauth_id=user_info['id'], oauth_provider='linkedin').first()
    if not user:
        user = User(
            email=email,
            name=f"{user_info.get('localizedFirstName', '')} {user_info.get('localizedLastName', '')}",
            oauth_provider='linkedin',
            oauth_id=user_info['id']
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('main.index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Successfully logged out'}) 