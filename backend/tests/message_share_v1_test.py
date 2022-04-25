'''
This file contains tests for funtion
message_share_v1.
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import pytest
from src.message import message_share_v1, message_send_v1, message_send_dm_v1, message_remove_v1
from src.error import InputError, AccessError
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
from src.dm import dm_create_v1
from src.other import clear_v1

def test_message_share_v1_only_negative_ids():
        '''
        Tests that InputError is raised when both channel_id and dm_id are invalid
        '''
        clear_v1()
        # register a pair of users
        owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
        # create a channel
        channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)

        # send a message in said channel
        message = 'Sent from test_message_share_v1_only_negative_ids'
        sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)

        with pytest.raises(InputError):
                message_share_v1(owner_details['token'], sent_message_details['message_id'], -1, -1)

def test_message_share_v1_no_negative_ids():
        '''
        Tests that InputError is raised when neither channel_id nor dm_id are -1
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
        message = 'Sent from test_message_share_v1_no_negative_ids'
        sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)

        with pytest.raises(InputError):
                message_share_v1(owner_details['token'], sent_message_details['message_id'],
                                channel_details['channel_id'], dm_details['dm_id'])

def test_message_share_v1_og_message_id_invalid():
        '''
        Tests that InputError is raised when og_message_id does not refer to a valid message
        within a channel/DM that the authorised user has joined
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
        message = 'Sent from test_message_share_v1_og_message_id_invalid'
        message_send_v1(owner_details['token'], channel_details['channel_id'], message)

        # og_message_id canonly be > 1000000 or < -1000000
        # anything thing in between is not allowed
        with pytest.raises(InputError):
                message_share_v1(owner_details['token'], 1, -1, dm_details['dm_id'])

def test_message_share_v1_message_too_long():
        '''
        Tests that InputError is rasised when length of message is more than 1000 characters
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
        message = 'Sent from test_message_share_v1_message_too_long'
        sent_message_details = message_send_v1(owner_details['token'], channel_details['channel_id'], message)

        optional_message = ''
        for i in range(1001):
                optional_message += str(i)

        with pytest.raises(InputError):
                message_share_v1(owner_details['token'], sent_message_details['message_id'],
                                -1, dm_details['dm_id'], message=optional_message)

def test_message_share_v1_user_not_in_channel():
        '''
        Tests that AccessError is raised when the authorised user
        has not joined the channel they are trying to share message to
        '''
        clear_v1()
        # register a pair of users
        owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
        user_details = auth_register_v1('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
        # create a channel
        channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)
        # create a dm
        dm_details = dm_create_v1(owner_details['token'], [user_details['auth_user_id']])

        # send a message in said dm
        message = 'Sent from test_message_share_v1_message_too_long'
        sent_message_details = message_send_dm_v1(owner_details['token'], dm_details['dm_id'], message)

        with pytest.raises(AccessError):
                message_share_v1(user_details['token'], sent_message_details['message_id'],
                                channel_details['channel_id'], -1)
        
def test_message_share_v1_user_not_in_dm():
        '''
        Tests that AccessError is raised when the authorised user
        has not joined the dm they are trying to share message to
        '''
        clear_v1()
        # register 3 users
        owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
        user_details = auth_register_v1('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
        user2_details = auth_register_v1('damienlagado@gmail.com', 'damienlagadospassword123', 'Damien', 'Lagado')
        # create a channel
        channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)

        # create a dm
        dm_details = dm_create_v1(user_details['token'], [user2_details['auth_user_id']])

        # send a message in said channel
        message = 'Sent from test_message_share_v1_user_not_in_dm'
        sent_message_details = message_send_dm_v1(user2_details['token'], dm_details['dm_id'], message)

        with pytest.raises(AccessError):
                message_share_v1(owner_details['token'], sent_message_details['message_id'],
                                channel_details['channel_id'], -1)

############################## EDGE CASE COVERAGE ###############################
def test_message_share_v1_deleted_og_message():
        clear_v1()

        owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
        user_details = auth_register_v1('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
        channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)
        dm_details = dm_create_v1(owner_details['token'], [user_details['auth_user_id']])

        message = 'Sent from test_message_share_v1_deleted_og_message'
        sent_message_details = message_send_dm_v1(user_details['token'], dm_details['dm_id'], message)

        optional_message = ''
        # share message
        message_share_v1(owner_details['token'], sent_message_details['message_id'],
                                channel_details['channel_id'], -1, optional_message)
        # delete og message
        message_remove_v1(owner_details['token'], sent_message_details['message_id'])
        start_latest = 0
        messages_details = channel_messages_v1(owner_details['token'], channel_details['channel_id'], start_latest)
        messages = messages_details['messages']
        
        message = message.replace("\n", "\n\t")
        assert messages[0]['message'] == f'>\n\t{message}\n<\n' + f'{optional_message}'

############################## CORRECTNESS TESTS ################################
def test_message_share_v1_message_shared_succefully():
        '''
        Test that message was shared successfully
        '''
        clear_v1()
        # register a pair of users
        owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
        user_details = auth_register_v1('janedoes@gmail.com', 'janedoespassword123', 'Jane', 'Doe')
        # create a channel
        channel_details = channels_create_v1(owner_details['token'], 'channel_valid', True)
        # create a dm
        dm_details = dm_create_v1(owner_details['token'], [user_details['auth_user_id']])

        # send a message in dm
        message = 'Sent from test_message_share_v1_message_shared_succefully'
        optional_message = 'Optional message from test_message_share_v1_message_shared_succefully'

        sent_message_details = message_send_dm_v1(user_details['token'], dm_details['dm_id'], message)
        # share our message from dm to cahnnel
        shared_message_details = message_share_v1(owner_details['token'], sent_message_details['message_id'],
                                channel_details['channel_id'], -1, optional_message)
        
        # request 50 latest messges from our newly created channel
        start_latest = 0
        messages_details = channel_messages_v1(owner_details['token'], channel_details['channel_id'], start_latest)
        messages = messages_details['messages']

        assert shared_message_details['shared_message_id'] == messages[0]['message_id']
        assert optional_message in messages[0]['message']
        assert message in messages[0]['message']

        ### check that the string was correctly formatted
        message = message.replace("\n", "\n\t")
        assert messages[0]['message'] == f'>\n\t{message}\n<\n' + f'{optional_message}'
