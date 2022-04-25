'''
24.3.22

Contains tests for admin userpermission change v1.

Luis Vicente De La Paz Reyes (z5206766)
'''

import requests
from src import config
'''
BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"
SECRET = 'placeholder'
'''
BASE_URL = config.url

def test_admin_userpermissions_change_basic():
    '''
    Contains basic tests for channel_join_v1.  Tests for appropriate return type,
    ability to reuse email and handle, and removal from channels and dms list.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token = response.json()['token']
   
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail2@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']
    u_id2 = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail3@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy3"
    })
    
    u_id3 = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token,
        'name': 'Channel 1',
        'is_public': False
    })

    channel_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token,
        "channel_id": channel_id,
        "u_id": u_id3
    })

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    

    assert response.status_code == 403

    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
        "token": token,
        "u_id": u_id2,
        "permission_id": 1
    }) 

    assert response.status_code == 200
    assert response.json() == {}

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })

    assert response.status_code == 200
    assert response.json() == {}

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        "token": token2,
        "channel_id": channel_id,
        "u_id": u_id3
    })

    assert response.status_code == 200
    assert response.json() == {}

    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': token,
        'channel_id': channel_id
    })
    assert response.json() == {
        'name' : 'Channel 1',
        'is_public' : False,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }, {
                'u_id': 3,
                'email': 'testemail3@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy3',
                'handle_str': 'testdummy3',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }, {
                'u_id': 3,
                'email': 'testemail3@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy3',
                'handle_str': 'testdummy3',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            },  {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ],
    }

def test_admin_userpermission_change_InputError_uid_invalid():
    '''
    Contains basic tests for admin_userpermission_change_v1.  Tests for 
    appropriate return type and channel priviledges
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

    u_id2 = 10000

    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
        "token": token,
        "u_id": u_id2,
        "permission_id": 1
    }) 
    
    assert response.status_code == 400

def test_admin_userpermission_change_InputError_only_global_owner():
    '''
    Contains test for admin_userpermission_change_v1.  Tests for u_id only global owner InputError
    thrown.
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

    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
        "token": token,
        "u_id": u_id,
        "permission_id": 2
    }) 
    
    assert response.status_code == 400

def test_admin_userpermission_change_InputError_permission_id():
    '''
    Contains test for admin_userpermission_change_v1.  Tests for invalid permissionid InputError
    thrown.
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
        'email': 'dummy2@hotmail.com',
        'password': 'pass123',
        'name_first': 'test2',
        'name_last': 'dummy2',
        })
    
    u_id = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
        "token": token,
        "u_id": u_id,
        "permission_id": 10000
    }) 
    
    assert response.status_code == 400

def test_admin_userpermission_change_InputError_no_change():
    '''
    Contains test for admin_userpermission_change_v1.  Tests for InputError
    throw when no change is made to permission id.
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
        'email': 'dummy2@hotmail.com',
        'password': 'pass123',
        'name_first': 'test2',
        'name_last': 'dummy2',
        })
    
    u_id = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
        "token": token,
        "u_id": u_id,
        "permission_id": 2
    })  
    
    assert response.status_code == 400


def test_admin_userpermission_change_AccessError_auth():
    '''
    Contains test for admin_userpermission_change_v1.  Tests for AccessError
    throw when user authorising action is not a global owner.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")

    # dummy user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy@hotmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy'
    })

        # dummy user 2
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy2@hotmail.com',
        'password': 'pass123',
        'name_first': 'test2',
        'name_last': 'dummy2'
    })

    token2 = response.json()['token']
    u_id = response.json()['auth_user_id']
    
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = {
        "token": token2,
        "u_id": u_id,
        "permission_id": 1
    })  

    assert response.status_code == 403