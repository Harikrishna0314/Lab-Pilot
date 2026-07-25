from datetime import date, timedelta

def test_booking_creation_and_conflict(client, auth_headers):
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 1. Create first booking
    res1 = client.post('/api/book', json={
        'lab_id': 1,
        'system_number': 1,
        'booking_date': tomorrow,
        'start_time': '10:00',
        'end_time': '12:00'
    }, headers=auth_headers)
    assert res1.status_code == 201

    # 2. Attempt overlapping booking for same user -> Conflict
    res2 = client.post('/api/book', json={
        'lab_id': 1,
        'system_number': 1,
        'booking_date': tomorrow,
        'start_time': '11:00',
        'end_time': '13:00'
    }, headers=auth_headers)
    assert res2.status_code in [400, 409]
    assert 'already' in res2.get_json()['error'].lower() or 'conflict' in res2.get_json()['error'].lower()

def test_booking_cancellation(client, auth_headers):
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Book
    res = client.post('/api/book', json={
        'lab_id': 1,
        'system_number': 2,
        'booking_date': tomorrow,
        'start_time': '14:00',
        'end_time': '15:00'
    }, headers=auth_headers)
    booking_id = res.get_json()['id']

    # Cancel
    cancel_res = client.delete(f'/api/booking/{booking_id}', headers=auth_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.get_json()['booking']['status'] == 'cancelled'
