from src.data_store import data_store
import requests, pytest
from src.config import url
from src.error import AccessError, InputError
import jwt

BASE_URL = url

@pytest.fixture(name = "user_presets")
def user_presets():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    
    # making three users

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
    assert j_renzella_details.status_code == 200
    j_renzella_details = j_renzella_details.json()
    
    return [e_luxa_details, h_smith_details, j_renzella_details]

############## dm/create/v1 and dm/list/v1 tests ###############
def test_make_one_and_multiple_dms(user_presets):
    '''
    make a dm, return 200 OK, list it to see the dm is there.
    '''
    data = user_presets
    
    # Making three dms
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": data[0]['token'],
        "u_ids": [data[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json()
    
    #jake should not be in any dms at this point.
    dm_list_empty = requests.get(f'{BASE_URL}/dm/list/v1', params={
        "token": data[2]['token']
    })
    assert dm_list_empty.status_code == 200
    dm_list_empty = dm_list_empty.json()
    
    assert dm_list_empty == {
        'dms': []
    }     
    
    dm_2 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": data[0]['token'],
        "u_ids": [data[1]['auth_user_id'], data[2]['auth_user_id']]
    })
    assert dm_2.status_code == 200
    dm_2 = dm_2.json()
    
    dm_3 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": data[1]['token'],
        "u_ids": [data[2]['auth_user_id']]
    })
    assert dm_3.status_code == 200
    dm_3 = dm_3.json()
    
    # listing all the dms emily luxa is in.
    dm_list_1 = requests.get(f'{BASE_URL}/dm/list/v1', params={
        'token': data[0]['token']
    })
    dm_list_1.status_code == 200
    dm_list_1 = dm_list_1.json()
    
    assert dm_list_1 == {
        'dms': [
            {
                'dm_id': dm_1['dm_id'],
                'name': 'emilyluxa, haydensmith'
            },
            {
                'dm_id': dm_2['dm_id'],
                'name': 'emilyluxa, haydensmith, jakerenzella'
            }
        ]
    }
    
    # list all the channel jake is in
    dm_list_2 = requests.get(f'{BASE_URL}/dm/list/v1', params={
        'token': data[2]['token']
    })
    dm_list_2.status_code == 200
    dm_list_2 = dm_list_2.json()   
    
    assert dm_list_2 == {
        'dms': [
            {
                'dm_id': dm_2['dm_id'],
                'name': 'emilyluxa, haydensmith, jakerenzella'
            },
            {
                'dm_id': dm_3['dm_id'],
                'name': 'haydensmith, jakerenzella'
            }
        ]
    }   


def test_dm_create_invalid_token():
    
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    faliure = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": jwt.encode({'auth_user_id': -1}, 'placeholder', algorithm='HS256'),
        "u_ids": [1]
    })
    assert faliure.status_code == AccessError.code
    
    faliure = requests.get(f'{BASE_URL}/dm/list/v1', params={
        'token': jwt.encode({'auth_user_id': -1}, 'placeholder', algorithm='HS256')
    })
    assert faliure.status_code == AccessError.code

def test_dm_create_invalid_u_id(user_presets):
    
    data = user_presets
    
    faliure = requests.post(f'{BASE_URL}/dm/create/v1', json={
            "token": data[0]['token'],
            "u_ids": [-500]
        })  
    assert faliure.status_code == InputError.code

def test_dm_create_duplicate_u_id(user_presets):
    
    users = user_presets
    
    faliure = requests.post(f'{BASE_URL}/dm/create/v1', json={
            "token": users[0]['token'],
            "u_ids": [users[1]['auth_user_id'], users[1]['auth_user_id']]
        })  
    assert faliure.status_code == InputError.code


############ dm/remove/v1 tests ############
    
def test_dm_remove_simple(user_presets):
    '''
        # make multiple dms, list, remove one of them, and list.
    '''
    users = user_presets
   
    # Making three dms
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json() 
    
    dm_2 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id'], users[2]['auth_user_id']]
    })
    assert dm_2.status_code == 200
    dm_2 = dm_2.json()
    
    dm_list_1 = requests.get(f'{BASE_URL}/dm/list/v1', params={
        'token': users[0]['token']
    })
    dm_list_1.status_code == 200
    dm_list_1 = dm_list_1.json()
    assert dm_list_1 == {
        'dms': [
            {
                'dm_id': dm_1['dm_id'],
                'name': 'emilyluxa, haydensmith'
            },
            {
                'dm_id': dm_2['dm_id'],
                'name': 'emilyluxa, haydensmith, jakerenzella'
            }
        ]
    }  
    
    response = requests.delete(f'{BASE_URL}/dm/remove/v1', json={
        'token': users[0]['token'],
        'dm_id': dm_1['dm_id']
    })
    assert response.status_code == 200

    dm_list_removed = requests.get(f'{BASE_URL}/dm/list/v1', params={
        'token': users[0]['token']
    })
    dm_list_removed.status_code == 200
    dm_list_removed = dm_list_removed.json()   
    assert dm_list_removed == {
        'dms': [
            {
                'dm_id': dm_2['dm_id'],
                'name': 'emilyluxa, haydensmith, jakerenzella'
            }
        ]
    } 

def test_dm_remove_invalid_dm_id(user_presets):
    '''
    # make multiple dms, list, remove one of them, but now with invalid dm_id, InputError thrown.
    '''
    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json() 
    
    faliure = requests.delete(f'{BASE_URL}/dm/remove/v1', json={
            'token': users[0]['token'],
            'dm_id': dm_1['dm_id'] - 500
        })
    assert faliure.status_code == InputError.code
        
def test_dm_remove_non_creator(user_presets):
    '''
    # make dm, list, remove one of them with valid dm_id, but authorised user not creator, throw AccessError
    '''
    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json() 
    
    faliure = requests.delete(f'{BASE_URL}/dm/remove/v1', json={
            'token': users[1]['token'],
            'dm_id': dm_1['dm_id']
        })
    assert faliure.status_code == AccessError.code
        
############### dm/details/v1 tests ###########

def test_print_details(user_presets):
    '''
    # make dm, print details,
    '''
    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json() 
    
    dm_1_details = requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': users[0]['token'],
        'dm_id': dm_1['dm_id']
    })
    assert dm_1_details.status_code == 200
    dm_1_details = dm_1_details.json()
    
    assert dm_1_details == {
        'name': 'emilyluxa, haydensmith',
        'members': [
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
            }
        ]
    }

def test_print_details_invalid_dm_id(user_presets):
    '''
    # make dm, print details but with invalid dm_id, throw InputError
    '''
    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json() 

    faliure = requests.get(f'{BASE_URL}/dm/details/v1', params={
            'token': users[0]['token'],
            'dm_id': -500
        })
    assert faliure.status_code == InputError.code
    
def test_print_details_invalid_user(user_presets):
    '''
    # make dm, print details with valid dm_id, but user not in DM, throw AccessError.
    '''
    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json() 
    
    faliure = requests.get(f'{BASE_URL}/dm/details/v1', params={
            'token': users[2]['token'],
            'dm_id': dm_1['dm_id']
        })   
    assert faliure.status_code == AccessError.code

############### dm/leave/v1 tests ###################

def test_dm_leave(user_presets):
    '''
    # make dm, print details, one of the user leaves, print details to see updated, name shouldn't be changed.
    '''
    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json()    

    dm_1_details = requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': users[0]['token'],
        'dm_id': dm_1['dm_id']
    })
    
    assert dm_1_details.status_code == 200
    dm_1_details = dm_1_details.json()
    
    assert dm_1_details == {
        'name': 'emilyluxa, haydensmith',
        'members': [
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
            }
        ]
    }

    delete_response = requests.post(f'{BASE_URL}/dm/leave/v1', json={
        'token': users[0]['token'],
        'dm_id': dm_1['dm_id']
    })
    assert delete_response.status_code == 200
    
    dm_1_details_new = requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': users[1]['token'],
        'dm_id': dm_1['dm_id']
    })
    assert dm_1_details_new.status_code == 200
    dm_1_details_new = dm_1_details_new.json()
    
    assert dm_1_details_new == {
        'name': 'emilyluxa, haydensmith',
        'members': [
            {
                'u_id': users[1]['auth_user_id'],
                'email': 'hayden.smith@unsw.edu.au',
                'name_first': 'hayden',
                'name_last': 'smith',
                'handle_str': 'haydensmith',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            }
        ]
    }

    delete_response = requests.post(f'{BASE_URL}/dm/leave/v1', json={
        'token': users[1]['token'],
        'dm_id': dm_1['dm_id']
    })
    assert delete_response.status_code == 200
    
def test_dm_leave_invalid_dm_id(user_presets):
    '''
    # make dm, print details, user leave but with invalid dm_id, InputError thrown.
    '''
    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json()    

    faliure = requests.post(f'{BASE_URL}/dm/leave/v1', json={
            'token': users[0]['token'],
            'dm_id': -500
        })        
    assert faliure.status_code == InputError.code
        
def test_dm_leave_non_member(user_presets):
    '''
    # make dm, print details, user leave with valid dm_id, but user_id not even in the dm, AccessError thrown.
    '''
    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json()    
    
    faliure = requests.post(f'{BASE_URL}/dm/leave/v1', json={
            'token': users[2]['token'],
            'dm_id': dm_1['dm_id']
        })
    assert faliure.status_code == AccessError.code
        
def test_dm_remove_creator_left(user_presets):
    # make dm, list, creator leaves, remove one of them with valid dm_id, auth_user is creator, but creator not in channel (because he left), 
    # throw AccessError.
    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json()      
    
    delete_response = requests.post(f'{BASE_URL}/dm/leave/v1', json={
        'token': users[0]['token'],
        'dm_id': dm_1['dm_id']
    })
    assert delete_response.status_code == 200
    
    faliure = requests.delete(f'{BASE_URL}/dm/remove/v1', json={
            'token': users[0]['token'],
            'dm_id': dm_1['dm_id']
        })
    assert faliure.status_code == AccessError.code
    
    
    
    
############ emergency fix new tests ############
    '''
    def test_dm_remove_and_remove_again(user_presets):

    # make dm, list, remove one of them with valid dm_id, but authorised user not creator, throw AccessError

    users = user_presets
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": users[0]['token'],
        "u_ids": [users[1]['auth_user_id']]
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json() 
    
    requests.delete(f'{BASE_URL}/dm/remove/v1', json={
            'token': users[0]['token'],
            'dm_id': dm_1['dm_id']
        })

    faliure = requests.delete(f'{BASE_URL}/dm/remove/v1', json={
            'token': users[0]['token'],
            'dm_id': dm_1['dm_id']
        })
    assert faliure.status_code == InputError.code
    '''