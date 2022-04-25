'''
23.3.22

Contains tests for channel add owner v1.

Luis Vicente De La Paz Reyes (z5206766)
'''

import requests
from src import config
from src.error import AccessError

'''
BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"
'''
BASE_URL = config.url

def test_channel_addowner_basic():
    '''
    Basic test to check channel/addowner/v1 returns correct output in basic success 
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

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'testdummy2@gmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy2'
    })
    
    token2 = response.json()['token']
    u_id2 = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id2
    })       

    assert response.json() == {}

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
            }, {
                'u_id': u_id2,
                'email': 'testdummy2@gmail.com',
                'name_first': 'test',
                'name_last': 'dummy2',
                'handle_str': 'testdummy2',
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
            }, {
                'u_id': u_id2,
                'email': 'testdummy2@gmail.com',
                'name_first': 'test',
                'name_last': 'dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ]
    }

def test_addowner_input_error_invalid_channel():
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
    
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'testdummy2@gmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy2'
    })
    
    u_id2 = response.json()['auth_user_id']

    # dummy invalid channel id.
    channel_id = {'channel_id' : 10000}
    
    # request to get channel details using dummy id.
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id2
    })       
    
    assert response.status_code == 400

def test_addowner_input_error_invalid_uid():
    '''
    tests for status code 400 (input error) - invalid user.
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

    # dummy channel id.
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'channel 1',
        'is_public': True
    })

    channel_id = response.json()['channel_id']

    u_id2 = 10000

    # request to get channel details using dummy id.
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id2
    })       
    
    assert response.status_code == 400

def test_addowner_input_error_non_member():
    '''
    tests for status code 400 (input error) - non member.
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

    # dummy channel id.
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'channel 1',
        'is_public': True
    })

    channel_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'testdummy2@gmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy2'
    })
    
    u_id2 = response.json()['auth_user_id']

    # request to get channel details using dummy id.
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id2
    })       
    
    assert response.status_code == 400

def test_addowner_input_error_already_owner():
    '''
    tests for status code 400 (input error) - already an owner.
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
    u_id = response.json()['auth_user_id']

    # dummy channel id.
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'channel 1',
        'is_public': True
    })

    channel_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })       
    
    assert response.status_code == 400

def test_addowner_AccessError():
    '''
    tests for status code 403 (access error) - user does not have owner
    permissions in the channel.
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

    token2 = response.json()['token']
    
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    


    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy3@hotmail.com',
        'password': 'pass123',
        'name_first': 'test3',
        'name_last': 'dummy3'
    })

    token3 = response.json()['token']
    u_id = response.json()['auth_user_id']
    
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token3,
        'channel_id': channel_id
    })    
    
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        'token': token2,
        'channel_id': channel_id,
        'u_id': u_id
    })

    assert response.status_code == 403
    
def test_globalowner_nonmember_cant_addowner():
    requests.delete(f"{BASE_URL}/clear/v1")

    # dummy user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy@hotmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy'
    })
    owner_token = response.json()['token']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy2@hotmail.com',
        'password': 'pass123',
        'name_first': 'test2',
        'name_last': 'dummy2'
    })

    token2 = response.json()['token']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy3@hotmail.com',
        'password': 'pass123',
        'name_first': 'test3',
        'name_last': 'dummy3'
    })

    token3 = response.json()['token']
    u_id = response.json()['auth_user_id']
    
    # dummy created channel (user should be member since they create it)
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token2,
        'name': 'channel 1',
        'is_public': True
    })
    channel_id = response.json()['channel_id']
    
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token3,
        'channel_id': channel_id
    })    
    
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        'token': owner_token,
        'channel_id': channel_id,
        'u_id': u_id
    })

    assert response.status_code == AccessError.code
    
def test_nonmember_cant_addowner():
    requests.delete(f"{BASE_URL}/clear/v1")

    # dummy user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy@hotmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy'
    })
    owner_token = response.json()['token']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy2@hotmail.com',
        'password': 'pass123',
        'name_first': 'test2',
        'name_last': 'dummy2'
    })

    token2 = response.json()['token']
    u_id = response.json()['auth_user_id']
    
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy3@hotmail.com',
        'password': 'pass123',
        'name_first': 'test3',
        'name_last': 'dummy3'
    })

    token3 = response.json()['token']
    
    
    # dummy created channel (user should be member since they create it)
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': owner_token,
        'name': 'channel 1',
        'is_public': True
    })
    channel_id = response.json()['channel_id']
    
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    
    
    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        'token': token3,
        'channel_id': channel_id,
        'u_id': u_id
    })

    assert response.status_code == AccessError.code