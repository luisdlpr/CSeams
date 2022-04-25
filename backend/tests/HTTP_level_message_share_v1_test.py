'''
This file contains all tests http requests through
route /message/share/v1.
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

def message_share_request(token, og_message_id, channel_id, dm_id,message=None):
    ''' 
    BLACKBOX
    Makes a /message/share/v1 POST request then returns the response

    Arguments:
        Takes in a valid user token, og_message_id (refering to a valid message),
        channel_id (refering to a valid channel), dm_id (refering to a valid DM),
        and an optional message (string) 
    Return Value:
        { shared_message_id }
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/message/share/v1', json = {
        'token': token,
        'og_message_id': og_message_id,
        'channel_id': channel_id,
        'dm_id': dm_id,
        'message': message
        }
    )

############################################
def test_message_share_v1_only_negative_ids():
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200

    owner_details = auth_register_request('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    channel_details = channels_create_request(owner_details['token'], 'channel1', True)
    assert channel_details.status_code == 200
    channel_details = channel_details.json()

    # send a message in said channel
    message = 'Sent from test_message_share_v1_only_negative_ids'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()

    optional_message = 'optional message from test_message_share_v1_only_negative_ids'
    share_response = message_share_request(owner_details['token'], sent_message_details['message_id'],
                -1, -1, message=optional_message)
    assert share_response.status_code == InputError.code

def test_message_share_v1_no_negative_ids():
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

    message = 'Sent from test_message_share_v1_no_negative_ids'
    sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
    assert sent_message_details.status_code == 200
    sent_message_details = sent_message_details.json()

    request_reaponse = message_share_request(owner_details['token'], sent_message_details['message_id'],
                                        channel_details['channel_id'], dm_details['dm_id'])
    assert request_reaponse.status_code == InputError.code

def test_message_share_v1_og_message_id_invalid():
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

        message = 'Sent from test_message_share_v1_og_message_id_invalid'
        sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
        assert sent_message_details.status_code == 200
        sent_message_details = sent_message_details.json()

        # og_message_id canonly be > 1000000 or < -1000000
        # anything thing in between is not allowed
        request_resonpse = message_share_request(owner_details['token'], 42070, -1, dm_details['dm_id'])
        assert request_resonpse.status_code == InputError.code
        request_resonpse = message_share_request(owner_details['token'], -42068, -1, dm_details['dm_id'])
        assert request_resonpse.status_code == InputError.code
        # use valid id which have not yet been assigned
        request_resonpse = message_share_request(owner_details['token'], 2000000, -1, dm_details['dm_id'])
        assert request_resonpse.status_code == InputError.code
        request_resonpse = message_share_request(owner_details['token'], -2000000, -1, dm_details['dm_id'])
        assert request_resonpse.status_code == InputError.code

def test_message_share_v1_message_too_long():
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

        message = 'Sent from test_message_share_v1_message_too_long'
        sent_message_details = message_send_request(owner_details['token'], channel_details['channel_id'], message)
        assert sent_message_details.status_code == 200
        sent_message_details = sent_message_details.json()

        optional_message = ''
        for i in range(1001):
                optional_message += str(i)

        request_response = message_share_request(owner_details['token'], sent_message_details['message_id'],
                                        -1, dm_details['dm_id'], message=optional_message)
        assert request_response.status_code == InputError.code
'''
        sent_dm_message_details = message_send_dm_v1(owner_details['token'], dm_details['dm_id'], message)
AccessError when:
        
        the authorised user has not joined the channel or DM they are trying to share the message to
'''
def test_message_share_v1_user_not_in_channel():
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

        message = 'Sent from test_message_share_v1_message_too_long'
        sent_message_details = message_send_dm_request(owner_details['token'], dm_details['dm_id'], message)
        assert sent_message_details.status_code == 200
        sent_message_details = sent_message_details.json()

        request_response = message_share_request(user_details['token'], sent_message_details['message_id'],
                                    channel_details['channel_id'], -1)
        assert request_response.status_code == AccessError.code
        
def test_message_share_v1_user_not_in_dm():
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

        channel_details = channels_create_request(owner_details['token'], 'channel_valid', True)
        assert channel_details.status_code == 200
        channel_details = channel_details.json()
        dm_details = dm_create_request(user_details['token'], [user2_details['auth_user_id']])
        assert dm_details.status_code == 200
        dm_details = dm_details.json()

        # send a message in said channel
        message = 'Sent from test_message_share_v1_user_not_in_dm'
        sent_message_details = message_send_dm_request(user_details['token'], dm_details['dm_id'], message)
        assert sent_message_details.status_code == 200
        sent_message_details = sent_message_details.json()

        request_response = message_share_request(owner_details['token'], sent_message_details['message_id'],
                                        channel_details['channel_id'], -1)
        assert request_response.status_code == AccessError.code

############################## EDGE CASE COVERAGE ###############################
def test_message_share_v1_deleted_og_message():
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

        message = 'Sent from test_message_share_v1_deleted_og_message'
        sent_message_details = message_send_dm_request(user_details['token'], dm_details['dm_id'], message)
        assert sent_message_details.status_code == 200
        sent_message_details = sent_message_details.json()

        optional_message = ''
        # share message
        request_response = message_share_request(owner_details['token'], sent_message_details['message_id'],
                                channel_details['channel_id'], -1, optional_message)
        assert request_response.status_code == 200

        # delete og message
        remove_request = requests.delete(f'{BASE_URL}/message/remove/v1', json = {
            'token': owner_details['token'],
            'message_id': sent_message_details['message_id']
            }
        )
        assert remove_request.status_code == 200

        start_latest = 0
        messages_details = channel_messages_request(owner_details['token'], channel_details['channel_id'], start_latest)
        assert messages_details.status_code == 200
        messages_details = messages_details.json()
        messages = messages_details['messages']

        message = message.replace("\n", "\n\t")
        assert messages[0]['message'] == f'>\n\t{message}\n<\n' + f'{optional_message}'

################################ CORRECTNESS TESTS ################################
def test_message_share_v1_message_shared_succefully():
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

        # send a message in dm
        message = 'Sent from test_message_share_v1_message_shared_succefully'
        optional_message = 'Optional message from test_message_share_v1_message_shared_succefully'

        sent_message_details = message_send_dm_request(user_details['token'], dm_details['dm_id'], message)
        assert sent_message_details.status_code == 200
        sent_message_details = sent_message_details.json()
        shared_message_details = message_share_request(owner_details['token'], sent_message_details['message_id'],
                                channel_details['channel_id'], -1, optional_message)
        assert shared_message_details.status_code == 200
        shared_message_details = shared_message_details.json()

        # request 50 latest messges from our newly created channel
        start_latest = 0
        messages_details = channel_messages_request(owner_details['token'], channel_details['channel_id'], start_latest)
        assert messages_details.status_code == 200
        messages_details = messages_details.json()
        messages = messages_details['messages']

        assert shared_message_details['shared_message_id'] == messages[0]['message_id']
        assert optional_message in messages[0]['message']
        assert message in messages[0]['message']

        ### check that the string was correctly formatted
        message = message.replace("\n", "\n\t")
        assert messages[0]['message'] == f'>\n\t{message}\n<\n' + f'{optional_message}'
