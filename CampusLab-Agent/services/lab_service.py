from models import db, Lab, System, Booking
from datetime import datetime, date, time

def create_lab(name, capacity, open_time_str, close_time_str, description=""):
    existing = Lab.query.filter_by(name=name).first()
    if existing:
        return None, f"Lab with name '{name}' already exists."

    try:
        open_time = datetime.strptime(open_time_str, "%H:%M").time()
        close_time = datetime.strptime(close_time_str, "%H:%M").time()
    except ValueError:
        return None, "Invalid time format. Use HH:MM format."

    lab = Lab(name=name, capacity=capacity, open_time=open_time, close_time=close_time, description=description)
    db.session.add(lab)
    db.session.flush() # get lab.id

    # Auto-generate systems for the lab
    for sys_num in range(1, capacity + 1):
        system = System(lab_id=lab.id, system_number=sys_num, status='available')
        db.session.add(system)

    db.session.commit()
    return lab.to_dict(), None

def get_all_labs():
    labs = Lab.query.all()
    return [l.to_dict() for l in labs]

def get_lab_by_id(lab_id):
    lab = Lab.query.get(lab_id)
    if not lab:
        return None, "Lab not found."
    
    lab_data = lab.to_dict()
    systems = System.query.filter_by(lab_id=lab_id).order_by(System.system_number).all()
    lab_data['systems'] = [s.to_dict() for s in systems]
    return lab_data, None

def get_systems(lab_id=None, status=None):
    query = System.query
    if lab_id:
        query = query.filter_by(lab_id=lab_id)
    if status:
        query = query.filter_by(status=status)
    
    systems = query.order_by(System.lab_id, System.system_number).all()
    return [s.to_dict() for s in systems]

def update_system_status(system_id, status):
    if status not in ['available', 'reserved', 'faulty']:
        return None, "Invalid status. Must be 'available', 'reserved', or 'faulty'."
    
    system = System.query.get(system_id)
    if not system:
        return None, "System not found."
    
    system.status = status
    db.session.commit()
    return system.to_dict(), None
