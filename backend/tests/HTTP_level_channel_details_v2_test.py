'''
22.3.22

Contains tests for channel details v2.

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
def test_channel_details_basic():
    '''
    Basic test to check channel/details/v2 returns correct output in basic success 
    case.
    '''    
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'testdummy@gmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy'
    })
    
    token = response.json()['token']
    u_id = response.json()['auth_user_id']
    
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'channel 1',
        'is_public': True
    })

    channel_id = response.json()['channel_id']

    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': token,
        'channel_id': channel_id
    })
    assert response.json() == {
        'name': 'channel 1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id,
                'email': 'testdummy@gmail.com',
                'name_first': 'test',
                'name_last': 'dummy',
                'handle_str': 'testdummy',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ],
        'all_members': [
            {
                'u_id': u_id,
                'email': 'testdummy@gmail.com',
                'name_first': 'test',
                'name_last': 'dummy',
                'handle_str': 'testdummy',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ]
    }

def test_details_input_error_invalid_channel():
    '''
    tests for status code 400 (input error) - invalid channel.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # dummy user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy@hotmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy',
        })
    
    token = response.json()['token']
    
    # dummy invalid channel id.
    channel_id = {'channel_id' : 10000}
    
    # request to get channel details using dummy id.
    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': token, 
        'channel_id': channel_id['channel_id']
    })
    
    assert response.status_code == 400

def test_details_AccessError():
    '''
    tests for status code 403 (access error) - user is not a member of valid
    channel.
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

    # dummy user 2
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy2@hotmail.com',
        'password': 'pass123',
        'name_first': 'test2',
        'name_last': 'dummy2'
    })

    token = response.json()['token']

    # request to get channel details using dummy2 id.
    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': token, 
        'channel_id': channel_id
    })

    assert response.status_code == 403