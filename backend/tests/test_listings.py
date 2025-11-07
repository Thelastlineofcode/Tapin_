from auth import token_for


def test_create_and_crud_listing(client, create_user):
    user_id = create_user('owner@example.com')
    token = token_for(user_id)
    headers = {'Authorization': f'Bearer {token}'}

    # create
    resp = client.post('/listings', json={'title': 'L1', 'description': 'D1'}, headers=headers)
    assert resp.status_code == 201
    listing = resp.get_json()
    lid = listing['id']

    # read
    r2 = client.get(f'/listings/{lid}')
    assert r2.status_code == 200

    # update
    r3 = client.put(f'/listings/{lid}', json={'title': 'L1-Updated'}, headers=headers)
    assert r3.status_code == 200
    assert r3.get_json()['title'] == 'L1-Updated'

    # delete
    r4 = client.delete(f'/listings/{lid}', headers=headers)
    assert r4.status_code == 200


def test_update_listing_ownership_verification(client, create_user):
    """Test Story 1.3: Only owner can update listing"""
    owner_id = create_user('owner@example.com')
    other_user_id = create_user('other@example.com')
    
    owner_token = token_for(owner_id)
    other_token = token_for(other_user_id)
    
    # Owner creates listing
    resp = client.post(
        '/listings',
        json={'title': 'Test Listing', 'description': 'Test'},
        headers={'Authorization': f'Bearer {owner_token}'}
    )
    assert resp.status_code == 201
    listing_id = resp.get_json()['id']
    
    # Owner can update
    resp_owner = client.put(
        f'/listings/{listing_id}',
        json={'title': 'Updated by Owner'},
        headers={'Authorization': f'Bearer {owner_token}'}
    )
    assert resp_owner.status_code == 200
    
    # Other user cannot update
    resp_other = client.put(
        f'/listings/{listing_id}',
        json={'title': 'Updated by Other'},
        headers={'Authorization': f'Bearer {other_token}'}
    )
    assert resp_other.status_code == 403
    assert 'not the owner' in resp_other.get_json()['error'].lower()


def test_delete_listing_ownership_verification(client, create_user):
    """Test Story 1.3: Only owner can delete listing"""
    owner_id = create_user('owner@example.com')
    other_user_id = create_user('other@example.com')
    
    owner_token = token_for(owner_id)
    other_token = token_for(other_user_id)
    
    # Owner creates listing
    resp = client.post(
        '/listings',
        json={'title': 'Test Listing', 'description': 'Test'},
        headers={'Authorization': f'Bearer {owner_token}'}
    )
    assert resp.status_code == 201
    listing_id = resp.get_json()['id']
    
    # Other user cannot delete
    resp_other = client.delete(
        f'/listings/{listing_id}',
        headers={'Authorization': f'Bearer {other_token}'}
    )
    assert resp_other.status_code == 403
    assert 'not the owner' in resp_other.get_json()['error'].lower()
    
    # Listing still exists
    resp_check = client.get(f'/listings/{listing_id}')
    assert resp_check.status_code == 200
    
    # Owner can delete
    resp_owner = client.delete(
        f'/listings/{listing_id}',
        headers={'Authorization': f'Bearer {owner_token}'}
    )
    assert resp_owner.status_code == 200
