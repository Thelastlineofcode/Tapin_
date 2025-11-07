from auth import token_for, refresh_for


def test_refresh_token_cycle(client, create_user):
    user_id = create_user()
    refresh = refresh_for(user_id)
    headers = {'Authorization': f'Bearer {refresh}'}
    resp = client.post('/refresh', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'access_token' in data
