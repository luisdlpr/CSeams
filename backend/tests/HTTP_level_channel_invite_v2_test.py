'''
This file contains http level test function for
channel/invite/v2.
Written by: Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import jwt
import requests
from src.config import url
from src.error import AccessError, InputError

SECRET = 'placeholder'

BASE_URL = url

######################### HELPER FUNCTIONS #####################################

def register_user_request(email, password, name_first, name_last):
    '''
    BLACKBOX
    Makes a /auth/register/v2 POST request then returns the response.
    
    Arguements:
        Takes in user details email, password, name_first and name_last.
    Return Value:
        {'token', 'auth_user_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/auth/register/v2', json = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
        }
    )

def channels_create_request(token, name, is_public):
    '''
    BLACKBOX
    Makes a /channels/create/v2 POST request then returns the response

    Arguments:
        Takes in a valid user token, name (for channel's name) and privacy status
        is_public.
    Return Value:
        {'channle_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/channels/create/v2', json = {
        'token': token,
        'name': name,
        'is_public': is_public
        }
    )

def channel_messages_request(token, channel_id, start):
    '''
    BLACKBOX
    Makes a /channel/messages/v2 GET request then returns the response

    Arguments:
        Takes in a valid user token, channel_id (refering to a valid channel) and 
        start (the first massage of a list to be returned). 
    Return Value:
        {'channle_id'}
    Return Type:
        Response object
    '''
    return requests.get(f'{BASE_URL}/channel/messages/v2', params = {
        'token': token,
        'channel_id': channel_id,
        'start': start
        }
    )


def send_message_request(token, channel_id, message):
    '''
    Makes a /message/send/v1 POST request then returns the response

    Arguments:
        Takes in a valid user token, channel_id (refering to a valid channel) and
        a message (string)
    Return Value:
        {'channle_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/message/send/v1', json = {
        'token': token,
        'channel_id': channel_id,
        'message': message
        }
    )

def invite_user_request(token, channel_id, u_id):
    '''
    BLACKBOX
    Makes a /channel/invite/v2 POST request then returns the response

    Arguments:
        Takes in a valid user token, channel_id (refering to a valid channel) and
        a valid u_id
    Return Value:
        {}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/channel/invite/v2', json = {
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
        }
    )

######################### HELPER FUNCTIONS #####################################

# 1. channel_id does not refer to a valid channel InputError
def test_channel_invite_v2_invalid_channel_id():
    '''
    Tests that when channel_id does not refer to a valid channel,
    channel_invite_v2 raises an InputError (403)
    '''
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
                'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    user_details = register_user_request('janedoe@gmail.com',
                'janedoespassword123', 'Jane', 'Doe')
    assert user_details.status_code == 200
    user_details = user_details.json()

    # no channel was created. all possitive id refer to an invalid channel
    channel_id_invalid = 1

    invite_status = invite_user_request(owner_details['token'],
                    channel_id_invalid, user_details['auth_user_id'])
    assert invite_status.status_code == InputError.code

# 2. u_id does not refer to a valid user InputError
def test_channel_invite_v2_invalid_u_id():
    '''
    Tests that when u_id does not refer to a valid channel,
    channel_invite_v2 raises an InputError
    '''
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = register_user_request('johndoe@gmail.com',
                'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    channel_details_valid = channels_create_request(owner_details['token'],
                'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    # only one user registered, any id other than 1 is invalid
    u_id_invalid = 2

    invite_status = invite_user_request(owner_details['token'],
                    channel_details_valid['channel_id'], u_id_invalid)
    assert invite_status.status_code == InputError.code
    

# 3. u_id refers to a user who is already a member of the channel InputError
def test_channel_invite_v2_existing_u_id():
    '''
    Tests that when u_id refers to a user who is already a member of the channel,
    channel_invite_v1 raises an InputError
    '''
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200
    
    # register owner
    owner_details = register_user_request('johndoe@gmail.com',
                'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # create channel
    channel_details_valid = channels_create_request(owner_details['token'],
                'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    # create user
    user_details = register_user_request('janedoe@gmail.com',
                'janedoespassword123', 'Jane', 'Doe')
    assert user_details.status_code == 200
    user_details = user_details.json()

    # invite user first time (everything goes fine)
    invite_status = invite_user_request(owner_details['token'],
                    channel_details_valid['channel_id'], user_details['auth_user_id'])
    assert invite_status.status_code == 200

    # invite user second time (InputError is raised)
    invite_status = invite_user_request(owner_details['token'],
                    channel_details_valid['channel_id'], user_details['auth_user_id'])
    assert invite_status.status_code == InputError.code

# 4. channel_id is valid and the authorised user is not a member of the channel AccessError
def test_channel_invite_v2_non_member_auth():
    '''
    Test that when and the authorised user is not a member of the channel,
    channel_invite_v1 raises and AccessError
    '''
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200
    
    # register owner
    owner_details = register_user_request('johndoe@gmail.com',
                'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # create channel
    channel_details_valid = channels_create_request(owner_details['token'],
                'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    # create first user
    user_details_first = register_user_request('janedoe@gmail.com',
                'janedoespassword123', 'Jane', 'Doe')
    assert user_details_first.status_code == 200
    user_details_first = user_details_first.json()

    # create second user
    user_details_second = register_user_request('jacobdoe@gmail.com',
                'jacobdoespassword123', 'Jacob', 'Doe')
    assert user_details_second.status_code == 200
    user_details_second = user_details_second.json()

    # invite second user with first user's token  (AccessError is raised)
    invite_status = invite_user_request(user_details_first['token'],
                    channel_details_valid['channel_id'], user_details_second['auth_user_id'])
    assert invite_status.status_code == AccessError.code

#Test for correct behaviour (ensure u_id is in channel after invite is sent)
def test_channel_invite_v2_user_added():
    '''
    Test that when a valid auth_user_id, a valid u_id, and a valid channel_id are passed
    to channel_invite_v1, the user of u_id "u_id" is added to channel of channel_id "channel_id".

    Functions used:
        src.channel.channel_details_before_v1
    '''
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    # register owner
    owner_details = register_user_request('johndoe@gmail.com',
                'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # create channel
    channel_details_valid = channels_create_request(owner_details['token'],
                'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    # create user
    user_details = register_user_request('janedoe@gmail.com',
                'janedoespassword123', 'Jane', 'Doe')
    assert user_details.status_code == 200
    user_details = user_details.json()

    # invite user (everything goes fine)
    invite_status = invite_user_request(owner_details['token'],
                    channel_details_valid['channel_id'], user_details['auth_user_id'])
    assert invite_status.status_code == 200

    # invited user check for channel details
    # if channel details request fails then he was not added successfully
    channel_details_request = requests.get(f'{BASE_URL}/channel/details/v2', params = {
        'token': user_details['token'],
        'channel_id': channel_details_valid['channel_id'],
        }
    )
    assert channel_details_request.status_code == 200

def test_channel_invite_v2_invalid_token():
    '''
    Test that when a valid user is invite to a valid channel but
    the authorised user has an invalid token, channel/invite/v2 raises
    an AccessError
    '''
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    # register owner
    owner_details = register_user_request('johndoe@gmail.com',
                'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # create channel
    channel_details_valid = channels_create_request(owner_details['token'],
                'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    # create user
    user_details = register_user_request('janedoe@gmail.com',
                'janedoespassword123', 'Jane', 'Doe')
    assert user_details.status_code == 200
    user_details = user_details.json()
    
    # generate fake token
    # id 72 was never allocated as there are only 2 users
    # u_id: 1 and u_id: 2
    fake_token = jwt.encode({'auth_user_id': 72, 'session_id': 4}, SECRET, algorithm = 'HS256')

    # invite user using fake token(AccessError is raised)
    invite_status = invite_user_request(fake_token,
                    channel_details_valid['channel_id'], user_details['auth_user_id'])
    assert invite_status.status_code == AccessError.code
