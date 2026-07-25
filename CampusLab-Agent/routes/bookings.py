from flask import Blueprint, request, jsonify
from services import booking_service
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/book', methods=['POST'])
@jwt_required()
def book_system():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    lab_id = data.get('lab_id')
    system_number = data.get('system_number')
    booking_date = data.get('booking_date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    if not lab_id or not booking_date or not start_time or not end_time:
        return jsonify({'error': 'lab_id, booking_date, start_time, and end_time are required.'}), 400

    booking, err, conflict = booking_service.create_booking(
        user_id=user_id,
        lab_id=lab_id,
        system_number=system_number,
        booking_date_str=booking_date,
        start_time_str=start_time,
        end_time_str=end_time
    )

    if err:
        response = {'error': err}
        if conflict:
            response['conflict_resolution'] = conflict
        return jsonify(response), 409 if conflict else 400

    return jsonify(booking), 201

@bookings_bp.route('/booking/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    is_admin = (claims.get('role') == 'admin')

    data = request.get_json() or {}
    new_date = data.get('booking_date')
    new_start = data.get('start_time')
    new_end = data.get('end_time')
    new_sys_num = data.get('system_number')

    booking, err, conflict = booking_service.modify_booking(
        booking_id=booking_id,
        user_id=user_id,
        is_admin=is_admin,
        new_date_str=new_date,
        new_start_str=new_start,
        new_end_str=new_end,
        new_system_number=new_sys_num
    )

    if err:
        response = {'error': err}
        if conflict:
            response['conflict_resolution'] = conflict
        return jsonify(response), 409 if conflict else 400

    return jsonify(booking), 200

@bookings_bp.route('/booking/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def delete_booking(booking_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    is_admin = (claims.get('role') == 'admin')

    booking, err = booking_service.cancel_booking(booking_id=booking_id, user_id=user_id, is_admin=is_admin)
    if err:
        return jsonify({'error': err}), 400

    return jsonify({'message': 'Booking cancelled successfully.', 'booking': booking}), 200

@bookings_bp.route('/bookings', methods=['GET'])
@jwt_required()
def list_bookings():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    status = request.args.get('status')
    
    # Students & Faculty view their own bookings by default; Admin views all
    filter_user_id = user_id if role in ['student', 'faculty'] else request.args.get('user_id', type=int)

    bookings = booking_service.get_user_bookings(user_id=filter_user_id, status=status)
    return jsonify(bookings), 200
