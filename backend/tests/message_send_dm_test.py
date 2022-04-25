'''
This file contains all test for message_send_dm_v1
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import jwt
import pytest
from src.config import url
from src.auth import auth_register_v1
from src.message import message_send_dm_v1, MESSAGE_MAX
from src.dm import dm_create_v1, dm_messages_v1
from src.error import AccessError, InputError
from src.other import clear_v1

SECRET = 'placeholder'
BASE_URL = url

# 1. (InputError)
def test_message_send_dm_v1_dm_id_invalid():
    '''
    Test that if dm_id does not refer to a valid dm
    InputError is raised
    '''
    clear_v1()

    # register user 
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create dm
    dm_id_invalid = {'dm_id': 17}
    # send message to dm
    with pytest.raises(InputError):
        message_send_dm_v1(owner_details['token'], dm_id_invalid['dm_id'], 'Hello, Jane Doe.')
    
# 2. (InputError)
def test_message_send_dm_v1_message_too_short():
    '''
    Test when length of message is less than 1 character
    InputError is raised
    '''
    clear_v1()
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')
    # create dm
    dm_id_valid = dm_create_v1(owner_details['token'], [user1_details['auth_user_id']])
    # send message to dm (len(message) less than 1)
    message = ''
    with pytest.raises(InputError):
        message_send_dm_v1(owner_details['token'], dm_id_valid['dm_id'], message)

# 3. (InputError)
def test_message_send_dm_v1_message_too_long():
    '''
    Test when length of message is greater than 1000 character
    InputError is raised
    '''
    clear_v1()
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')
    # create dm
    dm_id_valid = dm_create_v1(owner_details['token'], [user1_details['auth_user_id']])
    # send message to dm (len(message) grater than 1000)
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
        message_send_dm_v1(owner_details['token'], dm_id_valid['dm_id'], message)

# 4. (AccessError)
def test_message_send_dm_v1_auth_user_non_member():
    '''
    Testing that when dm_id is valid and the authorised user is not a member of the dm
    AccessError is raised
    '''
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')
    # create dm
    dm_id_valid = dm_create_v1(owner_details['token'], [user1_details['auth_user_id']])
    non_member_details = auth_register_v1('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
    # send message as non_member
    message = 'Hello there, John Doe'
    with pytest.raises(AccessError):
        message_send_dm_v1(non_member_details['token'], dm_id_valid['dm_id'], message)

# 5. (AccessError)
def test_message_send_dm_v1_auth_user_invalid():
    '''
    Testing that when dm_id is valid and the authorised user is invalid
    AccessError is raised
    '''
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')
    # create dm
    dm_id_valid = dm_create_v1(owner_details['token'], [user1_details['auth_user_id']])
    invalid_user_details = {'token': jwt.encode({'auth_user_id': -1, 'session_id': 77}, SECRET, algorithm='HS256')}
    # send message as non_member
    message = 'Hello there, John Doe'
    with pytest.raises(AccessError):
        message_send_dm_v1(invalid_user_details['token'], dm_id_valid['dm_id'], message)

def test_message_send_dm_v1_correct():
    '''
    Test that when every param is fine,
    message_send_dm_v1 returns the correct message_id
    '''
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')
    # create dm
    dm_id_valid = dm_create_v1(owner_details['token'], [user1_details['auth_user_id']])
    # send message as owner
    message1 = 'Hello, Jane Doe.'
    m_id1 = message_send_dm_v1(owner_details['token'], dm_id_valid['dm_id'], message1)
    assert m_id1['message_id'] >= dm_id_valid['dm_id'] * -MESSAGE_MAX - 1

    message2 = 'This is a follow up'    
    m_id2 = message_send_dm_v1(owner_details['token'], dm_id_valid['dm_id'], message2)
    assert m_id2['message_id'] == m_id1['message_id'] - 1

def test_message_send_dm_v1_message_in_dm():
    '''
    Test that the message send was inded added
    to the dm
    '''
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')
    # create dm
    dm_id_valid = dm_create_v1(owner_details['token'], [user1_details['auth_user_id']])
    # send message as owner
    message = 'Hello, Jane Doe.'
    m_id = message_send_dm_v1(owner_details['token'], dm_id_valid['dm_id'], message)

    messages_details = dm_messages_v1(owner_details['token'], dm_id_valid['dm_id'], 0)
    assert messages_details['messages'][0]['message_id'] == m_id['message_id']

def test_message_send_dm_v1_dm_id_non_int():
    clear_v1()
    # register user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create dm
    # send message as owner
    message = 'Hello, Jane Doe.'
    with pytest.raises(InputError):
        message_send_dm_v1(owner_details['token'], '1', message)
