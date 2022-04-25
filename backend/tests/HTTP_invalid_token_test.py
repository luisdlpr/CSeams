'''
24.3.22

Contains tests for invalid tokens and sessions.

Luis Vicente De La Paz Reyes (z5206766)
'''

import pytest
import requests
from src import config, helpers
import jwt
from src.error import InputError, AccessError

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"
SECRET = 'placeholder'

def test_invalid_token_leave_basic():
    '''
    Basic test to check leave function will not pass when invalid token is given
    '''    
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token = response.json()['token']
   
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'Channel 1',
        'is_public': True
    })

    channel_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testdummy2@gmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    

    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {
        "token": token2
    })

    assert response.status_code == 200

    response2 = requests.post(f"{BASE_URL}/channel/leave/v1", json = {
        'token': token2,
        'channel_id': channel_id
    })

    assert response2.status_code == 403

def test_invalid_token_join_basic():
    '''
    Basic test to check join function will not pass when invalid token is given
    '''    
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token = response.json()['token']
   
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'Channel 1',
        'is_public': True
    })

    channel_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testdummy2@gmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']

    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {
        "token": token2
    })

    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    

    assert response.status_code == 403

def test_invalid_token_userremoved_basic():
    '''
    Basic test to check join function will not pass when invalid token is given due to removed user
    '''    
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token = response.json()['token']
   
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'Channel 1',
        'is_public': True
    })

    channel_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testdummy2@gmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']
    u_id2 = response.json()['auth_user_id']

    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": token,
        "u_id": u_id2
    })

    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    

    assert response.status_code == 403

    with pytest.raises(AccessError):
        token2 = helpers.make_token(1, 20)
        helpers.check_valid_token(token2)
        
    with pytest.raises(AccessError):
        token2 = helpers.make_token(u_id2, 1)
        token2 = helpers.make_token(u_id2, 0)
        helpers.check_valid_token(token2)
    
    with pytest.raises(AccessError):
        token2 = helpers.make_token(u_id2, None)
        helpers.check_valid_token(token2)

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    

    assert response.status_code == 403

    token2 = jwt.encode({"auth_user_id": u_id2, "session_id": 1}, 'fake', algorithm ="HS256") 
    with pytest.raises(AccessError):
        assert helpers.check_valid_token(token2)
        assert helpers.decode_token(token2)

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    

    assert response.status_code == 403


