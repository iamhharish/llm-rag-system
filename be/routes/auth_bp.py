from flask import Blueprint, jsonify, request
from models import db, User


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input provided'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    
    if not username or not email or not password or not phone :
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    if User.query.filter((User.username == username) | (User.email == email) | (User.phone == phone)).first():
        return jsonify({'error': 'Username, email, or phone already exists'}), 400
    
    new_user = User(username=username, email=email, password=password, phone=phone)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input provided'}), 400
    username_or_email = data.get('username_or_email')
    password = data.get('password')
    
    if not username_or_email or not password:
        return jsonify({'error': 'Username/email and password are required'}), 400
    
    user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
    
    if not user or user.password != password:
        return jsonify({'error': 'Invalid username/email or password'}), 401
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone
    }), 200