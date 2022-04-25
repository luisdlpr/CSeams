'''
This file contains all tests http requests through
route /message/react/v1 and /message/unreact/v1.
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import requests
from src.config import url
from src.server import SECRET
from src.error import AccessError, InputError

BASE_URL = url

def auth_register_request(email, password, name_first, name_last):
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


def message_send_request(token, channel_id, message):
    '''
    BLACKBOX
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

def message_send_dm_request(token, dm_id, message):
    '''
    Makes a /message/senddm/v1 POST request then returns the response

    Arguments:
        Takes in a valid user token, dm_id (refering to a valid dm) and
        a message (string)
    Return Value:
        {'dm_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/message/senddm/v1', json = {
        'token': token,
        'dm_id': dm_id,
        'message': message
        }
    )
def dm_create_request(token, u_ids):
    '''
    BLACKBOX
    Makes a /dm/create/v1 POST request then returns the response

    Arguments:
        Takes in a valid user token, and a list of u_ids
    Return Value:
        {'dm_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/dm/create/v1', json = {
        'token': token,
        'u_ids': u_ids
        }
    )

def message_react_request(token, message_id, react_id):
    ''' 
    BLACKBOX
    Makes a /message/react/v1 POST request then returns the response

    Arguments:
        Takes in a valid user token, message_id (refering to a valid message),
        react_id (refering to a valid react)
    Return Value:
        {}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/message/react/v1', json = {
        'token': token,
        'message_id': message_id,
        'react_id': react_id
        }
    )

def message_unreact_request(token, message_id, react_id):
    ''' 
    BLACKBOX
    Makes a /message/unreact/v1 POST request then returns the response

    Arguments:
        Takes in a valid user token, message_id (refering to a valid message),
        react_id (refering to a valid react)
    Return Value:
        {}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/message/unreact/v1', json = {
        'token': token,
        'message_id': message_id,
        'react_id': react_id
        }
    )

########################################################
            # message_react_request tests #
########################################################
def test_message_v1_message_id_invalid():
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    user_details = auth_register_request('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
    assert user_details.status_code == 200
    user_details = user_details.json()

    channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()
    dm_details = dm_create_request(owner_details['token'], [user_details['auth_user_id']])
    assert dm_details.status_code == 200
    dm_details = dm_details.json()

    message = 'Sent from test_message_v1_invalid_react_id'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()

    message = 'Sent from test_message_v1_message_id_invalid'
    sent_message_dm_details = message_send_dm_request(owner_details['token'], dm_details['dm_id'], message)
    assert sent_message_dm_details.status_code == 200
    sent_message_dm_details = sent_message_dm_details.json()
    
    # try to react to non exiting message in channel of id 1
    assert message_react_request(user_details['token'], 1000042, 1).status_code == InputError.code
    # try to react to non exiting message in dm of id 1
    assert message_react_request(user_details['token'], -1000042, 1).status_code == InputError.code

    # try to react to invalid message_id in channel of id 1
    assert message_react_request(user_details['token'], 42070, 1).status_code == InputError.code
    # try to react to invalid message_id in dm of id 1
    assert message_react_request(user_details['token'], -42068, 1).status_code == InputError.code

def test_message_v1_invalid_react_id():
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()

    # send a message in said channel
    message = 'Sent from test_message_v1_invalid_react_id'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()

    assert message_react_request(owner_details['token'],
            sent_message_details['message_id'], -42).status_code == InputError.code

def test_message_v1_already_reacted():
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200
    
    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()

    # send a message in said channel
    message = 'Sent from test_message_v1_already_reacted'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()
   
    # first react
    message_react_request(owner_details['token'], sent_message_details['message_id'], 1)

    # second react
    assert message_react_request(owner_details['token'],
            sent_message_details['message_id'], 1).status_code == InputError.code

def test_message_v1_not_authorised():
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    user_details = auth_register_request('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
    assert user_details.status_code == 200
    user_details = user_details.json()
    user2_details = auth_register_request('damienlagado@gmail.com', 'damienlagadospassword123', 'Damien', 'Lagado')
    assert user2_details.status_code == 200
    user2_details = user2_details.json()

    # create a channel
    channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()
    # create a dm
    dm_details = dm_create_request(owner_details['token'], [user_details['auth_user_id']])
    assert dm_details.status_code == 200
    dm_details = dm_details.json()

    message = 'Sent from test_message_v1_not_authorised'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()

    sent_message_dm_details = message_send_dm_request(owner_details['token'], dm_details['dm_id'], message)
    assert sent_message_dm_details.status_code == 200
    sent_message_dm_details = sent_message_dm_details.json()
    
    # auth user not in channel
    assert message_react_request(user_details['token'],
        sent_message_details['message_id'], 1).status_code == AccessError.code
    # auth user not in dm
    assert message_react_request(user2_details['token'],
        sent_message_dm_details['message_id'], 1).status_code == AccessError.code

# test for correct behaviour
def test_message_v1_react_sent():
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # create a channel
    channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()

    # send a message in said channel
    message = 'Sent from test_message_v1_react_sent'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()

    # react to the message sent
    message_react_request(owner_details['token'], sent_message_details['message_id'], 1)
    
    most_recent_start = 0
    messages_details = channel_messages_request(owner_details['token'],
                channel_details['channel_id'],most_recent_start)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()

    message_reacts = messages_details['messages'][0]['reacts']
    
    assert {
        'react_id': 1,
        'u_ids': [owner_details['auth_user_id']],
        'is_this_user_reacted': True,
    } == message_reacts[0]

########################################################
            # message_react_request tests #
########################################################
def test_message_unreact_v1_message_id_invalid():
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    # register a pair of users
    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    user_details = auth_register_request('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
    assert user_details.status_code == 200
    user_details = user_details.json()

    # create a channel
    channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()
    # create a dm
    dm_details = dm_create_request(owner_details['token'], [user_details['auth_user_id']])
    assert dm_details.status_code == 200
    dm_details = dm_details.json()

	# send a message in said channel
    message = 'Sent from test_message_unreact_rv1_message_id_invalid'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()
    sent_message_dm_details = message_send_dm_request(owner_details['token'], dm_details['dm_id'], message)
    assert sent_message_dm_details.status_code == 200
    sent_message_dm_details = sent_message_dm_details.json()
    
    # try to unreact non exiting message in channel of id 1000001
    assert message_unreact_request(user_details['token'], 
        sent_message_details['message_id'] + 1, 1).status_code == InputError.code
    # try to unreact non exiting message in dm of id -1000001
    assert message_unreact_request(user_details['token'], 
        sent_message_dm_details['message_id'] - 1, 1).status_code == InputError.code

    # try to unreact invalid message_id in channel of id 42070
    assert message_unreact_request(user_details['token'], 42070, 1).status_code == InputError.code
    # try to unreact invalid message_id in dm of id -42068
    assert message_unreact_request(user_details['token'], -42068, 1).status_code == InputError.code

def test_message_unreact_v1_invalid_react_id():
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200
    
    # register a user
    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # create a channel
    channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()

    message = 'Sent from test_message_unreact_v1_message_id_invalid'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()
    assert message_react_request(owner_details['token'], sent_message_details['message_id'], 1).status_code == 200
    

    assert message_unreact_request(owner_details['token'],
                sent_message_details['message_id'], -42).status_code == InputError.code

def test_message_unreact_v1_already_unreacted():
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200
    
    # register a user
    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # create a channel
    channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()

    # send a message in said channel
    message = 'Sent from test_message_unreact_v1_message_id_invalid'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()

    # attempt unreact
    assert message_unreact_request(owner_details['token'],
         sent_message_details['message_id'], 1).status_code == InputError.code

def test_message_unreact_v1_unreact_sent():
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200
    
    # register a user
    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # create a channel
    channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()
    
    # send a message in said channel
    message = 'Sent from test_message_unreact_v1_unreact_sent'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()

    # react then unreact to the message sent
    assert message_react_request(owner_details['token'], sent_message_details['message_id'], 1).status_code == 200
    assert message_unreact_request(owner_details['token'], sent_message_details['message_id'], 1).status_code == 200

    most_recent_start = 0
    messages_details = channel_messages_request(owner_details['token'],
                channel_details['channel_id'],most_recent_start)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()

    message_reacts = messages_details['messages'][0]['reacts']
    
    assert {
        'react_id': 1,
        'u_ids': [],
        'is_this_user_reacted': False,
    } == message_reacts[0]

