
import requests, pytest
from src.config import url
from src.error import AccessError, InputError
import jwt

BASE_URL = url

@pytest.fixture(name = "user_presets")
def user_presets():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    
    # making two users
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()
    
    j_renzella_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'jake.renzella@unsw.edu.au',
        'password': 'password',
        'name_first': 'jake',
        'name_last': 'renzella',
    })
    j_renzella_details = j_renzella_details.json()
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": e_luxa_details['token'],
        "u_ids": [h_smith_details['auth_user_id'], j_renzella_details['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json()
    
    channel_1 = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': 'channel1',
        'is_public': True
        }
    )
    assert channel_1.status_code == 200
    channel_1 = channel_1.json()
    
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': h_smith_details['token'],
        'channel_id': channel_1['channel_id']
    })
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': j_renzella_details['token'],
        'channel_id': channel_1['channel_id']
    })
    assert response.status_code == 200
    
    return {
        'users' : [e_luxa_details, h_smith_details, j_renzella_details],
        'channel': channel_1,
        'dm': dm_1
    }

####### users/all/v1 tests ########

def test_list_all_users(user_presets):
    users = user_presets['users']
    
    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                 
            }
        ]
    }
    
def test_list_all_users_invalid_token(user_presets):
    faliure = requests.get(f"{BASE_URL}/users/all/v1", params={
        #####If you know how to blackbox this, do it #########
        'token': jwt.encode({'auth_user_id': -1}, 'placeholder', algorithm='HS256')
    })
    assert faliure.status_code == AccessError.code


def test_list_all_users_removed(user_presets):
    users = user_presets['users']
    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                
            }
        ]
    }
    remove_request = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        'token': users[0]['token'],
        'u_id': users[1]['auth_user_id']
    })
    assert remove_request.status_code == 200
    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    list_request = list_request.json()
    print(list_request)
    assert list_request == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"              
            }
        ]
    }
  
######### user/profile/v1 ##########

def test_display_user_profile(user_presets):
    users = user_presets['users']
    h_smith_profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': users[0]['token'],
            'u_id': users[1]['auth_user_id']
    })
    assert h_smith_profile.status_code == 200
    assert h_smith_profile.json() == {
        'user': {
            'u_id': users[1]['auth_user_id'],
            'email': 'hayden.smith@unsw.edu.au',
            'name_first': 'hayden',
            'name_last': 'smith',
            'handle_str': 'haydensmith',
            'profile_img_url': f"{BASE_URL}/images/default.jpg"
        }
    }

def test_display_removed_user_profile(user_presets):
    users = user_presets['users']
    remove_request = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        'token': users[0]['token'],
        'u_id': users[1]['auth_user_id']
    })
    assert remove_request.status_code == 200
    removed_profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': users[0]['token'],
            'u_id': users[1]['auth_user_id']
    })
    assert removed_profile.status_code == 200
    assert removed_profile.json() == {
        'user': {
            'u_id': users[1]['auth_user_id'],
            'email': 'hayden.smith@unsw.edu.au',
            'name_first': 'Removed',
            'name_last': 'user',
            'handle_str': 'haydensmith',
            'profile_img_url': f"{BASE_URL}/images/default.jpg"  
        }
    }

def test_display_profile_invalid_u_id(user_presets):
    users = user_presets['users']
    non_existant_profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': users[0]['token'],
            'u_id': users[1]['auth_user_id'] - 50000
    })
    assert non_existant_profile.status_code == InputError.code
    
def test_display_profile_invalid_token(user_presets):
    users = user_presets['users']
    unauthorised = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': jwt.encode({'auth_user_id': -1}, 'placeholder', algorithm='HS256'),
            'u_id': users[1]['auth_user_id'] - 50000
    })
    assert unauthorised.status_code == AccessError.code
    
######### user/profile/setname/v1 ##########
def test_change_profile_name(user_presets):
    users = user_presets['users']
    made_channel = user_presets['channel']
    made_dm = user_presets['dm']
    
    e_luxa_profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': users[0]['token'],
            'u_id': users[0]['auth_user_id']
    })
    assert e_luxa_profile.status_code == 200
    assert e_luxa_profile.json() == {
        'user': {
            'u_id': users[0]['auth_user_id'],
            'email': 'e.luxa@student.unsw.edu.au',
            'name_first': 'emily',
            'name_last': 'luxa',
            'handle_str': 'emilyluxa',
            'profile_img_url': f"{BASE_URL}/images/default.jpg"  
        }
    }
    
    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"               
            }
        ]
    }
    
    
    name_change = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        'token': users[0]['token'],
        'name_first': 'Westley',
        'name_last': 'Lo'
    })
    assert name_change.status_code == 200
    e_luxa_profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': users[0]['token'],
            'u_id': users[0]['auth_user_id']
    })
    assert e_luxa_profile.status_code == 200
    assert e_luxa_profile.json() == {
        'user': {
            'u_id': users[0]['auth_user_id'],
            'email': 'e.luxa@student.unsw.edu.au',
            'name_first': 'Westley',
            'name_last': 'Lo',
            'handle_str': 'emilyluxa',
            'profile_img_url': f"{BASE_URL}/images/default.jpg"  
        }
    }

    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Westley',
                'name_last': 'Lo',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella' ,
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                
            }
        ]
    }
    name_change2 = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        'token': users[1]['token'],
        'name_first': 'Amy',
        'name_last': 'Pham'
    })
    assert name_change2.status_code == 200
    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Westley',
                'name_last': 'Lo',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'Amy',
                'name_last': 'Pham',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                
            }
        ]
    }
    
    assert requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': users[0]['token'],
        'dm_id': made_dm['dm_id']
    }).json() == {
        'name': 'emilyluxa, haydensmith, jakerenzella',
        'members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Westley',
                'name_last': 'Lo',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'Amy',
                'name_last': 'Pham',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                 
            }
        ]
    }
    
    channel_request = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': users[0]['token'],
        'channel_id': made_channel['channel_id']
    }).json()
    assert channel_request == {
        'name': 'channel1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Westley',
                'name_last': 'Lo',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"               
            }
        ],
        'all_members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Westley',
                'name_last': 'Lo',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'Amy',
                'name_last': 'Pham',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                 
            }
        ]
    }
    
def test_change_name_empty_names(user_presets):
    users = user_presets['users']
 
    first_name_empty = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        'token': users[0]['token'],
        'name_first': '',
        'name_last': 'Lo'
    })
    assert first_name_empty.status_code == InputError.code
    
    last_name_empty = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        'token': users[0]['token'],
        'name_first': 'Westley',
        'name_last': ''
    })
    assert last_name_empty.status_code == InputError.code
    
def test_change_name_long_first_name(user_presets):
    users = user_presets['users']
 
    first_name_long = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        'token': users[0]['token'],
        'name_first': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'name_last': 'Lo'
    })
    assert first_name_long.status_code == InputError.code
    
    last_name_long = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        'token': users[0]['token'],
        'name_first': 'Westley',
        'name_last': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    })
    assert last_name_long.status_code == InputError.code
    
def test_change_name_invalid_token(user_presets):
    ######## if you can blackbox this, do it.
    name_change = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        'token': jwt.encode({'auth_user_id': -1}, 'placeholder', algorithm='HS256'),
        'name_first': 'Westley',
        'name_last': 'Lo'
    })
    assert name_change.status_code == AccessError.code
    
############ user/profile/setmail ##########
def test_change_profile_email(user_presets):
    users = user_presets['users']
    made_channel = user_presets['channel']
    made_dm = user_presets['dm']
    e_luxa_profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': users[0]['token'],
            'u_id': users[0]['auth_user_id']
    })
    assert e_luxa_profile.status_code == 200
    assert e_luxa_profile.json() == {
        'user': {
            'u_id': users[0]['auth_user_id'],
            'email': 'e.luxa@student.unsw.edu.au',
            'name_first': 'emily',
            'name_last': 'luxa',
            'handle_str': 'emilyluxa',
            'profile_img_url': f"{BASE_URL}/images/default.jpg"  
        }
    }
    
    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"              
            }
        ]
    }
    
    
    email_change = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        'token': users[0]['token'],
        'email': 'new@email.com'
    })
    assert email_change.status_code == 200
    e_luxa_profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': users[0]['token'],
            'u_id': users[0]['auth_user_id']
    })
    assert e_luxa_profile.status_code == 200
    assert e_luxa_profile.json() == {
        'user': {
            'u_id': users[0]['auth_user_id'],
            'email': 'new@email.com',
            'name_first': 'emily',
            'name_last': 'luxa',
            'handle_str': 'emilyluxa',
            'profile_img_url': f"{BASE_URL}/images/default.jpg"  
        }
    }

    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'new@email.com',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',               
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            }
        ]
    }
    email_change2 = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        'token': users[1]['token'],
        'email': 'new2@email.com'
    })
    assert email_change2.status_code == 200

    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'new@email.com',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'new2@email.com',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                
            }
        ]
    }
    assert requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': users[0]['token'],
        'dm_id': made_dm['dm_id']
    }).json() == {
        'name': 'emilyluxa, haydensmith, jakerenzella',
        'members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'new@email.com',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'new2@email.com',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                 
            }
        ]
    }
    
    details = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': users[0]['token'],
        'channel_id': made_channel['channel_id']
    })
    details = details.json() 
    assert details == {
        'name': 'channel1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'new@email.com',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            }
        ],
        'all_members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'new@email.com',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'new2@email.com',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                 
            }
        ]
    }
    
def test_setemail_invalid_emails(user_presets):
    users = user_presets['users']
    no_symbols = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        'token': users[0]['token'],
        'email': 'invalidemail'
    })
    assert no_symbols.status_code == InputError.code
    
    with_symbols = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        'token': users[0]['token'],
        'email': 'invalid@email.'
    })
    assert with_symbols.status_code == InputError.code
    
def test_change_email_duplicate_email(user_presets):
    users = user_presets['users']
 
    duplicate = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        'token': users[0]['token'],
        'email': 'jake.renzella@unsw.edu.au'
    })
    assert duplicate.status_code == InputError.code
    
def test_change_email_invalid_token():
    ######## if you can blackbox this, do it.
    invalid = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        'token': jwt.encode({'auth_user_id': -1}, 'placeholder', algorithm='HS256'),
        'email': 'valid@unsw.edu.au'
    })
    assert invalid.status_code == AccessError.code
    
############# user/profile/sethandle #############
def test_change_profile_handle(user_presets):
    users = user_presets['users']
    made_channel = user_presets['channel']
    made_dm = user_presets['dm']
    e_luxa_profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': users[0]['token'],
            'u_id': users[0]['auth_user_id']
    })
    assert e_luxa_profile.status_code == 200
    assert e_luxa_profile.json() == {
        'user': {
            'u_id': users[0]['auth_user_id'],
            'email': 'e.luxa@student.unsw.edu.au',
            'name_first': 'emily',
            'name_last': 'luxa',
            'handle_str': 'emilyluxa',
            'profile_img_url': f"{BASE_URL}/images/default.jpg"  
        }
    }
    
    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                
            }
        ]
    }
    
    
    handle_change = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        'token': users[0]['token'],
        'handle_str': 'newhandle'
    })
    assert handle_change.status_code == 200
    
    e_luxa_profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': users[0]['token'],
            'u_id': users[0]['auth_user_id']
    })
    assert e_luxa_profile.status_code == 200
    assert e_luxa_profile.json() == {
        'user': {
            'u_id': users[0]['auth_user_id'],
            'email': 'e.luxa@student.unsw.edu.au',
            'name_first': 'emily',
            'name_last': 'luxa',
            'handle_str': 'newhandle',
            'profile_img_url': f"{BASE_URL}/images/default.jpg"  
        }
    }

    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'newhandle',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                 
            }
        ]
    }
    handle_change2 = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        'token': users[1]['token'],
        'handle_str': 'newhandle2'
    })
    assert handle_change2.status_code == 200
    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': users[0]['token']
    })
    assert list_request.status_code == 200
    assert list_request.json() == {
        'users': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'newhandle',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'newhandle2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                
            }
        ]
    }
    
    assert requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': users[0]['token'],
        'dm_id': made_dm['dm_id']
    }).json() == {
        'name': 'emilyluxa, haydensmith, jakerenzella',
        'members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'newhandle',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'newhandle2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            }
        ]
    }
    
    assert requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': users[0]['token'],
        'channel_id': made_channel['channel_id']
    }).json() == {
        'name': 'channel1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'newhandle',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            }
        ],
        'all_members': [
            {
                'u_id': users[0]['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'newhandle',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            },
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'newhandle2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            },
            {
                'u_id': users[2]['auth_user_id'],
                'email': 'jake.renzella@unsw.edu.au',
                'name_first': 'jake',
                'name_last': 'renzella',
                'handle_str': 'jakerenzella',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"                 
            }
        ]
    }
    
def test_change_handle_invalid_handles(user_presets):
    users = user_presets['users']
    too_short = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        'token': users[0]['token'],
        'handle_str': 'ab'
    })
    assert too_short.status_code == InputError.code
    
    too_long = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        'token': users[0]['token'],
        'handle_str': '_____very_long_name__'
    })
    assert too_long.status_code == InputError.code
    
    non_alphanumeric = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        'token': users[0]['token'],
        'handle_str': 'asdf^ee'
    })
    assert non_alphanumeric.status_code == InputError.code
    
def test_change_handle_duplicate_handle(user_presets):
    users = user_presets['users']
 
    duplicate = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        'token': users[0]['token'],
        'handle_str': 'haydensmith'
    })
    assert duplicate.status_code == InputError.code
    
def test_change_handle_invalid_token():
    ######## if you can blackbox this, do it.
    invalid = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        'token': jwt.encode({'auth_user_id': -1}, 'placeholder', algorithm='HS256'),
        'handle_str': 'newhandle'
    })
    assert invalid.status_code == AccessError.code
