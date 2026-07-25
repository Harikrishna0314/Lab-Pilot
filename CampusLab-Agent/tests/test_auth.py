def test_user_registration(client):
    response = client.post('/api/register', json={
        'name': 'Alice User',
        'email': 'alice@campus.edu',
        'password': 'secretpassword',
        'role': 'student'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'token' in data
    assert data['user']['email'] == 'alice@campus.edu'

def test_user_login(client):
    # Register first
    client.post('/api/register', json={
        'name': 'Bob User',
        'email': 'bob@campus.edu',
        'password': 'bobpassword',
        'role': 'faculty'
    })
    # Login
    response = client.post('/api/login', json={
        'email': 'bob@campus.edu',
        'password': 'bobpassword'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert data['user']['role'] == 'faculty'

def test_invalid_login(client):
    response = client.post('/api/login', json={
        'email': 'nonexistent@campus.edu',
        'password': 'wrong'
    })
    assert response.status_code == 401
