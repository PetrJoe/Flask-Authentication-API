from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from models.user import User
from database import Base, engine
from flask_migrate import Migrate
from swagger import swagger_ui_blueprint

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)


# Configuration
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Register Swagger UI blueprint
app.register_blueprint(swagger_ui_blueprint)

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Reflect Base to work with Flask-Migrate
Base.metadata.bind = engine
Base.metadata.create_all(engine)
# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split()[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.session.query(User).filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# User Registration
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400

        if '@' not in data['email']:
            return jsonify({'message': 'Invalid email format'}), 400

        # Validate password length
        if len(data['password']) < 8:
            return jsonify({'message': 'Password must be at least 8 characters long'}), 400

        # Validate phone number if provided
        if data.get('phone'):
            if not data['phone'].isdigit() or len(data['phone']) < 11:
                return jsonify({'message': 'Phone number must be at least 11 digits'}), 400

        if db.session.query(User).filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 409

        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            email=data['email'],
            password=hashed_password,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    finally:
        db.session.close()

# User Login
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        # Check if all required fields are present
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400

        user = db.session.query(User).filter_by(email=data['email']).first()
        if user and check_password_hash(user.password, data['password']):
            access_token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.now(timezone.utc) + app.config['JWT_ACCESS_TOKEN_EXPIRES']
            }, app.config['SECRET_KEY']).decode('utf-8')
            
            refresh_token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.now(timezone.utc) + app.config['JWT_REFRESH_TOKEN_EXPIRES']
            }, app.config['SECRET_KEY']).decode('utf-8')

            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            })

        return jsonify({'message': 'Invalid credentials'}), 401
    finally:
        db.session.close()

# Refresh Token
@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    refresh_token = request.json.get('refresh_token')
    try:
        data = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user = db.session.query(User).filter_by(id=data['user_id']).first()

        access_token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }, app.config['SECRET_KEY'])

        return jsonify({'access_token': access_token})
    except:
        return jsonify({'message': 'Invalid refresh token'}), 401

# Password Reset Request
@app.route('/api/auth/password-reset-request', methods=['POST'])
def password_reset_request():
    data = request.get_json()
    user = db.session.query(User).filter_by(email=data['email']).first()
    
    if user:
        # Generate password reset token
        reset_token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'])
        
        # In production, send this token via email
        # For demo, we'll return it
        return jsonify({
            'message': 'Password reset link sent',
            'reset_token': reset_token
        })
    
    return jsonify({'message': 'Email not found'}), 404

# Password Reset
@app.route('/api/auth/password-reset', methods=['POST'])
def password_reset():
    data = request.get_json()
    try:
        token_data = jwt.decode(data['reset_token'], app.config['SECRET_KEY'], algorithms=["HS256"])
        user = db.session.query(User).filter_by(id=token_data['user_id']).first()
        
        if user:
            user.password = generate_password_hash(data['new_password'])
            db.session.commit()
            return jsonify({'message': 'Password reset successful'})
        
        return jsonify({'message': 'User not found'}), 404
    except:
        return jsonify({'message': 'Invalid or expired reset token'}), 401

# Protected route example
@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify(current_user.to_dict())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)