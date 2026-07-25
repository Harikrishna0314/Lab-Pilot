from flask import Blueprint, request, jsonify
from services.auth_service import register_user, authenticate_user
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required.'}), 400

    result, err = register_user(name, email, password, role)
    if err:
        return jsonify({'error': err}), 400

    return jsonify(result), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    result, err = authenticate_user(email, password)
    if err:
        return jsonify({'error': err}), 401

    return jsonify(result), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    claims = get_jwt()
    return jsonify({
        'user': {
            'id': int(user_id),
            'email': claims.get('email'),
            'name': claims.get('name'),
            'role': claims.get('role')
        }
    }), 200
