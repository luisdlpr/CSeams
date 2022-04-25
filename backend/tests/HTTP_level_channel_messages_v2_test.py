'''
channel/messages/v2 tests to ensure the implementation in
server.py in correct.
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import random
import requests
import jwt
from src.config import url
from src.error import InputError, AccessError

SECRET = 'placeholder'
BASE_URL = url
def generate_string():
    MIN_LIMIT = 32    # from 'a' ascii value to
    MAX_LIMIT = 126   # '~' ascii value
    
    random_string = ''
 
    for _ in range(20):
        random_integer = random.randint(MIN_LIMIT, MAX_LIMIT)
    # Keep appending random characters using chr(x)
        random_string += (chr(random_integer))
    
    return random_string


############## HELPER FUNCTIONS
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

##############
# 1. channel_id does not refer to a valid channel (InputError)
def test_channel_messages_v2_invalid_channel_id():
    '''
    Test that when an InputError is raised when channel_id does not
    refer to a valid channel
    '''
    # clear_v2()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    # make a user creation request
    user_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')

    # make sure our request was successful
    assert user_details.status_code == 200 
    # convert our response to json
    user_details = user_details.json()
    
    # no channels exist so any positive value refers to an invalid channel
    channel_id_invalid = 1
    start_valid = 0

    # make channel/messages/v2 request
    messages = channel_messages_request(user_details['token'],
        channel_id_invalid, start_valid)
    assert messages.status_code == InputError.code

# 2. start is greater than the total number of messages in the channel (InputError)
def test_channel_messages_v2_messages_invalid_start():
    '''
    Test that when start is greater than the total emount of messages in
    the given channel, an InputError is raised.
    '''
    # clear_v2()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    # make a user creation request
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # make a channel creation request (Return Type: {'channel_id': value})
    channel_details_valid = channels_create_request(owner_details['token'], 'invalid_start', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    # add message to invalid_start channel list (Return Type {'message_id': value})
    message_details = send_message_request(owner_details['token'], channel_details_valid['channel_id'], 'Hello, Jane Doe!')
    assert message_details.status_code == 200

    # we no longer need to check the length of message as we have only sent 1
    '''
    max_start = len(data['channels'][0]['channel_messages']) - 1
    if max_start < 0:
        max_start = 0
    '''
    # max_start = 0
    start_invalid = 1
    # make channel/messages/v2 request (Return Type {'messages', 'start', 'end'})
    messages = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_invalid)
    assert messages.status_code == InputError.code

# 3. channel_id is valid and the authorised user is not a member of the channel (AccessError)
def test_channel_messages_v2_token_refers_to_non_member_details():
    '''
    Test that when givena a valid channel_id but invalid token, 
    /channel/messages/v2 raises an AccessError
    '''
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    non_member_details = register_user_request('janedoe@gmail.com',
        'janedoespassword123', 'Jane', 'Doe')
    assert non_member_details.status_code == 200
    non_member_details = non_member_details.json()

    # make a channel creation request (Return Type: {'channel_id': value})
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()
    
    start_valid = 0
    messages = channel_messages_request(non_member_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages.status_code == AccessError.code

# 4. (AccessError)
def test_channel_messages_v2_invalid_token_given():
    '''
    Test that when given a non existing token, channel/messages/v2
    raises an AccessError
    '''
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    # generate a bogus token
    token_invalid = jwt.encode({'auth_user_id': 0}, SECRET, algorithm = 'HS256')

    # make a channel creation request (Return Type: {'channel_id': value})
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()
    start_valid = 0

    messages = channel_messages_request(token_invalid, 
                channel_details_valid['channel_id'], start_valid)
    assert messages.status_code == AccessError.code

# 5. correct output
def test_channel_messages_v2_no_messages():
    '''
    Test that when given a channel with no messages, channel_messages_v2 return
    {
        'messages': [],
        'start': start,
        'end': -1
    }
    '''
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    # make a user creation request
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()
    start_valid = 0

    messages = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages.status_code == 200
    messages = messages.json()

    correct_output = {
        'messages': [],
        'start': 0,
        'end': -1
    }
    assert messages == correct_output

def test_channel_messages_v2_50_messages_returned():
    '''
    Test that when given a channel with no messages, channel_messages_v2 return
    {
        'messages': [start:start+50],
        'start': start,
        'end': start+50
    }
    '''
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    message_list = []
    # send 51 messages to the channel
    for message_count in range(51):
        message_list.append(generate_string() + '--|' +  str(message_count))
    
    for message in message_list:
        message_details = send_message_request(owner_details['token'],
                    channel_details_valid['channel_id'], message)
        assert message_details.status_code == 200
    start_valid = 0

    ### remember, the most recent messages appear first ######
    message_list.reverse()

    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()

    #correct_output = {
    #    'messages': [{'message_id': message[0], 'u_id': owner_details['auth_user_id'], 'message': message[1]} for message in messages_expected[:]],
    #    'start': start_valid,
    #    'end': start_valid + 50
    #}
    #assert messages['messages'] == correct_output
    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:start_valid + 50]

def test_channel_messages_v2_less_than_50_returned():
    '''
    Test that when given a channel with len(channel_messages)-start - 50, 
    channel_messages_v2 returns
    {
        'messages': [start:-1],
        'start': start,
        'end': -1
    }
    This test is identical to the previous one with only 'end' 
    being different. implement when helper functions are available.
    '''
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    message_list = []
    # send 51 messages to the channel
    for message_count in range(51):
        message_list.append(generate_string() + '--|' +  str(message_count))
    
    for message in message_list:
        message_details = send_message_request(owner_details['token'],
                    channel_details_valid['channel_id'], message)
        assert message_details.status_code == 200
    
    message_list.reverse()
    
    start_valid = 25

    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()

    #correct_output = {
    #    'messages': [{'message_id': message[0], 'u_id': owner_details['auth_user_id'], 'message': message[1]} for message in messages_expected[start_valid:]],
    #    'start': start_valid,
    #    'end': -1
    #}
    #assert messages['messages'] == correct_output
    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:]
