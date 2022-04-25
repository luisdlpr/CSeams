'''
01.04.22

Contains tests for standup functions (http endpoint).

Luis Vicente De La Paz Reyes (z5206766)
'''

import pytest
import requests
import json
from src import config
import jwt
import datetime
import time
from src.error import AccessError, InputError
import threading

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"
SECRET = 'placeholder'

# does nothing for threading delays.
def nullfunction():
    return

# standup/start/v1

def test_standup_start_basic():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']
    
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail2@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']
    u_id2 = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail3@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy3"
    })
    
    u_id3 = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token1,
        "channel_id": channel1_id,
        "u_id": u_id2
    })

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token1,
        "channel_id": channel1_id,
        "u_id": u_id3
    })

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 2',
        'is_public': False
    })

    channel2_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token1,
        "channel_id": channel2_id,
        "u_id": u_id2
    })

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token1,
        "channel_id": channel2_id,
        "u_id": u_id3
    })

    length = 1
    tolerance = 1
    current = time.mktime(datetime.datetime.now().timetuple())

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token2,
        "channel_id": channel1_id,
        "length": length
    })

    assert response.json()['time_finish'] <= current + length + tolerance
    assert response.json()['time_finish'] >= current + length - tolerance

    current = time.mktime(datetime.datetime.now().timetuple())

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel2_id,
        "length": length
    })

    assert response.json()['time_finish'] <= current + length + tolerance
    assert response.json()['time_finish'] >= current + length - tolerance

    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()

    current = time.mktime(datetime.datetime.now().timetuple())

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "length": length
    })

    assert response.json()['time_finish'] <= current + length + tolerance
    assert response.json()['time_finish'] >= current + length - tolerance
    
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()


# test_standup_start_InputErr_ch_id - tests that function returns correct error 
# (InputError) when channel_id refers to invalid channel.
def test_standup_start_InputErr_ch_id():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })
    
    length = 1

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": -10000,
        "length": length
    })

    assert response.status_code == InputError.code

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": 10000,
        "length": length
    })

    assert response.status_code == InputError.code

# test_standup_start_InputErr_neg_length - tests that function returns correct
# error (InputError) when length given is a negative integer.
def test_standup_start_InputErr_neg_length():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "length": -100
    })

    assert response.status_code == InputError.code

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "length": -1
    })

    assert response.status_code == InputError.code

# test_standup_start_InputErr_stup_active - tests that function returns correct
# error (InputError) when standup is already active in channel.
def test_standup_start_InputErr_stup_active():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']
    
    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "length": 1
    })

    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "length": 1
    })

    assert response.status_code == InputError.code

    time.sleep(1)

# test_standup_start_AccessErr_non_member - tests that function returns correct
# error (AccessError) when auth user is not a member of the selected channel.
def test_standup_start_AccessErr_non_member():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail2@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']    

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 2',
        'is_public': False
    })

    channel2_id = response.json()['channel_id']
    
    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token2,
        "channel_id": channel1_id,
        "length": 1
    })

    assert response.status_code == AccessError.code    

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token2,
        "channel_id": channel2_id,
        "length": 1
    })

    assert response.status_code == AccessError.code

# test_standup_start_no_response - tests that function does not send msg
# when no contributions are made.
def test_standup_start_no_response():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "length": 1
    })

    t = threading.Timer(1, nullfunction)
    t.start()
    t.join()

    response = requests.get(f'{BASE_URL}/channel/messages/v2', params = {
        'token': token1,
        'channel_id': channel1_id,
        'start': 0
    })
    
    assert response.json() == {
        'messages': [],
        'start': 0,
        'end': -1
    }

# standup/active/v1

# tests basic functionality and correct return types in various scenario:
# for private and public channels, called by channel owner, global owner, and
# member:
#   on fresh channel create
#   during standup period
#   after standup period has completed
def test_standup_active_basic():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']
    
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail2@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']
    u_id2 = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token1,
        "channel_id": channel1_id,
        "u_id": u_id2
    })

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 2',
        'is_public': False
    })

    channel2_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token1,
        "channel_id": channel2_id,
        "u_id": u_id2
    })

    correct_response = {
        'is_active': False,
        'time_finish': None
    }

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel1_id
    })

    assert response.json() == correct_response

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token2,
        'channel_id': channel2_id
    })

    assert response.json() == correct_response

    length = 1

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token2,
        "channel_id": channel1_id,
        "length": length
    })

    time_channel_1 = response.json()['time_finish']

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel2_id,
        "length": length
    })

    time_channel_2 = response.json()['time_finish']

    correct_response1 = {
        'is_active': True,
        'time_finish': time_channel_1
    }

    correct_response2 = {
        'is_active': True,
        'time_finish': time_channel_2
    }

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token2,
        'channel_id': channel1_id
    })

    assert response.json() == correct_response1

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel2_id
    })

    assert response.json() == correct_response2

    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token2,
        'channel_id': channel1_id
    })

    assert response.json() == correct_response

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel2_id
    })

    assert response.json() == correct_response

# test_standup_active_AccessErr_non_member - tests that function returns correct
# error (AccessError) when auth user is not a member of the selected channel.
def test_standup_active_AccessErr_non_member():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail2@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']    

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 2',
        'is_public': False
    })

    channel2_id = response.json()['channel_id']
    
    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        "token": token2,
        "channel_id": channel1_id,
    })

    assert response.status_code == AccessError.code

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        "token": token2,
        "channel_id": channel2_id,
    })

    assert response.status_code == AccessError.code

# test_standup_active_InputErr_ch_id - tests that function returns correct error 
# (InputError) when channel_id refers to invalid channel.
def test_standup_active_InputErr_ch_id():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })
    
    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        "token": token1,
        "channel_id": -10000,
    })

    assert response.status_code == InputError.code

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        "token": token1,
        "channel_id": 10000,
    })

    assert response.status_code == InputError.code

# standup/send/v1

# test_standup_send_basic - tests that function can be used for public and private 
# channels, by any member, and that the return is correct
def test_standup_send_basic():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']
    
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail2@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']
    u_id2 = response.json()['auth_user_id']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token1,
        "channel_id": channel1_id,
        "u_id": u_id2
    })

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 2',
        'is_public': False
    })

    channel2_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channel/invite/v2", json = {
        "token": token1,
        "channel_id": channel2_id,
        "u_id": u_id2
    })

    length = 1

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token2,
        "channel_id": channel1_id,
        "length": length
    })

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token2,
        'channel_id': channel1_id
    })

    assert response.json()['is_active'] == True

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "message": 'testmessage1'
    })

    assert response.status_code == 200
    assert response.json() == {}

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token2,
        "channel_id": channel1_id,
        "message": 'testmessage2'
    })

    assert response.status_code == 200
    assert response.json() == {}
    
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token2,
        'channel_id': channel1_id
    })

    assert response.json()['is_active'] == False

    response = requests.get(f"{BASE_URL}/channel/messages/v2", params = {
        'token': token2,
        'channel_id': channel1_id,
        'start': 0
    })

    assert response.json()['messages'][0]['message'] == \
         "testdummy1: testmessage1\ntestdummy2: testmessage2\n"

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel2_id,
        "length": length
    })

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel2_id
    })

    assert response.json()['is_active'] == True

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token1,
        "channel_id": channel2_id,
        "message": 'testmessage3'
    })

    assert response.status_code == 200
    assert response.json() == {}

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token2,
        "channel_id": channel2_id,
        "message": 'testmessage4'
    })

    assert response.status_code == 200
    assert response.json() == {}
    
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel2_id
    })

    assert response.json()['is_active'] == False

    response = requests.get(f"{BASE_URL}/channel/messages/v2", params = {
        'token': token1,
        'channel_id': channel2_id,
        'start': 0
    })

    assert response.json()['messages'][0]['message'] == \
         "testdummy1: testmessage3\ntestdummy2: testmessage4\n"

# test_standup_send_InputError_ch_id - tests that function raises InputError
# when an invalid channel is selected
def test_standup_send_InputError_ch_id():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })
    
    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token1,
        "channel_id": -10000,
        "message": 'testmessage1'
    })

    assert response.status_code == InputError.code

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token1,
        "channel_id": 10000,
        "message": 'testmessage2'
    })

    assert response.status_code == InputError.code

# test_standup_send_InputError_long_message - tests that function raises InputError
# when a message is longer than 1000 chars
def test_standup_send_InputError_long_message():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    length = 1

    i = 0
    long_message = ""
    while i <= 1000:
        long_message += "a"
        i += 1
    
    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "length": length
    })    

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel1_id
    })

    assert response.json()['is_active'] == True

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "message": long_message
    })

    assert response.status_code == InputError.code

# test_standup_send_InputError_not_active - tests that function raises InputError
# when a standup is not active in the channel
def test_standup_send_InputError_not_active():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel1_id
    })

    assert response.json()['is_active'] == False

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "message": 'testmessage1'
    })

    assert response.status_code == InputError.code

    length = 1

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "length": length
    })    
    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel1_id
    })

    assert response.json()['is_active'] == True
    
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join() 

    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel1_id
    })

    assert response.json()['is_active'] == False

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "message": 'testmessage1'
    })

    assert response.status_code == InputError.code

# test_standup_send_AccessErr_non_member - tests that function returns correct
# error (AccessError) when auth user is not a member of the selected channel.
def test_standup_send_AccessErr_non_member():
    requests.delete(f"{BASE_URL}/clear/v1")

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    
    token1 = response.json()['token']
    
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail2@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy2"
    })
    
    token2 = response.json()['token']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 1',
        'is_public': True
    })

    channel1_id = response.json()['channel_id']

    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        'token': token1,
        'name': 'Channel 2',
        'is_public': False
    })

    channel2_id = response.json()['channel_id']

    length = 1

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel1_id,
        "length": length
    })    
    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel1_id
    })

    assert response.json()['is_active'] == True

    response = requests.post(f"{BASE_URL}/standup/start/v1", json = {
        "token": token1,
        "channel_id": channel2_id,
        "length": length
    })    
    response = requests.get(f"{BASE_URL}/standup/active/v1", params = {
        'token': token1,
        'channel_id': channel2_id
    })

    assert response.json()['is_active'] == True

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token2,
        "channel_id": channel1_id,
        "message": 'testmessage1'
    })

    assert response.status_code == AccessError.code

    response = requests.post(f"{BASE_URL}/standup/send/v1", json = {
        "token": token2,
        "channel_id": channel2_id,
        "message": 'testmessage2'
    })

    assert response.status_code == AccessError.code