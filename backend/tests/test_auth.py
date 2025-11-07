from auth import token_for
from app import app


def test_register_and_login(client):
    # register
    resp = client.post('/register', json={'email': 'a1@example.com', 'password': 'pw'})
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'access_token' in data

    # login
    resp2 = client.post('/login', json={'email': 'a1@example.com', 'password': 'pw'})
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert 'access_token' in data2

def test_me_requires_jwt(client, create_user):
    user_id = create_user('me@example.com')
    token = token_for(user_id)
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.get('/me', headers=headers)
    assert resp.status_code == 200
    assert 'user' in resp.get_json()
