from flask import Blueprint, request, jsonify
from ai.assistant import process_chat_message
from flask_jwt_extended import jwt_required, get_jwt_identity

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat_endpoint():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message cannot be empty.'}), 400

    result = process_chat_message(user_id=user_id, user_message=message)
    return jsonify(result), 200
