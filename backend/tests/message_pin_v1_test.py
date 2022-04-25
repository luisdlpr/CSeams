'''
This file contains tests for funtion
message_pin_v1.
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import pytest
from src.message import message_pin_v1, message_send_v1, message_send_dm_v1
from src.error import InputError, AccessError
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
from src.dm import dm_create_v1
from src.other import clear_v1

def test_message_pin_v1_message_id_invalid():
    '''
    Test that when message_id is not a valid message within
    a channel or DM that the authorised user has joined
    InputError is raised.
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
    message = 'Sent from test_message_pin_v1_message_id_invalid'
    sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)
    sent_message_dm_details = message_send_dm_v1(owner_details['token'], dm_details['dm_id'], message)

    # try to pin non exiting message in channel of id 1
    with pytest.raises(InputError):
        message_pin_v1(owner_details['token'], sent_message_details['message_id'] + 1)
    # try to pin non exiting message in dm of id 1
    with pytest.raises(InputError):
        message_pin_v1(owner_details['token'], sent_message_dm_details['message_id'] - 1)

    # try to pin invalid message_id in channel of id 1
    with pytest.raises(InputError):
        message_pin_v1(owner_details['token'], 34)
    # try to pin invalid message_id in dm of id 1
    with pytest.raises(InputError):
        message_pin_v1(owner_details['token'], -12)

def test_message_pin_v1_message_already_pinned():
    ''' 
    Test that when the message of ID message_id is already pinned,
    InputError is raised
    '''
    clear_v1()
    # register a user
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')

    # create a channel
    channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)

    # send a message in said channel
    message = 'Sent from test_message_pin_v1_message_already_pinned'
    sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)

    # first pin
    message_pin_v1(owner_details['token'], sent_message_details['message_id'])

    # second pin
    with pytest.raises(InputError):
        message_pin_v1(owner_details['token'], sent_message_details['message_id'])

def test_message_pin_v1_message_auth_not_owner():
    ''' 
    Test that when authorised user is not the owner of channel/DM
    InputError is raised.
    '''
    clear_v1()
    # register a pair of users
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user_details = auth_register_v1('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
    # create a dm
    dm_details = dm_create_v1(owner_details['token'], [user_details['auth_user_id']])

    # send a message in said dm
    message = 'Sent from test_message_pin_v1_message_auth_not_owner'
    sent_message_details = message_send_dm_v1(owner_details['token'], dm_details['dm_id'], message)

    with pytest.raises(AccessError):
        message_pin_v1(user_details['token'], sent_message_details['message_id'])

# test for correct behaviour
def test_message_pin_v1_message_pinned_successfully():
    clear_v1()
    # register a pair of users
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    # create a channel
    channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)
    
    # send a message in said channel
    message = 'Sent from test_message_pin_v1_message_pinned_successfully'
    sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)

    # pin the message
    message_pin_v1(owner_details['token'], sent_message_details['message_id'])
    start_latest = 0
    messages_details = channel_messages_v1(owner_details['token'], channel_details['channel_id'], start_latest)

    pinned_message = {}
    for msg in  messages_details['messages']:
        if msg['message_id'] == sent_message_details['message_id']:
            pinned_message = msg
    
    # print(pinned_message)
    assert pinned_message['is_pinned'] == True
