def test_ai_chat_booking_intent(client, auth_headers):
    response = client.post('/api/chat', json={
        'message': 'I need Lab A tomorrow from 10 to 12.'
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] in ['success', 'conflict']
    assert 'message' in data

def test_ai_chat_view_reservations(client, auth_headers):
    response = client.post('/api/chat', json={
        'message': 'Show my reservations'
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
