import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config_by_name
from models import db, User, Lab, System

def create_app(config_name=None):
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    jwt = JWTManager(app)

    # Register API Blueprints
    from routes.auth import auth_bp
    from routes.labs import labs_bp
    from routes.systems import systems_bp
    from routes.bookings import bookings_bp
    from routes.faults import faults_bp
    from routes.ai_chat import ai_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(labs_bp, url_prefix='/api')
    app.register_blueprint(systems_bp, url_prefix='/api')
    app.register_blueprint(bookings_bp, url_prefix='/api')
    app.register_blueprint(faults_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api')

    # Frontend Page Routes
    @app.route('/')
    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')

    @app.route('/chat')
    def chat_page():
        return render_template('chat.html')

    @app.route('/bookings-page')
    def bookings_page():
        return render_template('bookings.html')

    @app.route('/labs-page')
    def labs_page():
        return render_template('labs.html')

    @app.route('/admin')
    def admin_page():
        return render_template('admin.html')

    @app.route('/faults-page')
    def faults_page():
        return render_template('faults.html')

    # Global Error Handlers
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Request is missing an authorization token.'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token signature or format.'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired. Please log in again.'}), 401

    # Database auto-seed helper on startup if empty
    with app.app_context():
        try:
            db.create_all()
            if not Lab.query.first():
                # Seed default labs and systems
                lab_a = Lab(name="Lab A - AI & Data Science", capacity=20, open_time=datetime.strptime("08:00", "%H:%M").time(), close_time=datetime.strptime("20:00", "%H:%M").time(), description="High performance GPU workstations for AI and ML training.")
                lab_b = Lab(name="Lab B - Software Engineering", capacity=25, open_time=datetime.strptime("08:00", "%H:%M").time(), close_time=datetime.strptime("22:00", "%H:%M").time(), description="General computer science lab with full dev stack tools.")
                lab_c = Lab(name="Lab C - Hardware & Networking", capacity=15, open_time=datetime.strptime("09:00", "%H:%M").time(), close_time=datetime.strptime("18:00", "%H:%M").time(), description="Cisco networking racks and hardware troubleshooting kits.")
                db.session.add_all([lab_a, lab_b, lab_c])
                db.session.flush()

                for l in [lab_a, lab_b, lab_c]:
                    for i in range(1, l.capacity + 1):
                        db.session.add(System(lab_id=l.id, system_number=i, status='available'))
                
                # Seed default admin user
                admin = User(name="Lab Admin", email="admin@campus.edu", role="admin")
                admin.set_password("admin123")
                db.session.add(admin)

                student = User(name="Student John", email="john@campus.edu", role="student")
                student.set_password("student123")
                db.session.add(student)

                db.session.commit()
        except Exception as e:
            app.logger.warning(f"Auto-seed exception: {e}")

    return app

from datetime import datetime

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)
