'''
24.3.22

Contains tests for admin remove user v1.

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

def test_admin_removeuser_basic():
    '''
    Basic test to check admin/remove/user/v1 returns correct output in basic success 
    case.
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

    u_id2 = response.json()['auth_user_id']

    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": token,
        "u_id": u_id2
    })

    assert response.status_code == 200
    assert response.json() == {}

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testdummy2@gmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']
    u_id2 = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': token2,
        'channel_id': channel_id
    })    

    response = requests.post(f"{BASE_URL}/channel/addowner/v1", json = {
        "token": token,
        "channel_id": channel_id,
        "u_id": u_id2
    })       

    response = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": token,
        "u_ids": [u_id2]
    })

    dm_id = response.json()['dm_id']

    response = requests.post(f'{BASE_URL}/message/send/v1', json = {
        'token': token2,
        'channel_id': channel_id,
        'message': 'test test 123'
    })

    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}/message/senddm/v1', json = {
        'token': token2,
        'dm_id': dm_id,
        'message': 'test test 123'
    })

    assert response.status_code == 200

    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": token,
        "u_id": u_id2
    })

    assert response.status_code == 200
    assert response.json() == {}

    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': token,
        'channel_id': channel_id
    })
    print(response.json())
    assert response.json() == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
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
            }
        ],
    }

    response = requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': token,
        'dm_id': dm_id
    })

    assert response.json() == {
        'name': 'testdummy1, testdummy2',
        'members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ]
    }

    response = requests.get(f'{BASE_URL}/channel/messages/v2', params = {
        'token': token,
        'channel_id': channel_id,
        'start': 0
    })
    assert response.status_code == 200
    assert response.json()['messages'][0]['message'] == 'Removed user'

    response = requests.get(f'{BASE_URL}/dm/messages/v1', params = {
        'token': token,
        'dm_id': dm_id,
        'start': 0
    })
    assert response.status_code == 200
    assert response.json()['messages'][0]['message'] == 'Removed user'

def test_admin_removeuser_basic_2():
    requests.delete(f"{BASE_URL}/clear/v1")
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    }).json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    }).json()
    
    j_renzella_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'jake.renzella@unsw.edu.au',
        'password': 'password',
        'name_first': 'jake',
        'name_last': 'renzella',
    }).json()

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': e_luxa_details['token'],
        'name': 'Channel1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': h_smith_details['token'],
        'channel_id': channel1_id
    }) 
    
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': h_smith_details['token'],
        'name': 'Channel2',
        'is_public': False
    })

    channel2_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        'token': h_smith_details['token'],
        'channel_id': channel2_id,
        'u_id': j_renzella_details['auth_user_id']
    })   

    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": j_renzella_details['token'],
        "u_ids": [h_smith_details['auth_user_id']]
    }).json() 
    
    dm_2 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": h_smith_details['token'],
        "u_ids": [e_luxa_details['auth_user_id']]
    }).json()

    result = requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': j_renzella_details['token'],
        'dm_id': dm_1['dm_id']
    }).json()
    assert result == {
        'name': 'haydensmith, jakerenzella',
        'members': [
            {
                'u_id': j_renzella_details['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'handle_str': 'jakerenzella',
                'name_first': 'jake',
                'name_last': 'renzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            },
            {
                'u_id': h_smith_details['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ]
    }
    assert requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': h_smith_details['token'],
        'dm_id': dm_2['dm_id']
    }).json() == {
        'name': 'emilyluxa, haydensmith',
        'members': [
            {
                'u_id': h_smith_details['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            },
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"            
            }
        ]
    }

    requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': h_smith_details['token'],
        'channel_id': channel1_id
    }).json() == {
        'name': 'Channel1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"              
            }
        ],
        'all_members': [
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            },
            {
                'u_id': h_smith_details['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ]
    }
    
    requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': h_smith_details['token'],
        'channel_id': channel2_id
    }).json() == {
        'name': 'Channel2',
        'is_public': False,
        'owner_members': [
            {
                'u_id': h_smith_details['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ],
        'all_members': [
            {
                'u_id': j_renzella_details['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'handle_str': 'jakerenzella',
                'name_first': 'jake',
                'name_last': 'renzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            },
            {
                'u_id': h_smith_details['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ]
    }
    
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": e_luxa_details['token'],
        "u_id": h_smith_details['auth_user_id']
    })
    assert response.status_code == 200

    requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': e_luxa_details['token'],
        'channel_id': channel1_id
    }).json() == {
        'name': 'Channel1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"               
            }
        ],
        'all_members': [
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ]
    }
    
    requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': j_renzella_details['token'],
        'channel_id': channel2_id
    }).json() == {
        'name': 'Channel2',
        'is_public': False,
        'owner_members': [],
        'all_members': [
            {
                'u_id': j_renzella_details['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'handle_str': 'jakerenzella',
                'name_first': 'jake',
                'name_last': 'renzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            }
        ]
    }
    
    result = requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': j_renzella_details['token'],
        'dm_id': dm_1['dm_id']
    }).json()
    assert result == {
        'name': 'haydensmith, jakerenzella',
        'members': [
            {
                'u_id': j_renzella_details['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'handle_str': 'jakerenzella',
                'name_first': 'jake',
                'name_last': 'renzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            },
        ]
    }
    assert requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': e_luxa_details['token'],
        'dm_id': dm_2['dm_id']
    }).json() == {
        'name': 'emilyluxa, haydensmith',
        'members': [
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa', 
                'profile_img_url': f"{BASE_URL}/images/default.jpg"             
            }
        ]
    }
    
    assert requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": j_renzella_details['token']
    }).json() == {
        'users': [
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"
            },
            {
                'u_id': j_renzella_details['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"              
            }
        ]
    }
    
    assert requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': e_luxa_details['token'],
            'u_id': h_smith_details['auth_user_id']
    }).json() == {
        'user': {
            'u_id': h_smith_details['auth_user_id'],
            'email': 'hayden.smith@unsw.edu.au',
            'name_first': 'Removed',
            'name_last': 'user',
            'handle_str': 'haydensmith',
            'profile_img_url': f"{BASE_URL}/images/default.jpg"  
        }
    }
    
    
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": e_luxa_details['token'],
        "u_id": j_renzella_details['auth_user_id']
    })
    assert response.status_code == 200
    

def test_remove_user_input_error_invalid_uid():
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

    u_id2 = 10000

    # request to get channel details using dummy id.
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": token,
        "u_id": u_id2
    })
    
    assert response.status_code == 400

def test_remove_user_input_error_only_owner():
    '''
    tests for status code 400 (input error) - attempting to remove only remaining
    owner.
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

    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": token,
        "u_id": u_id
    })
    
    assert response.status_code == 400

def test_remove_user_AccessError():
    '''
    tests for status code 403 (access error) - user does not have global owner
    permissions.
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

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        'email': 'dummy3@hotmail.com',
        'password': 'pass123',
        'name_first': 'test3',
        'name_last': 'dummy3'
    })

    u_id = response.json()['auth_user_id']
    
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": token2,
        "u_id": u_id
    })

    assert response.status_code == 403