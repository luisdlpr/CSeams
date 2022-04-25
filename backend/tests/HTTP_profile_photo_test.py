'''
    Tests for user/profile/uploadphoto/v1
'''

import requests, hashlib
from src.error import InputError
from src.config import url
BASE_URL = url
'''
    Bucket List:
    # Do it with Invalid URL, get 404ed.
    # x_start, y_start, x_end, y_end not the same as the image dimension.
    # x_end less than x_start.
    # y_end less than y_start.
    # image isn't a jpg.
    
    # Invalid token.
'''

def test_profilephoto_invalid_img_URL():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()

    ### invalid url, get InputError
    invalid_url = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": e_luxa_details["token"],
        "img_url": "https://walpercave.com/wp/wp5042627.jpg",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100,
        "y_end": 100
    })
    assert invalid_url.status_code == InputError.code
    
    forbidden_url = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": e_luxa_details["token"],
        "img_url": "https://cdn.watchgoblinslayer.com/file/mangap/1828/10344000/13.jpg",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100,
        "y_end": 100
    })
    assert forbidden_url.status_code == InputError.code
    
def test_profilephoto_wrong_dimensions():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    wrong_dimensions = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": e_luxa_details["token"],
        "img_url": "https://img.freepik.com/free-photo/closeup-beautiful-green-leaves_23-2148245094.jpg",
        "x_start": 0,
        "y_start": 0,
        "x_end": 10000000000000000000000000000,
        "y_end": 100,
    })
    assert wrong_dimensions.status_code == InputError.code
    
    wrong_dimensions2 = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": e_luxa_details["token"],
        "img_url": "https://img.freepik.com/free-photo/closeup-beautiful-green-leaves_23-2148245094.jpg",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100,
        "y_end": 10000000000000000000000000000,
    })
    assert wrong_dimensions2.status_code == InputError.code

def test_profilephoto_start_greater():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    wrong_dimensions = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": e_luxa_details["token"],
        "img_url": "https://img.freepik.com/free-photo/closeup-beautiful-green-leaves_23-2148245094.jpg",
        "x_start": 50,
        "y_start": 0,
        "x_end": 0,
        "y_end": 100,
    })
    assert wrong_dimensions.status_code == InputError.code

    wrong_dimensions = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": e_luxa_details["token"],
        "img_url": "https://img.freepik.com/free-photo/closeup-beautiful-green-leaves_23-2148245094.jpg",
        "x_start": 0,
        "y_start": 50,
        "x_end": 100,
        "y_end": 0,
    })
    assert wrong_dimensions.status_code == InputError.code    

def test_not_a_jpg():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    not_jpg = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": e_luxa_details["token"],
        "img_url": "https://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100,
        "y_end": 100,
    })
    assert not_jpg.status_code == InputError.code
    
def test_upload_profile_photo_correct():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()

    profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': e_luxa_details['token'],
            'u_id': e_luxa_details['auth_user_id']
    })
    assert profile.status_code == 200
    assert profile.json() == {
        'user': {
            'u_id': e_luxa_details['auth_user_id'],
            'email': 'e.luxa@student.unsw.edu.au',
            'name_first': 'emily',
            'name_last': 'luxa',
            'handle_str': 'emilyluxa',
            'profile_img_url': f"{BASE_URL}/images/default.jpg" 
        }
    }

    correct = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": e_luxa_details["token"],
        "img_url": "https://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP.jpg",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100,
        "y_end": 100,
    })
    assert correct.status_code == 200
    
    profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': e_luxa_details['token'],
            'u_id': e_luxa_details['auth_user_id']
    })
    image_name = hashlib.sha256(str(e_luxa_details['auth_user_id']).encode()).hexdigest()
    assert profile.status_code == 200
    assert profile.json()['user']['profile_img_url'] != f'{BASE_URL}/images/default.jpg'
    assert profile.json()['user']['profile_img_url'] == f'{BASE_URL}/images/{image_name}.jpg'


def test_channel_dm_profile_photo_change():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()

    profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': e_luxa_details['token'],
            'u_id': e_luxa_details['auth_user_id']
    })
    assert profile.status_code == 200
    assert profile.json() == {
        'user': {
            'u_id': e_luxa_details['auth_user_id'],
            'email': 'e.luxa@student.unsw.edu.au',
            'name_first': 'emily',
            'name_last': 'luxa',
            'handle_str': 'emilyluxa',
            'profile_img_url': f"{BASE_URL}/images/default.jpg" 
        }
    }

    another_test_channel_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "test",
        'is_public': False
        }
    )
    assert another_test_channel_details.status_code == 200
    another_test_channel_details = another_test_channel_details.json()
    
    dm_1 = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": e_luxa_details['token'],
        "u_ids": []
    })
    assert dm_1.status_code == 200
    dm_1 = dm_1.json()    

    correct = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": e_luxa_details["token"],
        "img_url": "https://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP.jpg",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100,
        "y_end": 100,
    })
    assert correct.status_code == 200

    profile = requests.get(f"{BASE_URL}/user/profile/v1", params={
            'token': e_luxa_details['token'],
            'u_id': e_luxa_details['auth_user_id']
    })
    image_name = hashlib.sha256(str(e_luxa_details['auth_user_id']).encode()).hexdigest()
    assert profile.status_code == 200
    assert profile.json()['user']['profile_img_url'] != f'{BASE_URL}/images/default.jpg'
    assert profile.json()['user']['profile_img_url'] == f'{BASE_URL}/images/{image_name}.jpg'
    
    response = requests.get(f"{BASE_URL}/channel/details/v2", params = {
        'token': e_luxa_details['token'],
        'channel_id': another_test_channel_details['channel_id']
    })
    assert response.json() == {
        'name': 'test',
        'is_public': False,
        'owner_members': [
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f'{BASE_URL}/images/{image_name}.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f'{BASE_URL}/images/{image_name}.jpg'
            }
        ]
    }
    
    dm_1_details = requests.get(f'{BASE_URL}/dm/details/v1', params={
        'token': e_luxa_details['token'],
        'dm_id': dm_1['dm_id']
    })
    assert dm_1_details.status_code == 200
    dm_1_details = dm_1_details.json()
    
    assert dm_1_details == {
        'name': 'emilyluxa',
        'members': [
            {
                'u_id': e_luxa_details['auth_user_id'],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'emily',
                'name_last': 'luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f'{BASE_URL}/images/{image_name}.jpg'
            }
        ]
    }
