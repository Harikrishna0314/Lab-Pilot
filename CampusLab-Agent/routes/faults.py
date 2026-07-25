from flask import Blueprint, request, jsonify
from services import fault_service
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

faults_bp = Blueprint('faults', __name__)

@faults_bp.route('/fault', methods=['POST'])
@jwt_required()
def create_fault_report():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    system_id = data.get('system_id')
    issue_type = data.get('issue_type')
    description = data.get('description', '')

    if not system_id or not issue_type:
        return jsonify({'error': 'system_id and issue_type are required.'}), 400

    report, err = fault_service.report_fault(system_id, user_id, issue_type, description)
    if err:
        return jsonify({'error': err}), 400

    return jsonify(report), 201

@faults_bp.route('/faults', methods=['GET'])
@jwt_required()
def list_fault_reports():
    status = request.args.get('status')
    lab_id = request.args.get('lab_id')

    reports = fault_service.get_fault_reports(status=status, lab_id=lab_id)
    return jsonify(reports), 200

@faults_bp.route('/fault/<int:report_id>', methods=['PATCH'])
@jwt_required()
def update_fault(report_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin authorization required.'}), 403

    data = request.get_json() or {}
    status = data.get('status')

    if not status:
        return jsonify({'error': 'Status is required.'}), 400

    report, err = fault_service.update_fault_status(report_id, status)
    if err:
        return jsonify({'error': err}), 400

    return jsonify(report), 200
