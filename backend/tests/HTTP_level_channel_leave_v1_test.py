'''
Created: 22.3.22
Last update:

Contains tests for channel/leave/v1. 

Luis Vicente De La Paz Reyes (z5206766)
'''

import requests
from src import config
from src.error import AccessError, InputError
'''
BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"    
'''
BASE_URL = config.url
def test_leave_basic_return():
    '''
    Basic test to check channel/leave/v1 return values.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    token = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "testemail@gmail.com",
        "password": "pass123",
        "name_first": "test",
        "name_last": "dummy"
    }).json()
    channel = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": token["token"],
        "name": "channel_1",
        "is_public": True
    }).json()
    token2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "testemail2@gmail.com",
        "password": "pass123",
        "name_first": "test2",
        "name_last": "dummy2"
    }).json()
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        'token': token2["token"],
        'channel_id': channel["channel_id"]
    })
    
    assert requests.get(f"{BASE_URL}/channel/details/v2", params={
        'token': token["token"],
        'channel_id': channel["channel_id"],
    }).json() == {
        'name': "channel_1",
        'is_public': True,
        'owner_members': [
            {
                "email": "testemail@gmail.com",
                "name_first": "test",
                "name_last": "dummy",
                "handle_str": "testdummy",
                "u_id": 1,
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            }
        ],
        'all_members': [
            {
                "email": "testemail@gmail.com",
                "name_first": "test",
                "name_last": "dummy",
                "handle_str": "testdummy",
                "u_id": 1,
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                "email": "testemail2@gmail.com",
                "name_first": "test2",
                "name_last": "dummy2",
                "handle_str": "test2dummy2",
                "u_id": 2,
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            }           
        ]   
    }
    
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": token["token"],
        "channel_id": channel["channel_id"],
    })
    assert requests.get(f"{BASE_URL}/channel/details/v2", params={
        'token': token2["token"],
        'channel_id': channel["channel_id"],
    }).json() == {
        'name': "channel_1",
        'is_public': True,
        'owner_members': [],
        'all_members': [
            {
                "email": "testemail2@gmail.com",
                "name_first": "test2",
                "name_last": "dummy2",
                "handle_str": "test2dummy2",
                "u_id": 2,
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            }           
        ]   
    }
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": token2['token'],
        "channel_id": channel["channel_id"],
    })
    assert response.json() == {}

def test_leave_keyError():
    '''
    Basic test to check channel/leave/v1 return values.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    token = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "testemail@gmail.com",
        "password": "pass123",
        "name_first": "test",
        "name_last": "dummy"
    })
    channel = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": token.json()["token"],
        "name": "channel_1",
        "is_public": True
    })
    token = token.json()["token"] + "asd"
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": token,
        "channel_id": channel.json()["channel_id"],
    })
    assert response.status_code == AccessError.code

def test_leave_basic_400_InputError():
    '''
    Basic test to check channel/leave/v1 InputError 400 thrown correctly.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    token = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "testemail@gmail.com",
        "password": "pass123",
        "name_first": "test",
        "name_last": "dummy"
    })
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": token.json()["token"],
        "channel_id": 1,
    })
    assert response.status_code == 400

def test_leave_basic_403_AccessError():
    '''
    Basic test to check channel/leave/v1 AccessError 403 thrown correctly.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    token = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "testemail@gmail.com",
        "password": "pass123",
        "name_first": "test",
        "name_last": "dummy"
    })
    channel = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": token.json()["token"],
        "name": "channel_1",
        "is_public": True
    })
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": token.json()["token"],
        "channel_id": channel.json()["channel_id"],
    })
    assert response.json() == {}
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": token.json()["token"],
        "channel_id": channel.json()["channel_id"],
    })
    assert response.status_code == 403

def test_leave_active_standup_InputError():
    '''
    Basic test to check channel/leave/v1 InputError 400 thrown correctly
    for standup host.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']
    
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail2@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']
    u_id2 = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token1,
        "channel_id": channel1_id,
        "u_id": u_id2
    })

    length = 2

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token2,
        "channel_id": channel1_id,
        "length": length
    })

    response = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": token2,
        "channel_id": channel1_id,
    })

    assert response.status_code == 400
