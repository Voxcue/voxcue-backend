import os
from flask import Blueprint, request, jsonify
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app.models import User
from app import db

auth = Blueprint('auth', __name__)

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

# Generate JWT token
def generate_token(user_id: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({"user_id": user_id, "exp": expiration}, SECRET_KEY, algorithm="HS256")
    return token

# Register user
@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400
    
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully"}), 201

# Login user
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = generate_token(user.id)
    
    return jsonify({"token": token}), 200

# Protected route (authentication check)
def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"error": "Token is missing"}), 403
        
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(id=decoded_token['user_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorator
