from flask import Blueprint, request, jsonify
from services import lab_service
from flask_jwt_extended import jwt_required, get_jwt

labs_bp = Blueprint('labs', __name__)

@labs_bp.route('/labs', methods=['GET'])
def list_labs():
    labs = lab_service.get_all_labs()
    return jsonify(labs), 200

@labs_bp.route('/labs/<int:lab_id>', methods=['GET'])
def get_lab(lab_id):
    lab_data, err = lab_service.get_lab_by_id(lab_id)
    if err:
        return jsonify({'error': err}), 404
    return jsonify(lab_data), 200

@labs_bp.route('/labs', methods=['POST'])
@jwt_required()
def create_lab():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin authorization required.'}), 403

    data = request.get_json() or {}
    name = data.get('name')
    capacity = data.get('capacity')
    open_time = data.get('open_time', '08:00')
    close_time = data.get('close_time', '20:00')
    description = data.get('description', '')

    if not name or not capacity:
        return jsonify({'error': 'Lab name and capacity are required.'}), 400

    lab, err = lab_service.create_lab(name, int(capacity), open_time, close_time, description)
    if err:
        return jsonify({'error': err}), 400

    return jsonify(lab), 201
