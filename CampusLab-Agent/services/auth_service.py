from models import db, User
from flask_jwt_extended import create_access_token

def register_user(name, email, password, role='student'):
    if User.query.filter_by(email=email).first():
        return None, "User with this email already exists."
    
    if role not in ['student', 'faculty', 'admin']:
        return None, "Invalid role specified."

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    token = create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'email': user.email, 'name': user.name})
    return {'user': user.to_dict(), 'token': token}, None

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None, "Invalid email or password."
    
    token = create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'email': user.email, 'name': user.name})
    return {'user': user.to_dict(), 'token': token}, None
