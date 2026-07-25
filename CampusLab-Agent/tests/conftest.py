import pytest
from app import create_app
from models import db, User, Lab, System

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Register and login a test student user, returning JWT Bearer headers"""
    client.post('/api/register', json={
        'name': 'Test Student',
        'email': 'teststudent@campus.edu',
        'password': 'password123',
        'role': 'student'
    })
    login_res = client.post('/api/login', json={
        'email': 'teststudent@campus.edu',
        'password': 'password123'
    })
    token = login_res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def admin_headers(client):
    """Register and login a test admin user, returning JWT Bearer headers"""
    client.post('/api/register', json={
        'name': 'Test Admin',
        'email': 'testadmin@campus.edu',
        'password': 'adminpassword123',
        'role': 'admin'
    })
    login_res = client.post('/api/login', json={
        'email': 'testadmin@campus.edu',
        'password': 'adminpassword123'
    })
    token = login_res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}
