from flask import Blueprint, request, jsonify
from services import lab_service
from flask_jwt_extended import jwt_required, get_jwt

systems_bp = Blueprint('systems', __name__)

@systems_bp.route('/systems', methods=['GET'])
def list_systems():
    lab_id = request.args.get('lab_id', type=int)
    status = request.args.get('status')
    systems = lab_service.get_systems(lab_id=lab_id, status=status)
    return jsonify(systems), 200

@systems_bp.route('/systems/<int:system_id>', methods=['PATCH'])
@jwt_required()
def patch_system(system_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin authorization required.'}), 403

    data = request.get_json() or {}
    status = data.get('status')
    if not status:
        return jsonify({'error': 'Status field is required.'}), 400

    system, err = lab_service.update_system_status(system_id, status)
    if err:
        return jsonify({'error': err}), 400

    return jsonify(system), 200
