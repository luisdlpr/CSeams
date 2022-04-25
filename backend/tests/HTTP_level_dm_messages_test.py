'''
dm/messages/v2 tests to ensure the implementation in
server.py in correct.
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import random
import requests
from src.config import url
from src.error import InputError, AccessError

BASE_URL = url

############## HELPER FUNCTIONS
def generate_string():
    MIN_LIMIT = 32    # from 'a' ascii value to
    MAX_LIMIT = 126   # '~' ascii value
    
    random_string = ''
 
    for _ in range(20):
        random_integer = random.randint(MIN_LIMIT, MAX_LIMIT)
    # Keep appending random characters using chr(x)
        random_string += (chr(random_integer))
    
    return random_string


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

def dm_messages_request(token, dm_id, start):
    '''
    BLACKBOX
    Makes a /dm/messages/v1 GET request then returns the response

    Arguments:
        Takes in a valid user token, dm_id (refering to a valid dm) and 
        start (the first massage of a list to be returned). 
    Return Value:
        {'channle_id'}
    Return Type:
        Response object
    '''
    return requests.get(f'{BASE_URL}/dm/messages/v1', params = {
        'token': token,
        'dm_id': dm_id,
        'start': start
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

############

def test_dm_messages_v1_no_messages():
    '''
    Test that when given a dm with no messages, dm_messages_v1 return
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
    
    # make a second user create request
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()

    # create a dm
    dm_details_valid = dm_create_request(owner_details['token'], [user1_details['auth_user_id']])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()
    start_valid = 0

    # request all messages from dm for analysis
    messages = dm_messages_request(owner_details['token'], 
                dm_details_valid['dm_id'], start_valid)
    assert messages.status_code == 200
    messages = messages.json()

    correct_output = {
        'messages': [],
        'start': 0,
        'end': -1
    }
    assert messages == correct_output

def test_dm_messages_v1_50_messages_returned():
    '''
    Test that when given a dm with no messages, dm_messages_v1 return
    {
        'messages': [start:start+50],
        'start': start,
        'end': start+50
    }
    '''
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200
    # register first user
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    # register a second user
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()

    # create a dm
    dm_details_valid = dm_create_request(owner_details['token'], [user1_details['auth_user_id']])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    message_list = []
    # send 51 messages to the dm
    for message_count in range(51):
        message_list.append(generate_string() + '--|' +  str(message_count))
    
    for message in message_list:
        message_details = message_send_dm_request(owner_details['token'],
                    dm_details_valid['dm_id'], message)
        assert message_details.status_code == 200
    start_valid = 0

    message_list.reverse()
    
    # request all messages from dm for analysis
    messages_details = dm_messages_request(owner_details['token'], 
                dm_details_valid['dm_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()

    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:start_valid + 50]

def test_dm_messages_v1_less_than_50_returned():
    '''
    Test that when given a dm with len(dm_messages)-start - 50, 
    dm_messages_v1 returns
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

    # make a user cretion request
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # make a second user create request
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()

    # create a dm
    dm_details_valid = dm_create_request(owner_details['token'], [user1_details['auth_user_id']])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    message_list = []
    # send 51 messages to the dm
    for message_count in range(51):
        message_list.append(generate_string() + '--|' +  str(message_count))
    
    for message in message_list:
        message_details = message_send_dm_request(owner_details['token'],
                    dm_details_valid['dm_id'], message)
        assert message_details.status_code == 200
        
    message_list.reverse()
    
    start_valid = 25

    # request all messages from dm for analysis
    messages_details = dm_messages_request(owner_details['token'], 
                dm_details_valid['dm_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()

    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:]
    
def test_dm_messages_v2_invalid_dm_id():
    '''
    Test that when an InputError is raised when dm_id does not
    refer to a valid dm
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
    
    # no dms exist so any positive value refers to an invalid dm
    dm_id_invalid = 1
    start_valid = 0

    # make dm/messages/v2 request
    messages = dm_messages_request(user_details['token'],
        dm_id_invalid, start_valid)
    assert messages.status_code == InputError.code
    
def test_dm_messages_v2_messages_invalid_start():
    '''
    Test that when start is greater than the total emount of messages in
    the given dm, an InputError is raised.
    '''
    # clear_v2()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    # make a user creation request
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # make a dm creation request (Return Type: {'dm_id': value})
    dm_details_valid = dm_create_request(owner_details['token'], [])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    # add message to invalid_start dm list (Return Type {'message_id': value})
    message_details = message_send_dm_request(owner_details['token'], dm_details_valid['dm_id'], 'Hello, Jane Doe!')
    assert message_details.status_code == 200

    # we no longer need to check the length of message as we have only sent 1
    '''
    max_start = len(data['dms'][0]['dm_messages']) - 1
    if max_start < 0:
        max_start = 0
    '''
    # max_start = 0
    start_invalid = 1
    # make dm/messages/v2 request (Return Type {'messages', 'start', 'end'})
    messages = dm_messages_request(owner_details['token'], 
                dm_details_valid['dm_id'], start_invalid)
    assert messages.status_code == InputError.code
    
def test_dm_messages_v2_token_refers_to_non_member_details():
    '''
    Test that when givena a valid dm_id but invalid token, 
    /dm/messages/v2 raises an AccessError
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

    # make a dm creation request (Return Type: {'dm_id': value})
    dm_details_valid = dm_create_request(owner_details['token'], [])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()
    
    start_valid = 0
    messages = dm_messages_request(non_member_details['token'], 
                dm_details_valid['dm_id'], start_valid)
    assert messages.status_code == AccessError.code