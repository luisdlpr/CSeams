"""'''
This file contains tests for the funtion message_send_v1
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import pytest
import jwt
from src.config import url
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
from src.other import clear_v1
from src.error import AccessError, InputError
from src.message import message_send_v1, MESSAGE_MAX
from src.server import SECRET

BASE_URL = url

# 1. (InputError)
def test_message_send_v1_channel_id_invalid():
    '''
    Test that if channel_id does not refer to a valid channel or
    length of message is less than 1 or over 1000 characters
    InputError is raised
    '''
    clear_v1()

    # register user 
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create channel
    channel_id_invalid = {'channel_id': 17}
    # send message to channel
    with pytest.raises(InputError):
        message_send_v1(owner_details['token'], channel_id_invalid['channel_id'], 'Hello, Jane Doe.')
    
# 2. (InputError)
def test_message_send_v1_message_too_short():
    '''
    Test when length of message is less than 1 character
    InputError is raised
    '''
    clear_v1()
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create channel
    channel_id_valid = channels_create_v1(owner_details['auth_user_id'], 'channel_valid', True)
    # send message to channel (len(message) less than 1)
    message = ''
    with pytest.raises(InputError):
        message_send_v1(owner_details['token'], channel_id_valid['channel_id'], message)

# 3. (InputError)
def test_message_send_v1_message_too_long():
    '''
    Test when length of message is greater than 1000 character
    InputError is raised
    '''
    clear_v1()
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create channel
    channel_id_valid = channels_create_v1(owner_details['auth_user_id'], 'channel_valid', True)
    # send message to channel (len(message) grater than 1000)
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
    vel illum dolore eu fe
    '''
    assert len(message) > 1000
    with pytest.raises(InputError):
        message_send_v1(owner_details['token'], channel_id_valid['channel_id'], message)

# 4. (AccessError)
def test_message_send_v1_auth_user_non_member():
    '''
    Testing that when channel_id is valid and the authorised user is not a member of the channel
    AccessError is raised
    '''
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create channel
    channel_id_valid = channels_create_v1(owner_details['auth_user_id'], 'channel_valid', True)
    non_member_details = auth_register_v1('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
    # send message as non_member
    message = 'Hello there, John Doe'
    with pytest.raises(AccessError):
        message_send_v1(non_member_details['token'], channel_id_valid['channel_id'], message)

# 5. (AccessError)
def test_message_send_v1_auth_user_invalid():
    '''
    Testing that when channel_id is valid and the authorised user is invalid
    AccessError is raised
    '''
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create channel
    channel_id_valid = channels_create_v1(owner_details['auth_user_id'], 'channel_valid', True)
    invalid_user_details = {'token': jwt.encode({'auth_user_id': -1, 'session_id': 77}, SECRET, algorithm='HS256')}
    # send message as non_member
    message = 'Hello there, John Doe'
    with pytest.raises(AccessError):
        message_send_v1(invalid_user_details['token'], channel_id_valid['channel_id'], message)

def test_message_send_v1_correct():
    '''
    Test that when every param is fine,
    message_send_v1 returns the correct message_id
    '''
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create channel
    channel_id_valid = channels_create_v1(owner_details['auth_user_id'], 'channel_valid', True)
    # send message as owner
    message1 = 'Hello, Jane Doe.'
    m_id1 = message_send_v1(owner_details['token'], channel_id_valid['channel_id'], message1)
    assert m_id1['message_id'] >= channel_id_valid['channel_id'] * MESSAGE_MAX

    message2 = 'This is a follow up'    
    m_id2 = message_send_v1(owner_details['token'], channel_id_valid['channel_id'], message2)
    assert m_id2['message_id'] == m_id1['message_id'] + 1

def test_message_send_v1_message_in_channel():
    '''
    Test that the message send was inded added
    to the channel
    '''
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create channel
    channel_id_valid = channels_create_v1(owner_details['auth_user_id'], 'channel_valid', True)
    # send message as owner
    message = 'Hello, Jane Doe.'
    m_id = message_send_v1(owner_details['token'], channel_id_valid['channel_id'], message)

    messages_details = channel_messages_v1(owner_details['auth_user_id'], channel_id_valid['channel_id'], 0)
    assert messages_details['messages'][0]['message_id'] == m_id['message_id']

def test_message_send_v1_channel_id_non_int():
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create channel
    channels_create_v1(owner_details['auth_user_id'], 'channel_valid', True)
    # send message as owner
    message = 'Hello, Jane Doe.'
    with pytest.raises(InputError):
        message_send_v1(owner_details['token'], '1', message)
"""