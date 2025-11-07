from auth import token_for
from app import app


def test_get_items_empty(client):
    resp = client.get('/api/items')
    assert resp.status_code == 200
    assert isinstance(resp.get_json().get('items'), list)


def test_post_items_requires_auth(client):
    resp = client.post('/api/items', json={'name': 'X'})
    assert resp.status_code == 401 or resp.status_code == 422


def test_post_items_success(client, create_user):
    user_id = create_user('items@example.com')
    token = token_for(user_id)
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post('/api/items', json={'name': 'ItemA'}, headers=headers)
    assert resp.status_code == 201
    assert resp.get_json()['name'] == 'ItemA'
