'''
This file contains all tests http requests through
route /message/send/v1.
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import jwt
import requests
from src.config import url
from src.error import AccessError, InputError
import datetime
import time

SECRET = 'placeholder'
BASE_URL = url

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

##############

def test_message_send_v1_correct():
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

    message = 'Hello, Marry Jane.'
    send_request_details_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()

    start = 0
    messages = channel_messages_request(owner_details['token'],
        channel_details_valid['channel_id'], start)
    assert messages.status_code == 200
    messages = messages.json()

    assert messages['messages'][0]['message_id'] == m_id['message_id']

    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = int(utc_time.timestamp())

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        "token": owner_details['token'],
        "channel_id": channel_details_valid['channel_id'],
        "message": message,
        "time_sent": utc_timestamp + 1
    })
    
    assert response.status_code == 200

    time.sleep(1)


def test_message_send_v1_invalid_token():
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
    
    message = 'This message should not have gone through'
    send_request_details = send_message_request(token_invalid,
                channel_details_valid['channel_id'], message)
    assert send_request_details.status_code == AccessError.code
    
    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = int(utc_time.timestamp())

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        "token": token_invalid,
        "channel_id": channel_details_valid['channel_id'],
        "message": message,
        "time_sent": utc_timestamp + 1
    })
    
    assert response.status_code == AccessError.code

def test_message_send_v1_invalid_channel_id():
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # make a channel creation request (Return Type: {'channel_id': value})
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()
    
    #### invalid channel_id ########
    message = 'This message should not have gone through'
    send_request_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'] + 200, message)
    assert send_request_details.status_code == InputError.code

    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = int(utc_time.timestamp())

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        "token": owner_details['token'],
        "channel_id": channel_details_valid['channel_id'] + 200,
        "message": message,
        "time_sent": utc_timestamp + 1
    })
    
    assert response.status_code == InputError.code

def test_message_send_v1_message_too_short_and_too_long():
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    # make a channel creation request (Return Type: {'channel_id': value})
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()
    
    #### really long message ########
    message = '''Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
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
    send_request_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details.status_code == InputError.code

    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = int(utc_time.timestamp())

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        "token": owner_details['token'],
        "channel_id": channel_details_valid['channel_id'],
        "message": message,
        "time_sent": utc_timestamp + 1
    })
    
    assert response.status_code == InputError.code

    ###### Really short message ######
    message = ''
    send_request_details = send_message_request(owner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details.status_code == InputError.code

    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = int(utc_time.timestamp())

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        "token": owner_details['token'],
        "channel_id": channel_details_valid['channel_id'],
        "message": message,
        "time_sent": utc_timestamp + 1
    })
    
    assert response.status_code == InputError.code

def test_message_send_v1_message_non_channel_member():
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()

    nonowner_details = register_user_request('janedoe@gmail.com',
        'johndoespassword123', 'Jane', 'Doe')
    assert nonowner_details.status_code == 200
    nonowner_details = nonowner_details.json()

    # make a channel creation request (Return Type: {'channel_id': value})
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()
    
    #### Non channel member tries to send a emssage to the channel #####
    message = 'The dude is not in the channel'
    send_request_details = send_message_request(nonowner_details['token'],
                channel_details_valid['channel_id'], message)
    assert send_request_details.status_code == AccessError.code

    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = int(utc_time.timestamp())

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        "token": nonowner_details['token'],
        "channel_id": channel_details_valid['channel_id'],
        "message": message,
        "time_sent": utc_timestamp + 1
    })
    
    assert response.status_code == AccessError.code

def test_message_sendlater_v1_inputError_time():
    # clear_v1()
    clear = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear.status_code == 200

    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoes@gmail.com',
        'jjanedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()
    
    nonowner_details = register_user_request('jingdoe@gmail.com',
        'johndoespassword123', 'Jing', 'Doe')
    
    assert nonowner_details.status_code == 200
    nonowner_details = nonowner_details.json()

    # make a channel creation request (Return Type: {'channel_id': value})
    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()

    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = int(utc_time.timestamp())

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        "token": owner_details['token'],
        "channel_id": channel_details_valid['channel_id'],
        "message": "testmessage 123",
        "time_sent": utc_timestamp - 100
        }
    )
    
    assert response.status_code == InputError.code
    
    
def test_message_sendlater_tagging():
    # clear_v1()
    clear = requests.delete(f"{BASE_URL}/clear/v1")
    assert clear.status_code == 200
    
    owner_details = register_user_request('johndoe@gmail.com',
        'johndoespassword123', 'John', 'Doe')
    assert owner_details.status_code == 200
    owner_details = owner_details.json()
    
    user1_details = register_user_request('janedoe@gmail.com',
        'janedoespassword123', 'Jane', 'Doe')
    assert user1_details.status_code == 200
    user1_details = user1_details.json()

    channel_details_valid = channels_create_request(owner_details['token'], 'channel_valid', True)
    assert channel_details_valid.status_code == 200
    channel_details_valid = channel_details_valid.json()
    
    response = requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': user1_details['token'],
        'channel_id': channel_details_valid['channel_id']
    })
    assert response.status_code == 200

    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    
    message = 'Hello, @janedoe @johndoe'
    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        "token": owner_details['token'],
        "channel_id": channel_details_valid['channel_id'],
        "message": message,
        "time_sent": utc_timestamp + 1
    })
    assert response.status_code == 200
    m_id = response.json()
    
    time.sleep(2)
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": owner_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [
        {
            'channel_id': channel_details_valid['channel_id'],
            'dm_id': -1,
            'notification_message': "johndoe tagged you in channel_valid: Hello, @janedoe @joh"
        }
    ]
    
    start = 0
    messages = channel_messages_request(owner_details['token'],
        channel_details_valid['channel_id'], start)
    assert messages.status_code == 200
    messages = messages.json()
    assert messages['messages'][0]['message_id'] == m_id['message_id']