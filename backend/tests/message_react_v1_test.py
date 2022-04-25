'''
This file contains tests for funtion
message_react_v1.
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import pytest
from src.message import message_send_v1, message_send_dm_v1, message_react_v1
from src.error import InputError, AccessError
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
from src.dm import dm_create_v1
from src.other import clear_v1

def test_message_react_v1_message_id_invalid():
    '''
    Test that when message_id is not a valid message within a channel or DM 
    InputError is raised
    '''
    clear_v1()
    # register a pair of users
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user_details = auth_register_v1('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')

    # create a channel
    channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)
    # create a dm
    dm_details = dm_create_v1(owner_details['token'], [user_details['auth_user_id']])

	# send a message in said channel
    message = 'Sent from test_message_react_v1_message_id_invalid'
    message_send_v1(owner_details['token'], channel_details['channel_id'], message)
    message_send_dm_v1(owner_details['token'], dm_details['dm_id'], message)
    
    # try to react to non exiting message in channel of id 1
    with pytest.raises(InputError):
        message_react_v1(user_details['token'], 1000042, 1)
    # try to react to non exiting message in dm of id 1
    with pytest.raises(InputError):
        message_react_v1(user_details['token'], -1000042, 1)

    # try to react to invalid message_id in channel of id 1
    with pytest.raises(InputError):
        message_react_v1(user_details['token'], 34, 1)
    # try to react to invalid message_id in dm of id 1
    with pytest.raises(InputError):
        message_react_v1(user_details['token'], -12, 1)

def test_message_react_v1_invalid_react_id():
    '''
    Test that when react_id is not a valid react ID InputError is raised
    '''
    clear_v1()
    # register a user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')

    # create a channel
    channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)

    # send a message in said channel
    message = 'Sent from test_message_react_v1_invalid_react_id'
    sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)

    with pytest.raises(InputError):
        message_react_v1(owner_details['token'], sent_message_details['message_id'], -42)

def test_message_react_v1_already_reacted():
    '''
    Test that when the message already contains a
    react with ID react_id from the authorised user InputError is raised
    '''
    clear_v1()
    # register a user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')

    # create a channel
    channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)

    # send a message in said channel
    message = 'Sent from test_message_react_v1_already_reacted'
    sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)

    # first react
    message_react_v1(owner_details['token'], sent_message_details['message_id'], 1)

    # second react
    with pytest.raises(InputError):
        message_react_v1(owner_details['token'], sent_message_details['message_id'], 1)

def test_message_react_v1_not_authorised_channel():
    '''
    Test that AccessError is raised when user tries to react to
    message in channel/dm they do not have not joinned
    '''
    clear_v1()
    # register 3 users
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user_details = auth_register_v1('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
    user2_details = auth_register_v1('damienlagado@gmail.com', 'damienlagadospassword123', 'Damien', 'Lagado')

    # create a channel
    channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)
    # create a dm
    dm_details = dm_create_v1(owner_details['token'], [user_details['auth_user_id']])

	# send a message in said channel
    message = 'Sent from test_message_react_v1_not_authorised_channel'
    sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)
    sent_message_dm_details = message_send_dm_v1(owner_details['token'], dm_details['dm_id'], message)
    
    with pytest.raises(AccessError):
        # auth user not in channel
        message_react_v1(user_details['token'], sent_message_details['message_id'], 1)

    with pytest.raises(AccessError):
        # auth user not in dm
        message_react_v1(user2_details['token'], sent_message_dm_details['message_id'], 1)


# test for correct behaviour
def test_message_react_v1_react_sent():
    '''
    Test that react was sent correctly
    '''
    clear_v1()
    # register a user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')

    # create a channel
    channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)

    # send a message in said channel
    message = 'Sent from test_message_react_v1_react_sent'
    sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)

    # react to the message sent
    message_react_v1(owner_details['token'], sent_message_details['message_id'], 1)
    
    most_recent_start = 0
    messages_details = channel_messages_v1(owner_details['token'],
                channel_details['channel_id'],most_recent_start)
    
    message_reacts = messages_details['messages'][0]['reacts']
    
    assert {
        'react_id': 1,
        'u_ids': [owner_details['auth_user_id']],
        'is_this_user_reacted': True,
    } == message_reacts[0]