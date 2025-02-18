from flask_login import UserMixin
from datetime import datetime
import secrets
from app import db, login_manager

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    oauth_provider = db.Column(db.String(20))  # 'github' or 'linkedin'
    oauth_id = db.Column(db.String(120), unique=True)
    api_token = db.Column(db.String(64), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)

    def generate_api_token(self):
        """Generate a new API token for the user"""
        self.api_token = secrets.token_hex(32)
        db.session.commit()
        return self.api_token

    @staticmethod
    def verify_api_token(token):
        """Verify an API token and return the associated user"""
        if not token:
            return None
        return User.query.filter_by(api_token=token).first()

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location_id = db.Column(db.String(20), nullable=False)
    city_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)  # Email to receive panchang
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_sent = db.Column(db.DateTime) 