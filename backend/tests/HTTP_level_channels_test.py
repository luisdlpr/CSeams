'''
Same tests as those in channels_test.py, but now brought up to the HTTP layer.
It's used as a sanity check.
Typed up by Westley Lo
z5363938
'''

import requests
import jwt
from src.config import url
from src.error import InputError, AccessError

SECRET = 'placeholder'

BASE_URL = url

####### channel_listall_v1() focused tests ######

def test_listall_empty_channel_list():
    '''
        If there are no channels, then the funciton should return an empty list.
    '''
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
     
    all_channels = requests.get(f'{BASE_URL}/channels/listall/v2', params={
        "token": e_luxa_details['token']
    })
    assert all_channels.status_code == 200
    all_channels = all_channels.json()
    assert all_channels == {
        'channels' : [],
    }

def test_listall_private_and_public_channels():
    '''
        Create 2 channels, 1 public and 1 private, listall_v1 should then return a list of the
        channel details of both.
    '''
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
    channel_1name = "channel1"
    channel_2name = "channel2"
    
    channel1_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': channel_1name,
        'is_public': True
        }
    )
    assert channel1_details.status_code == 200
    channel1_details = channel1_details.json()
    
    channel2_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'],   
        'name': channel_2name,
        'is_public': False
        }
    )    
    assert channel2_details.status_code == 200
    channel2_details = channel2_details.json()
    
    all_channels = requests.get(f'{BASE_URL}/channels/listall/v2', params={
        "token": e_luxa_details['token']
    })
    assert all_channels.status_code == 200
    all_channels = all_channels.json()
    
    assert all_channels == {
        'channels': [
            {
                'channel_id': channel1_details["channel_id"],
                'name': "channel1"
            },
            {
                'channel_id': channel2_details["channel_id"],
                'name': "channel2"
            },           
        ]
    }

def test_non_user_listall():
    '''
        If the auth_user_id don't match any in datastore, an AccessError should be raised.
    '''
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    failure = requests.get(f'{BASE_URL}/channels/listall/v2', params={
        "token": jwt.encode({'auth_user_id': -1}, SECRET, algorithm='HS256')
    })
    assert failure.status_code == AccessError.code


####### channel_list_v1() focused tests ######

def test_list_empty_channel_list():
    '''
        If the user is not in any channels,
        then channels_list_v1 should return an empty list.
    '''
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

    listed_channels = requests.get(f'{BASE_URL}/channels/list/v2', params={
        'token': e_luxa_details['token']
    })
    assert listed_channels.status_code == 200
    listed_channels = listed_channels.json()
    
    assert listed_channels == {
        'channels': []
    }


def test_list_one_and_multiple_channels():
    '''
        Create a channel, then use channels_list_v1, it should list that channel's details.
        Create another channel with the same user, then user channels_list_v1 again,
        there should now be 2 items in the list.
    '''
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

    test_channel_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "test_channel",
        'is_public': True
        }
    )
    assert  test_channel_details.status_code == 200
    test_channel_details =  test_channel_details.json()

    listed_channels = requests.get(f'{BASE_URL}/channels/list/v2', params={
        'token': e_luxa_details['token']
    })
    assert listed_channels.status_code == 200
    listed_channels = listed_channels.json()
    assert listed_channels == {
        'channels': [
            {
                'channel_id': test_channel_details["channel_id"],
                'name': "test_channel"
            }
        ]
    }

    another_test_channel_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "another_test_channel",
        'is_public': False
        }
    )
    assert another_test_channel_details.status_code == 200
    another_test_channel_details = another_test_channel_details.json()

    listed_channels = requests.get(f'{BASE_URL}/channels/list/v2', params={
        'token': e_luxa_details['token']
    })
    assert listed_channels.status_code == 200
    listed_channels = listed_channels.json()

    assert listed_channels == {
        'channels': [
            {
                'channel_id': test_channel_details["channel_id"],
                'name': "test_channel"
            },
            {
                'channel_id': another_test_channel_details["channel_id"],
                'name': 'another_test_channel'
            }
        ]
    }

def test_list_multiple_users_in_different_channels():

    #Make two users, then make two channel for the first user.
    #    Ensure that the second user isn't in any channel.
    #    Make a channel for the second user, channels_list should then list only the third channel.
    #    have the second user join one of the first user's channel and list it again.
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
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()    
    
    channel1_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "channel1",
        'is_public': True
        }
    )
    assert  channel1_details.status_code == 200
    channel1_details =  channel1_details.json()

    channel2_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "channel2",
        'is_public': False
        }
    )
    assert  channel2_details.status_code == 200
    channel2_details =  channel2_details.json()

    # it should return an empty list because hayden isn't in any channel    
    listed_channels = requests.get(f'{BASE_URL}/channels/list/v2', params={
        'token': h_smith_details['token']
    })
    assert listed_channels.status_code == 200
    listed_channels = listed_channels.json()
    assert listed_channels == {
        'channels': []
    }

    # a channel is created for hayden, so there should be the details of one channel.
    channel3_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': h_smith_details['token'], 
        'name': "channel3",
        'is_public': True
        }
    )
    assert  channel3_details .status_code == 200
    channel3_details  =  channel3_details.json()
    listed_channels = requests.get(f'{BASE_URL}/channels/list/v2', params={
        'token': h_smith_details['token']
    })
    assert listed_channels.status_code == 200
    listed_channels = listed_channels.json()
    assert listed_channels == {
        'channels': [
            {
                'channel_id': channel3_details["channel_id"],
                'name': 'channel3',
            }
        ]
    }
    
    invitation = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        'token': e_luxa_details['token'],
        'channel_id': channel1_details["channel_id"],
        'u_id': h_smith_details['auth_user_id']
    })
    assert invitation.status_code == 200
    invitation = invitation.json()

    listed_channels = requests.get(f'{BASE_URL}/channels/list/v2', params={
        'token': h_smith_details['token']
    })
    assert listed_channels.status_code == 200
    listed_channels = listed_channels.json()
    assert listed_channels == {
        'channels': [
            {
                'channel_id': channel1_details["channel_id"],
                'name': 'channel1',
            },
            {
                'channel_id': channel3_details["channel_id"],
                'name': 'channel3',
            }
        ]
    }

def test_non_user_list():
    '''
        should raise AccessError if the user isn't even authorised.
    '''
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    faliure = requests.get(f'{BASE_URL}/channels/list/v2', params={
        "token": jwt.encode({'auth_user_id': -1}, SECRET, algorithm='HS256')
    })
    assert faliure.status_code == AccessError.code

######## channel_create_v1() focused tests ########

def test_make_public_channel():
        #Make a public channel

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

    created_channel_name = "channel1"
    created_channel_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': created_channel_name,
        'is_public': True
        }
    )
    assert created_channel_details.status_code == 200
    created_channel_details = created_channel_details.json()

    # The channel creator's name must be listed in the channel's members section and owners section
    channel_details = requests.get(f'{BASE_URL}/channel/details/v2', params={
        'token': e_luxa_details['token'],
        'channel_id': created_channel_details['channel_id']
    })
    assert channel_details.status_code == 200
    channel_details = channel_details.json()
    
    assert channel_details == {
        'name': created_channel_name,
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
        ],
    }
'''
def test_make_private_channel():
    clear_v1()
    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password', 'Emily', 'Luxa')

    channel_name = "channel1"

    channel_details = channels_create_v1(e_luxa_details["auth_user_id"], channel_name, False)

    # The channel creator's name must be listed in the channel's members section and owners section

    assert channel_details_v1(e_luxa_details["auth_user_id"], channel_details["channel_id"]) == {
        'name': channel_name,
        'is_public': False,
        'owner_members': [
            {
                'u_id': e_luxa_details["auth_user_id"],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Emily',
                'name_last': 'Luxa',
                'handle_str': 'emilyluxa'
            }
        ],
        'all_members': [
            {
                'u_id': e_luxa_details["auth_user_id"],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Emily',
                'name_last': 'Luxa',
                'handle_str': 'emilyluxa'
            }
        ],
    }
    clear_v1()
'''

def test_channel_input_error():
    '''
    Make a public channel, with empty string, should raise InputError.
    '''
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    # InputError should be raised for channel names less than 1 character, or greater than 20
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()

    faliure = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "",
        'is_public': True
        }
    )
    assert faliure.status_code == InputError.code


def test_channel_input_error_2():
    '''
    Make a public channel, with really long name, should raise InputError.
    '''

    # InputError should be raised for channel names less than 1 character, or greater than 20
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    # InputError should be raised for channel names less than 1 character, or greater than 20
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    faliure = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "dfoiausofiaufpoauifdp",
        'is_public': True
        }
    )
    assert faliure.status_code == InputError.code

def test_non_user_create():
    '''
        should raise AccessError if the user isn't even authorised.
    '''

    faliure = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': jwt.encode({'auth_user_id': -1}, SECRET, algorithm='HS256'), 
        'name': "unauthorised",
        'is_public': True
        }
    )
    assert faliure.status_code == AccessError.code