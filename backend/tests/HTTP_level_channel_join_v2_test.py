'''
12.3.22

Contains tests for channel join v2.

Luis Vicente De La Paz Reyes (z5206766)
'''

import requests
from src import config
'''
BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"
'''
BASE_URL = config.url
def test_channel_join_basic():
    '''
    Basic test to check channel/join/v2 returns correct output in basic success 
    case.
    '''    
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy@hotmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy'
    })
    
    token = response.json()['token']
    
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'channel 1',
        'is_public': True
    })

    channel_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy2@hotmail.com',
        'password': 'pass123',
        'name_first': 'test2',
        'name_last': 'dummy2'
    })
    
    token = response.json()['token']

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token,
        'channel_id': channel_id
    })

    assert response.json() == {}

def test_join_input_error_invalid_channel():
    '''
    tests for status code 400 (input error) - invalid channel.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # dummy user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy@hotmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy'})
    token = response.json()['token']
    
    # dummy invalid channel id.
    channel_id = {'channel_id' : 10000}
    
    # request to post channel join using details
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token, 
        'channel_id': channel_id
    })
    
    assert response.status_code == 400

def test_join_input_error_user():
    '''
    tests for status code 400 (input error) - user already a member.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")

    # dummy user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy@hotmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy'
    })

    token = response.json()['token']
    
    # dummy created channel (user should be member since they create it)
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'channel 1',
        'is_public': True
    })
    channel_id = response.json()['channel_id']

    # request to post channel join using details
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token,
        'channel_id': channel_id
    })
    
    assert response.status_code == 400

def test_join_access_error():
    ''' Tests for AccessError (channel id is private and user is not channel member or global owner)'''
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy@hotmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy'
    })
    token = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'channel 1',
        'is_public': False
    })
    channel_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy2@hotmail.com',
        'password': 'pass123',
        'name_first': 'test2',
        'name_last': 'dummy2'
    })
    token = response.json()['token']

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token,
        'channel_id': channel_id
    })

    assert response.status_code == 403

# ## NEEDS admin/user/remove/v1

def test_join_access_error_removed():
    ''' Tests for AccessError invalid token/user_id'''
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
         'email': 'dummy@hotmail.com',
         'password': 'pass123',
         'name_first': 'test',
         'name_last': 'dummy'
     })
    token = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'channel 1',
        'is_public': False
    })
    channel_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy2@hotmail.com',
        'password': 'pass123',
        'name_first': 'test2',
        'name_last': 'dummy2'
    })
    deleted_token = response.json()['token']
    u_id = response.json()['auth_user_id']


    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = {
        'token': token,
        'u_id': u_id
    })

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': deleted_token,
        'channel_id': channel_id
    })

    assert response.status_code == 403