'''
HTTP_search_test.py
4/4/22
Amy Pham z5359018 - W11B CAMEL
Tests to ensure correct output and errors are
given by search/v1
'''
import pytest
import requests
from src import config
import src.server
import jwt
from src.error import AccessError, InputError

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"

########## HELPER FUNCTIONS ################
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
        {
        'messages': []
        'start':
        'end':
        }
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
        {'message_id'}
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
        {
        'messages': []
        'start':
        'end':
        }
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

############################################

def test_search_invalid_query_over_1000():
    '''
    tests for InputError for search/v1 
    if query_string passed is over 1000 chars
    '''
    requests.delete(f'{BASE_URL}/clear/v1')

    # registers 1 user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert response.status_code == 200
    token = response.json()['token']

    long_query = '''qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
    qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
    qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
    qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
    qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
    qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
    qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
    qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
    qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
    qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq'''

    response1 = requests.get(f"{BASE_URL}/search/v1", params={
            'token': token,
            'query_str': long_query
    })
    assert response1.status_code == 400

def test_search_invalid_query_empty():
    '''
    tests for InputError for search/v1 
    if query_string passed is empty
    '''
    requests.delete(f'{BASE_URL}/clear/v1')

    # registers 1 user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert response.status_code == 200
    token = response.json()['token']

    response1 = requests.get(f"{BASE_URL}/search/v1", params={
            'token': token,
            'query_str': ''
    })
    assert response1.status_code == 400

def test_search_invalid_token():
    '''
    tests for InputError for search/v1 
    if query_string passed is empty
    '''
    requests.delete(f'{BASE_URL}/clear/v1')

    # registers 1 user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"
    })
    assert response.status_code == 200

    # use invalid token in search
    invalid_token = jwt.encode({"auth_user_id": 1, "session_id": 1}, 'fake', algorithm='HS256')
    response1 = requests.get(f"{BASE_URL}/search/v1", params={
            'token': invalid_token,
            'query_str': 'hello'
    })
    assert response1.status_code == 403

def test_search_correct_channel_messages():
    '''
    tests for correct output when search/v1 
    is used on messages in a channel 
    and there is a match
    '''
    requests.delete(f'{BASE_URL}/clear/v1')

    # registers 1 user
    owner_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"
    })
    assert owner_details.status_code == 200
    owner = owner_details.json()

    # create a new channel
    channel1_details = channels_create_request(owner['token'], "new_channel", True)
    assert channel1_details.status_code == 200
    channel1 = channel1_details.json()

    # sends some messages on new_channel
    message1 = send_message_request(owner['token'], channel1['channel_id'], "Yes, Hello")
    assert message1.status_code == 200
    message2 = send_message_request(owner['token'], channel1['channel_id'], "This is testing,")
    assert message2.status_code == 200
    message3 = send_message_request(owner['token'], channel1['channel_id'], "search on channels!")
    assert message3.status_code == 200

    # view all messages in new_channel
    channel_messages_details = channel_messages_request(owner['token'],
        channel1['channel_id'], 0)
    assert channel_messages_details.status_code == 200
    channel_messages = channel_messages_details.json()
    # searches for  "hello"
    print(owner['token'])
    search_details = requests.get(f"{BASE_URL}/search/v1", params={
            'token': owner['token'],
            'query_str': 'hello'
    })
    assert search_details.status_code == 200
    search = search_details.json()
    # should be the same as 1st message in channel_messages
    assert search['messages'] == [channel_messages['messages'][2]]

def test_search_correct_dm_messages():
    '''
    tests for correct output when search/v1 
    is used on messages in a dm
    and there is a match
    '''
    requests.delete(f'{BASE_URL}/clear/v1')

    # registers 1 user
    owner_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"
    })
    assert owner_details.status_code == 200
    owner = owner_details.json()

    # registers another user
    user_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid1@email.com",
    "password": "password1",
    "name_first": "first1",
    "name_last": "last1"
    })
    assert user_details.status_code == 200
    user = user_details.json()

    # creates a dm with owner and user
    dm_details = dm_create_request(owner['token'], [user['auth_user_id']])
    assert dm_details.status_code == 200
    dm = dm_details.json()

    # sends some dm messages
    message= message_send_dm_request(owner['token'], dm['dm_id'], "This is testing")
    assert message.status_code == 200
    message1= message_send_dm_request(owner['token'], dm['dm_id'], "search on dms!")
    assert message1.status_code == 200
    message2= message_send_dm_request(owner['token'], dm['dm_id'], "Hello again.")
    assert message2.status_code == 200

    dm_messages_details = dm_messages_request(owner['token'], dm['dm_id'], 0)
    assert dm_messages_details.status_code == 200
    dm_messages = dm_messages_details.json()
    
    # search for "hello" in dm
    search_details = requests.get(f"{BASE_URL}/search/v1", params={
            'token': owner['token'],
            'query_str': 'hello'
    })
    assert search_details.status_code == 200
    search = search_details.json()

    # 3rd message in dm should be returned
    assert search['messages'] == [dm_messages['messages'][0]]

def test_search_correct_multiple_dm_channel_messages():
    '''
    tests for correct output when search/v1 
    is used on messages in a channel and dm
    and there is a match in both the channel and dm
    '''
    requests.delete(f'{BASE_URL}/clear/v1')
    
    # registers 1 user
    owner_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"
    })
    assert owner_details.status_code == 200
    owner = owner_details.json()

    # registers another user
    user_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid1@email.com",
    "password": "password1",
    "name_first": "first1",
    "name_last": "last1"
    })
    assert user_details.status_code == 200
    user = user_details.json()
    
    # create a new channel
    channel1_details = channels_create_request(owner['token'], "new_channel", True)
    assert channel1_details.status_code == 200
    channel1 = channel1_details.json()

    # sends some messages on new_channel
    message1 = send_message_request(owner['token'], channel1['channel_id'], "Yes, Hello")
    assert message1.status_code == 200
    message2 = send_message_request(owner['token'], channel1['channel_id'], "This is testing,")
    assert message2.status_code == 200
    message3 = send_message_request(owner['token'], channel1['channel_id'], "search on channels!")
    assert message3.status_code == 200

    # view all messages in new_channel
    channel_messages_details = channel_messages_request(owner['token'],
        channel1['channel_id'], 0)
    assert channel_messages_details.status_code == 200
    channel_messages = channel_messages_details.json()

    # creates a dm with owner and user
    dm_details = dm_create_request(owner['token'], [user['auth_user_id']])
    assert dm_details.status_code == 200
    dm = dm_details.json()

    # sends some dm messages
    dmessage= message_send_dm_request(owner['token'], dm['dm_id'], "This is testing")
    assert dmessage.status_code == 200
    dmessage1= message_send_dm_request(owner['token'], dm['dm_id'], "search on dms!")
    assert dmessage1.status_code == 200
    dmessage2= message_send_dm_request(owner['token'], dm['dm_id'], "Hello again.")
    assert dmessage2.status_code == 200

    dm_messages_details = dm_messages_request(owner['token'], dm['dm_id'], 0)
    assert dm_messages_details.status_code == 200
    dm_messages = dm_messages_details.json()
    
    # search for "hello" using owner's token
    search_details = requests.get(f"{BASE_URL}/search/v1", params={
            'token': owner['token'],
            'query_str': 'hello'
    })
    assert search_details.status_code == 200
    search = search_details.json()
    # should return 1st message in channel_messages and 3rd message in dm
    assert search['messages'] == [channel_messages['messages'][2], dm_messages['messages'][0]]

def test_search_correct_no_matches():
    '''
    tests for correct output when search/v1 
    is used on messages in a channel and dm
    and there are no matches
    '''
    requests.delete(f'{BASE_URL}/clear/v1')

    # registers 1 user
    owner_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"
    })
    assert owner_details.status_code == 200
    owner = owner_details.json()

    # registers another user
    user_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid1@email.com",
    "password": "password1",
    "name_first": "first1",
    "name_last": "last1"
    })
    assert user_details.status_code == 200
    user = user_details.json()
    
    # create a new channel
    channel1_details = channels_create_request(owner['token'], "new_channel", True)
    assert channel1_details.status_code == 200
    channel1 = channel1_details.json()

    # sends some messages on new_channel
    message1 = send_message_request(owner['token'], channel1['channel_id'], "Yes, Hello")
    assert message1.status_code == 200
    message2 = send_message_request(owner['token'], channel1['channel_id'], "This is testing,")
    assert message2.status_code == 200
    message3 = send_message_request(owner['token'], channel1['channel_id'], "search on channels!")
    assert message3.status_code == 200

    # creates a dm with owner and user
    dm_details = dm_create_request(owner['token'], [user['auth_user_id']])
    assert dm_details.status_code == 200
    dm = dm_details.json()

    # sends some dm messages
    dmessage= message_send_dm_request(owner['token'], dm['dm_id'], "This is testing")
    assert dmessage.status_code == 200
    dmessage1= message_send_dm_request(owner['token'], dm['dm_id'], "search on dms!")
    assert dmessage1.status_code == 200
    dmessage2= message_send_dm_request(owner['token'], dm['dm_id'], "Hello again.")
    assert dmessage2.status_code == 200

    # search for "no_match" using owner's token
    search_details = requests.get(f"{BASE_URL}/search/v1", params={
            'token': owner['token'],
            'query_str': 'no_match'
    })
    assert search_details.status_code == 200
    search = search_details.json()
    # should return empty list
    assert search['messages'] == []

def test_search_correct_no_messages():
    '''
    tests for correct output if search/v1 
    is used an there are no messages
    in channels or dms
    '''
    requests.delete(f'{BASE_URL}/clear/v1')

    # registers 1 user
    owner_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"
    })
    assert owner_details.status_code == 200
    owner = owner_details.json()

    # registers another user
    user_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid1@email.com",
    "password": "password1",
    "name_first": "first1",
    "name_last": "last1"
    })
    assert user_details.status_code == 200
    user = user_details.json()
    
    # create a new channel
    channel1_details = channels_create_request(owner['token'], "new_channel", True)
    assert channel1_details.status_code == 200

    # creates a dm with owner and user
    dm_details = dm_create_request(owner['token'], [user['auth_user_id']])
    assert dm_details.status_code == 200
    
    # search for "hello" using owner's token
    search_details = requests.get(f"{BASE_URL}/search/v1", params={
            'token': owner['token'],
            'query_str': 'hello'
    })
    assert search_details.status_code == 200
    search = search_details.json()
    # should return 1st message in channel_messages and 3rd message in dm
    assert search['messages'] == []

def test_search_no_matches_user_not_in_dm():
    '''
    tests for correct output when search/v1 
    is used where the query_string matches with a dm message
    but the user calling search isn't in that dm
    '''
    requests.delete(f'{BASE_URL}/clear/v1')

    # registers 1 user
    owner_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"
    })
    assert owner_details.status_code == 200
    owner = owner_details.json()

    # registers another user
    user_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid1@email.com",
    "password": "password1",
    "name_first": "first1",
    "name_last": "last1"
    })
    assert user_details.status_code == 200
    user = user_details.json()

    # registers another user1
    check_user_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid2@email.com",
    "password": "password2",
    "name_first": "first2",
    "name_last": "last2"
    })
    assert check_user_details.status_code == 200
    check_user = check_user_details.json()

    # creates a dm with owner and user (check_user isn't in dm)
    dm_details = dm_create_request(owner['token'], [user['auth_user_id']])
    assert dm_details.status_code == 200
    dm = dm_details.json()

    # sends some dm messages
    dmessage= message_send_dm_request(owner['token'], dm['dm_id'], "This is testing")
    assert dmessage.status_code == 200
    dmessage1= message_send_dm_request(owner['token'], dm['dm_id'], "search on dms!")
    assert dmessage1.status_code == 200
    dmessage2= message_send_dm_request(owner['token'], dm['dm_id'], "Hello again.")
    assert dmessage2.status_code == 200
    
    # search for "hello" using check_user's token
    search_details = requests.get(f"{BASE_URL}/search/v1", params={
            'token': check_user['token'],
            'query_str': 'hello'
    })
    assert search_details.status_code == 200
    search = search_details.json()
    # should have no matches
    assert search['messages'] == []

def test_search_no_matches_user_not_in_channel():
    '''
    tests for correct output when search/v1 
    is used where the query_string matches with a dm message
    but the user calling search isn't in that private channel
    '''
    requests.delete(f'{BASE_URL}/clear/v1')

    # registers 1 user
    owner_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"
    })
    assert owner_details.status_code == 200
    owner = owner_details.json()

    # registers another user
    user_details = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid1@email.com",
    "password": "password1",
    "name_first": "first1",
    "name_last": "last1"
    })
    assert user_details.status_code == 200
    user = user_details.json()

    # create a new channel
    channel1_details = channels_create_request(owner['token'], "new_channel", True)
    assert channel1_details.status_code == 200
    channel1 = channel1_details.json()

    # sends some messages on new_channel
    message1 = send_message_request(owner['token'], channel1['channel_id'], "Yes, Hello")
    assert message1.status_code == 200
    message2 = send_message_request(owner['token'], channel1['channel_id'], "This is testing,")
    assert message2.status_code == 200
    message3 = send_message_request(owner['token'], channel1['channel_id'], "search on channels!")
    assert message3.status_code == 200

    # searches for  "hello"
    search_details = requests.get(f"{BASE_URL}/search/v1", params={
            'token': user['token'],
            'query_str': 'hello'
    })
    assert search_details.status_code == 200
    search = search_details.json()
    # should be the same as 1st message in channel_messages
    assert search['messages'] == []