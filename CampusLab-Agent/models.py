from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # 'student', 'faculty', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade="all, delete-orphan")
    fault_reports = db.relationship('FaultReport', backref='reporter', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Lab(db.Model):
    __tablename__ = 'labs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)
    open_time = db.Column(db.Time, nullable=False) # e.g. 08:00:00
    close_time = db.Column(db.Time, nullable=False) # e.g. 20:00:00
    description = db.Column(db.Text, nullable=True)

    # Relationships
    systems = db.relationship('System', backref='lab', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity,
            'open_time': self.open_time.strftime('%H:%M'),
            'close_time': self.close_time.strftime('%H:%M'),
            'description': self.description,
            'total_systems': len(self.systems),
            'available_systems': sum(1 for s in self.systems if s.status == 'available')
        }


class System(db.Model):
    __tablename__ = 'systems'

    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id', ondelete='CASCADE'), nullable=False)
    system_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available') # 'available', 'reserved', 'faulty'

    __table_args__ = (
        db.UniqueConstraint('lab_id', 'system_number', name='unique_lab_system_number'),
    )

    # Relationships
    bookings = db.relationship('Booking', backref='system', lazy=True)
    fault_reports = db.relationship('FaultReport', backref='system', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'lab_id': self.lab_id,
            'lab_name': self.lab.name if self.lab else None,
            'system_number': self.system_number,
            'status': self.status
        }


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=False)
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id', ondelete='CASCADE'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active') # 'active', 'cancelled', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_email': self.user.email if self.user else None,
            'system_id': self.system_id,
            'system_number': self.system.system_number if self.system else None,
            'lab_id': self.system.lab_id if self.system else None,
            'lab_name': self.system.lab.name if (self.system and self.system.lab) else None,
            'booking_date': self.booking_date.strftime('%Y-%m-%d'),
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class FaultReport(db.Model):
    __tablename__ = 'fault_reports'

    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id', ondelete='SET NULL'), nullable=False)
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False) # 'keyboard', 'mouse', 'monitor', 'network', 'power'
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='open') # 'open', 'in_progress', 'repaired'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'system_id': self.system_id,
            'system_number': self.system.system_number if self.system else None,
            'lab_name': self.system.lab.name if (self.system and self.system.lab) else None,
            'reported_by': self.reported_by,
            'reporter_name': self.reporter.name if self.reporter else None,
            'issue_type': self.issue_type,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
