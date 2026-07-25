from models import db, Booking, System, Lab, User
from datetime import datetime, date, time, timedelta

def check_time_overlap(start1, end1, start2, end2):
    """Check if two time intervals overlap (assuming same date)"""
    return max(start1, start2) < min(end1, end2)

def is_system_available(system_id, booking_date, start_time, end_time, exclude_booking_id=None):
    """Check if a specific system is free from overlapping active bookings and not faulty"""
    system = System.query.get(system_id)
    if not system:
        return False, "System does not exist."
    if system.status == 'faulty':
        return False, "System is marked as faulty and cannot be booked."

    # Check lab timings
    lab = system.lab
    if start_time < lab.open_time or end_time > lab.close_time:
        return False, f"Booking time must be within lab operating hours ({lab.open_time.strftime('%H:%M')} - {lab.close_time.strftime('%H:%M')})."

    query = Booking.query.filter(
        Booking.system_id == system_id,
        Booking.booking_date == booking_date,
        Booking.status == 'active'
    )
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)

    existing_bookings = query.all()
    for b in existing_bookings:
        if check_time_overlap(start_time, end_time, b.start_time, b.end_time):
            return False, f"System {system.system_number} is already reserved between {b.start_time.strftime('%H:%M')} and {b.end_time.strftime('%H:%M')}."

    return True, None

def find_alternative_seats(lab_id, booking_date, start_time, end_time):
    """Suggest alternative available systems in the same lab for the requested slot"""
    systems = System.query.filter_by(lab_id=lab_id, status='available').order_by(System.system_number).all()
    available_seats = []
    for s in systems:
        avail, _ = is_system_available(s.id, booking_date, start_time, end_time)
        if avail:
            available_seats.append(s.system_number)
    return available_seats

def find_alternative_timings(system_id, booking_date, duration_minutes=60):
    """Suggest alternative available time slots for the requested system on the given date"""
    system = System.query.get(system_id)
    if not system or system.status == 'faulty':
        return []

    lab = system.lab
    suggestions = []
    
    current_dt = datetime.combine(booking_date, lab.open_time)
    end_dt = datetime.combine(booking_date, lab.close_time)
    step = timedelta(minutes=30)
    slot_len = timedelta(minutes=duration_minutes)

    while current_dt + slot_len <= end_dt:
        slot_start = current_dt.time()
        slot_end = (current_dt + slot_len).time()
        
        avail, _ = is_system_available(system.id, booking_date, slot_start, slot_end)
        if avail:
            suggestions.append({
                "start_time": slot_start.strftime("%H:%M"),
                "end_time": slot_end.strftime("%H:%M")
            })
            if len(suggestions) >= 4: # Limit suggestions
                break
        current_dt += step

    return suggestions

def create_booking(user_id, lab_id, system_number, booking_date_str, start_time_str, end_time_str):
    try:
        if isinstance(booking_date_str, str):
            b_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
        else:
            b_date = booking_date_str

        start_t = datetime.strptime(start_time_str, "%H:%M").time() if isinstance(start_time_str, str) else start_time_str
        end_t = datetime.strptime(end_time_str, "%H:%M").time() if isinstance(end_time_str, str) else end_time_str
    except ValueError:
        return None, "Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time.", None

    if start_t >= end_t:
        return None, "Start time must be before end time.", None

    if b_date < date.today():
        return None, "Cannot book systems for past dates.", None

    # Check if system exists or auto-assign if system_number not provided
    if system_number:
        system = System.query.filter_by(lab_id=lab_id, system_number=system_number).first()
        if not system:
            return None, f"System number {system_number} does not exist in lab ID {lab_id}.", None
    else:
        # Auto assign first available system
        alt_seats = find_alternative_seats(lab_id, b_date, start_t, end_t)
        if not alt_seats:
            return None, "No systems available in this lab for the selected time slot.", None
        system_number = alt_seats[0]
        system = System.query.filter_by(lab_id=lab_id, system_number=system_number).first()

    # Prevent double booking for same user at overlapping time
    user_conflict = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.booking_date == b_date,
        Booking.status == 'active'
    ).all()
    for uc in user_conflict:
        if check_time_overlap(start_t, end_t, uc.start_time, uc.end_time):
            return None, f"You already have an active booking on {b_date} from {uc.start_time.strftime('%H:%M')} to {uc.end_time.strftime('%H:%M')}.", None

    # Verify system availability
    avail, reason = is_system_available(system.id, b_date, start_t, end_t)
    if not avail:
        # Generate alternatives
        alt_seats = find_alternative_seats(lab_id, b_date, start_t, end_t)
        duration = int((datetime.combine(date.min, end_t) - datetime.combine(date.min, start_t)).total_seconds() / 60)
        alt_times = find_alternative_timings(system.id, b_date, duration)
        
        conflict_details = {
            "reason": reason,
            "alternative_seats": alt_seats,
            "alternative_timings": alt_times
        }
        return None, f"Booking Conflict: {reason}", conflict_details

    # Create booking
    booking = Booking(
        user_id=user_id,
        system_id=system.id,
        booking_date=b_date,
        start_time=start_t,
        end_time=end_t,
        status='active'
    )
    db.session.add(booking)
    db.session.commit()

    return booking.to_dict(), None, None

def cancel_booking(booking_id, user_id=None, is_admin=False):
    booking = Booking.query.get(booking_id)
    if not booking:
        return None, "Booking not found."
    
    if not is_admin and user_id and booking.user_id != user_id:
        return None, "Unauthorized to cancel this booking."

    if booking.status == 'cancelled':
        return None, "Booking is already cancelled."

    booking.status = 'cancelled'
    db.session.commit()
    return booking.to_dict(), None

def modify_booking(booking_id, user_id=None, is_admin=False, new_date_str=None, new_start_str=None, new_end_str=None, new_system_number=None):
    booking = Booking.query.get(booking_id)
    if not booking:
        return None, "Booking not found.", None
    
    if not is_admin and user_id and booking.user_id != user_id:
        return None, "Unauthorized to modify this booking.", None

    if booking.status != 'active':
        return None, "Only active bookings can be modified.", None

    # Determine new parameters
    b_date = datetime.strptime(new_date_str, "%Y-%m-%d").date() if new_date_str else booking.booking_date
    start_t = datetime.strptime(new_start_str, "%H:%M").time() if new_start_str else booking.start_time
    end_t = datetime.strptime(new_end_str, "%H:%M").time() if new_end_str else booking.end_time

    if start_t >= end_t:
        return None, "Start time must be before end time.", None

    system_id = booking.system_id
    if new_system_number:
        sys_obj = System.query.filter_by(lab_id=booking.system.lab_id, system_number=new_system_number).first()
        if not sys_obj:
            return None, f"System number {new_system_number} not found in lab.", None
        system_id = sys_obj.id

    # Availability check excluding current booking ID
    avail, reason = is_system_available(system_id, b_date, start_t, end_t, exclude_booking_id=booking.id)
    if not avail:
        alt_seats = find_alternative_seats(booking.system.lab_id, b_date, start_t, end_t)
        duration = int((datetime.combine(date.min, end_t) - datetime.combine(date.min, start_t)).total_seconds() / 60)
        alt_times = find_alternative_timings(system_id, b_date, duration)
        return None, f"Modification Conflict: {reason}", {"alternative_seats": alt_seats, "alternative_timings": alt_times}

    booking.booking_date = b_date
    booking.start_time = start_t
    booking.end_time = end_t
    booking.system_id = system_id
    db.session.commit()

    return booking.to_dict(), None, None

def get_user_bookings(user_id=None, status=None, upcoming_only=False):
    query = Booking.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    if upcoming_only:
        query = query.filter(Booking.booking_date >= date.today())
    
    bookings = query.order_by(Booking.booking_date.desc(), Booking.start_time.desc()).all()
    return [b.to_dict() for b in bookings]
