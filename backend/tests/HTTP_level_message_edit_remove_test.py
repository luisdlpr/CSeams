'''
This file contains all tests http requests through
route /message/edit/v1 and /message/remove/v1.
Written by Westley Lo
z5363938 UNSW COMP1531 22T1
'''

import requests, random
from src.config import url
from src.error import AccessError, InputError

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


######## message/edit/v1 tests #########

def test_message_edit_v1_in_channel_correct():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()
    
    user2_details = register_user_request('jingdoe@gmail.com',
        'johndoespassword123', 'Jing', 'Doe')
    assert user2_details.status_code == 200
    user2_details = user2_details.json()

    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()
    
    channel_join = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user1_details['token'],
        "channel_id": channel_details_valid['channel_id']
    })
    assert channel_join.status_code == 200

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()

    message = 'message2'
    send_request_details_details = send_message_request(user1_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m2_id = send_request_details_details.json()
    
    message = 'message3'
    send_request_details_details = send_message_request(user1_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m3_id = send_request_details_details.json()
    
    messages = channel_messages_request(user1_details['token'],
        channel_details_valid['channel_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ['message3', 'message2', "message1"]
    
    
    
    
    
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user1_details['token'],
        "message_id": m3_id['message_id'],
        "message": "Real new message"
    })
    assert edit_request.status_code == 200
    
    ### should've altered ###
    messages = channel_messages_request(user1_details['token'],
        channel_details_valid['channel_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ['Real new message', 'message2', "message1"]
    
    
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": m2_id['message_id'],
        "message": "Updated as global owner"
    })
    
    assert edit_request.status_code == 200
    
    messages = channel_messages_request(user1_details['token'],
        channel_details_valid['channel_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()    
    assert [message['message']for message in messages['messages']] == ['Real new message', 'Updated as global owner', "message1"]
    
    ####### obliterate a message #####
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": m2_id['message_id'],
        "message": ""
    })
    assert edit_request.status_code == 200
    
    messages = channel_messages_request(user1_details['token'],
        channel_details_valid['channel_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()    
    assert [message['message']for message in messages['messages']] == ['Real new message', "message1"]
    
    
    
    
    ####### making a dm right here #######
    dm_details_valid = dm_create_request(user1_details['token'], [owner_details['auth_user_id'], user2_details['auth_user_id']])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()
    
    
    message = 'message1'
    send_request_details_details = message_send_dm_request(owner_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()

    message = 'message2'
    send_request_details_details = message_send_dm_request(user1_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m2_id = send_request_details_details.json()
    
    message = 'message3'
    send_request_details_details = message_send_dm_request(user2_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m3_id = send_request_details_details.json()
    
    messages = dm_messages_request(user2_details['token'],
        dm_details_valid['dm_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ['message3', 'message2', "message1"]
    
    
    
    

    ##### altering dm messages #####
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user2_details['token'],
        "message_id": m3_id['message_id'],
        "message": "Real new message"
    })
    assert edit_request.status_code == 200
    
    ### should've altered ###
    messages = dm_messages_request(user1_details['token'],
        dm_details_valid['dm_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ["Real new message", 'message2', "message1"]
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user2_details['token'],
        "message_id": m3_id['message_id'],
        "message": "Alter"
    })
    assert edit_request.status_code == 200
    
    ### should've altered again###
    messages = dm_messages_request(user1_details['token'],
        dm_details_valid['dm_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ["Alter", "message2", "message1"]
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user1_details['token'],
        "message_id": m3_id['message_id'],
        "message": "Owner updates"
    })
    assert edit_request.status_code == 200
    
    ### should've altered again###
    messages = dm_messages_request(user1_details['token'],
        dm_details_valid['dm_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ["Owner updates", "message2", "message1"]
    
    ####### obliterate a message #####
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": m_id['message_id'],
        "message": ""
    })
    assert edit_request.status_code == 200
    
    messages = dm_messages_request(user1_details['token'],
        dm_details_valid['dm_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()    
    assert [message['message']for message in messages['messages']] == ["Owner updates", "message2"]
    
    
    
    
def test_invalid_message_id():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": 0,
        "message": "Real new message"
    })
    assert edit_request.status_code == InputError.code
    
def test_non_channel_member_edit():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()
    
    
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    
    
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user1_details['token'],
        "message_id": m_id['message_id'],
        "message": "Real new message"
    })
    assert edit_request.status_code == AccessError.code
    
def test_edit_channel_too_long():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()
    
    
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    
    
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": m_id['message_id'],
        "message": '''Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
    sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. 
    Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod 
    tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.
    At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren,
    no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet,
    consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et
    dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.
    Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. 
    Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat,
    vel illum dolore eu fe'''
    })
    assert edit_request.status_code == InputError.code
    
def test_invalid_message_id_not_in_channel():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": m_id['message_id'] + 20,
        "message": "Real new message"
    })
    assert edit_request.status_code == InputError.code
    

    
def test_edit_not_author():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json() 

    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    channel_join = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user1_details['token'],
        "channel_id": channel_details_valid['channel_id']
    })
    assert channel_join.status_code == 200

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user1_details['token'],
        "message_id": m_id['message_id'],
        "message": "Real new message"
    })
    assert edit_request.status_code == AccessError.code
    
    
def test_non_dm_member_edit():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()
    
    
    dm_details_valid = dm_create_request(owner_details['token'], [])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    message = 'message1'
    send_request_details_details = message_send_dm_request(owner_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    
    
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user1_details['token'],
        "message_id": m_id['message_id'],
        "message": "Real new message"
    })
    assert edit_request.status_code == AccessError.code
    

def test_edit_dm_message_too_long():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()
    
    
    dm_details_valid = dm_create_request(owner_details['token'], [])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    message = 'message1'
    send_request_details_details = message_send_dm_request(owner_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": m_id['message_id'],
        "message": '''Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
    sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. 
    Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod 
    tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.
    At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren,
    no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet,
    consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et
    dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.
    Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. 
    Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat,
    vel illum dolore eu fe'''
    })
    assert edit_request.status_code == InputError.code


def test_invalid_message_id_not_in_dm():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    dm_details_valid = dm_create_request(owner_details['token'], [])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    message = 'message1'
    send_request_details_details = message_send_dm_request(owner_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": m_id['message_id'] - 200,
        "message": "Real new message"
    })
    assert edit_request.status_code == InputError.code
    
def test_edit_not_author_in_dm():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json() 

    dm_details_valid = dm_create_request(owner_details['token'], [user1_details['auth_user_id']])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    message = 'message1'
    send_request_details_details = message_send_dm_request(owner_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user1_details['token'],
        "message_id": m_id['message_id'],
        "message": "Real new message"
    })
    assert edit_request.status_code == AccessError.code
    
def test_edit_message_50_messages_returned():
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
    
    message_id_list = []
    for message in message_list:
        message_details = send_message_request(owner_details['token'],
                    channel_details_valid['channel_id'], message)
        assert message_details.status_code == 200
        message_id_list.append(message_details.json()['message_id'])
    start_valid = 0

    ### remember, the most recent messages appear first ######
    message_id_list.reverse()
    message_list.reverse()

    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()
    
    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:start_valid + 50]
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": message_id_list[25],
        "message": "Real new message"
    })
    assert edit_request.status_code == 200
    message_list[25] = "Real new message"
    
    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()
    
    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:start_valid + 50]
    
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": owner_details['token'],
        "message_id": message_id_list[50],
        "message": "Unseen"
    })
    
    message_list[50] = "Unseen"

    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()
    
    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:start_valid + 50]
    
    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], 25)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()
    
    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[25:]
    
    




######### message/remove/v1 tests #######

def test_message_remove_v1_in_channel_correct():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()
    
    user2_details = register_user_request('jingdoe@gmail.com',
        'johndoespassword123', 'Jing', 'Doe')
    assert user2_details.status_code == 200
    user2_details = user2_details.json()

    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()
    
    channel_join = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user1_details['token'],
        "channel_id": channel_details_valid['channel_id']
    })
    assert channel_join.status_code == 200

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()

    message = 'message2'
    send_request_details_details = send_message_request(user1_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m2_id = send_request_details_details.json()
    
    message = 'message3'
    send_request_details_details = send_message_request(user1_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m3_id = send_request_details_details.json()
    
    messages = channel_messages_request(user1_details['token'],
        channel_details_valid['channel_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ['message3', 'message2', "message1"]
    
    
    
    
    
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user1_details['token'],
        "message_id": m3_id['message_id'],
    })
    assert edit_request.status_code == 200
    
    ### should've altered ###
    messages = channel_messages_request(user1_details['token'],
        channel_details_valid['channel_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ['message2', "message1"]
    
    
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": owner_details['token'],
        "message_id": m2_id['message_id'],
    })
    
    assert edit_request.status_code == 200
    
    messages = channel_messages_request(user1_details['token'],
        channel_details_valid['channel_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()    
    assert [message['message']for message in messages['messages']] == ["message1"]
    
    
    
    
    ####### making a dm right here #######
    dm_details_valid = dm_create_request(user1_details['token'], [owner_details['auth_user_id'], user2_details['auth_user_id']])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()
    
    message = 'message1'
    send_request_details_details = message_send_dm_request(owner_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()

    message = 'message2'
    send_request_details_details = message_send_dm_request(user1_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m2_id = send_request_details_details.json()
    
    message = 'message3'
    send_request_details_details = message_send_dm_request(user2_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m3_id = send_request_details_details.json()
    
    messages = dm_messages_request(user2_details['token'],
        dm_details_valid['dm_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ['message3', 'message2', "message1"]
    
    
    
    

    ##### altering dm messages #####
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user2_details['token'],
        "message_id": m3_id['message_id'],
    })
    assert edit_request.status_code == 200
    
    ### should've altered ###
    messages = dm_messages_request(user1_details['token'],
        dm_details_valid['dm_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ['message2', "message1"]
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user1_details['token'],
        "message_id": m2_id['message_id'],
    })
    assert edit_request.status_code == 200
    
    ### should've altered again###
    messages = dm_messages_request(user1_details['token'],
        dm_details_valid['dm_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == ["message1"]
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user1_details['token'],
        "message_id": m_id['message_id'],
    })
    assert edit_request.status_code == 200
    
    ### should've altered again###
    messages = dm_messages_request(user1_details['token'],
        dm_details_valid['dm_id'], 0)
    assert messages.status_code == 200
    messages = messages.json()
    assert [message['message']for message in messages['messages']] == []
    
    
    
    
    
def test_remove_invalid_message_id():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": owner_details['token'],
        "message_id": 0,
    })
    assert edit_request.status_code == InputError.code
    
def test_remove_non_channel_member():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()
    
    
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    
    
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user1_details['token'],
        "message_id": m_id['message_id'],
    })
    assert edit_request.status_code == AccessError.code
    
def test_remove_message_id_not_in_channel():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": owner_details['token'],
        "message_id": m_id['message_id'] + 20,
    })
    assert edit_request.status_code == InputError.code
    
def test_remove_not_author():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json() 

    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    channel_join = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user1_details['token'],
        "channel_id": channel_details_valid['channel_id']
    })
    assert channel_join.status_code == 200

    message = 'message1'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user1_details['token'],
        "message_id": m_id['message_id'],
    })
    assert edit_request.status_code == AccessError.code
    
    
def test_non_dm_member_remove():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()
    
    
    dm_details_valid = dm_create_request(owner_details['token'], [])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    message = 'message1'
    send_request_details_details = message_send_dm_request(owner_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user1_details['token'],
        "message_id": m_id['message_id'],
    })
    assert edit_request.status_code == AccessError.code
    

def test_remove_message_id_not_in_dm():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    dm_details_valid = dm_create_request(owner_details['token'], [])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    message = 'message1'
    send_request_details_details = message_send_dm_request(owner_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": owner_details['token'],
        "message_id": m_id['message_id'] - 200,
    })
    assert edit_request.status_code == InputError.code
    
def test_remove_not_author_in_dm():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json() 

    dm_details_valid = dm_create_request(owner_details['token'], [user1_details['auth_user_id']])
    assert dm_details_valid.status_code == 200
    dm_details_valid = dm_details_valid.json()

    message = 'message1'
    send_request_details_details = message_send_dm_request(owner_details['token'],
                dm_details_valid['dm_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user1_details['token'],
        "message_id": m_id['message_id'],
    })
    assert edit_request.status_code == AccessError.code
    
def test_remove_message_50_messages_returned():
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
    
    message_id_list = []
    for message in message_list:
        message_details = send_message_request(owner_details['token'],
                    channel_details_valid['channel_id'], message)
        assert message_details.status_code == 200
        message_id_list.append(message_details.json()['message_id'])
    start_valid = 0

    ### remember, the most recent messages appear first ######
    message_id_list.reverse()
    message_list.reverse()

    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()
    
    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:start_valid + 50]
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": owner_details['token'],
        "message_id": message_id_list[50],
    })
    assert edit_request.status_code == 200
    del message_list[50]
    
    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()
    
    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:start_valid + 50]
    
    edit_request = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": owner_details['token'],
        "message_id": message_id_list[10],
    })
    
    del message_list[10]

    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], start_valid)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()
    
    messages = [message['message'] for message in messages_details['messages']]
    assert messages == message_list[start_valid:start_valid + 50]
    
    messages_details = channel_messages_request(owner_details['token'], 
                channel_details_valid['channel_id'], 25)
    assert messages_details.status_code == 200
    messages_details = messages_details.json()
    
    messages = [message['message'] for message in messages_details['messages']]
    
    assert messages == message_list[25:]
    
    
    
    