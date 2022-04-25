"""'''
This file contains test function for channel.py
Written by:
z5206766 Luis Reyes and,
z5367441 Reuel Nkomo
'''
import pytest
from src.channel import channel_join_v1, channel_details_v1, \
    channel_messages_v1, channel_invite_v1, channel_leave_v1, \
        channel_add_owner_v1, channel_remove_owner_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from tests.test_data import set_test_variables
from src.data_store import data_store
from src.config import url as BASE_URL


                                ###################################
                                ##     channel_join_v1_test.py   ##
                                ###################################

# test_join_basic - tests that members are placed into member list of channels
# and previous members remain the same.  Also tests other users not placed in channel mistakenly.
def test_join_basic():
    '''
    Contains basic tests for channel_join_v1.  Reliant on auth_register_v1, channels_create_v1,
    channel_join_v1, and channel_details_v1.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    member_ids = []
    for users in channel_details_v1(user1_id['auth_user_id'],
                                    channel1_id['channel_id'])['all_members']:
        member_ids.append(users['u_id'])

    assert user2_id['auth_user_id'] in [users['u_id'] for users in channel_details_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['all_members']]

# tests for inputError when channel id does not refer to a valid channel
def test_join_input_error_invalid_channel():
    '''
    Contains tests for channel_join_v1 that attempt to raise an InputError based on
    reference to an invalid channel.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    with pytest.raises(InputError):
        assert channel_join_v1(user1_id['auth_user_id'], 6)
    with pytest.raises(InputError):
        assert channel_join_v1(user2_id['auth_user_id'], 100)

# tests for inputError when user already member
def test_join_input_error_user():
    '''
    Contains tests for channel_join_v1 that attempt to raise an InputError based on
    reference to a user that is already a channel member.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    with pytest.raises(InputError):
        assert channel_join_v1(user1_id['auth_user_id'], channel1_id['channel_id'])

# tests for accesserror (user not allowed in private channel)
def test_join_access_error():
    '''
    Contains tests for channel_join_v1 that attempt to raise an AccessError based on
    reference to a private channel from an account without permissions.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', False)
    with pytest.raises(AccessError):
        assert channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])

clear_v1()

                                ###################################
                                ##   channel_details_v1_test.py  ##
                                ###################################
## channel_details_v1 tests ##
# basic functionality test, checks output is correct for valid input args.
def test_details_basic_tests():
    ''' Tests that channel_details_v1 returns the correct output. '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    assert channel_details_v1(user1_id['auth_user_id'], channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

# checks for inputerror return when channelid is invalid.
def tests_details_input_error():
    ''' Tests that channel_details_v1 raises an InputError when referencing an invalid channel '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    with pytest.raises(InputError):
        assert channel_details_v1(user1_id['auth_user_id'], 100)
        assert channel_details_v1(user1_id['auth_user_id'], 223)

# checks for accesserror when used is not a member of selected channel.
def tests_details_access_error():
    '''
    tests that channel_details_v1 raises an AccessError when auth_id is not a member of the
    selected channel
     '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    with pytest.raises(AccessError):
        assert channel_details_v1(user2_id['auth_user_id'], channel1_id['channel_id'])

clear_v1()

                                ###################################
                                ##   channel_invite_v1_test.py   ##
                                ###################################

# 1. channel_id does not refer to a valid channel InputError
def test_channel_invite_v1_invalid_channel_id(set_test_variables):
    '''
    Tests that when channel_id does not refer to a valid channel,
    channel_invite_v1 raises an InputError
    '''
    data = set_test_variables
    channels = data['channels']
    users = data['users']

    channel_id_invalid = len(channels) + 1
    u_id_valid = users[2]['u_id']
    auth_user_id_valid = users[0]['u_id']

    with pytest.raises(InputError):
        channel_invite_v1(auth_user_id_valid, channel_id_invalid, u_id_valid)

    clear_v1()

# 2. u_id does not refer to a valid user InputError
def test_channel_invite_v1_invalid_u_id(set_test_variables):
    '''
    Tests that when u_id does not refer to a valid channel,
    channel_invite_v1 raises an InputError
    '''
    data = set_test_variables
    channels = data['channels']
    users = data['users']

    channel_id_valid = channels[0]['channel_id']
    u_id_invalid = len(users) + 1
    auth_user_id_valid = channels[0]['owner_members'][0]['u_id']


    with pytest.raises(InputError):
        channel_invite_v1(auth_user_id_valid, channel_id_valid, u_id_invalid)

    clear_v1()

# 3. u_id refers to a user who is already a member of the channel InputError
def test_channel_invite_v1_existing_u_id(set_test_variables):
    '''
    Tests that when u_id refers to a user who is already a member of the channel,
    channel_invite_v1 raises an InputError
    '''
    data = set_test_variables
    channels = data['channels']
    users = data['users']

    channel_id_valid = channels[0]['channel_id']
    auth_user_id_valid = users[0]['u_id']

    # invite user 5
    u_id_existing = users[5]['u_id']
    channel_invite_v1(auth_user_id_valid, channel_id_valid, u_id_existing)

    with pytest.raises(InputError):
        channel_invite_v1(auth_user_id_valid, channel_id_valid, u_id_existing)

    clear_v1()

# 4. channel_id is valid and the authorised user is not a member of the channel AccessError
def test_channel_invite_v1_invalid_auth_user_id(set_test_variables):
    '''
    Test that when and the authorised user is not a member of the channel,
    channel_invite_v1 raises and AccessError
    '''
    data = set_test_variables
    channels = data['channels']
    users = data['users']

    channel_id_valid = channels[0]['channel_id']
    u_id_valid = users[5]['u_id']
    auth_user_id_invalid = users[2]['u_id']

    with pytest.raises(AccessError):
        channel_invite_v1(auth_user_id_invalid, channel_id_valid, u_id_valid)

    clear_v1()
#Test for correct behaviour (ensure u_id is in channel after invite is sent)
def test_channel_invite_v1_u_id_added(set_test_variables):
    '''
    Test that when a valid auth_user_id, a valid u_id, and a valid channel_id are passed
    to channel_invite_v1, the user of u_id "u_id" is added to channel of channel_id "channel_id".

    Functions used:
        src.channel.channel_details_before_v1
    '''
    data = set_test_variables
    channels = data['channels']
    users = data['users']

    # chose auth_user_id, u_id, and channel_id
    channel_id_valid = channels[0]['channel_id']

    # if the user is not in the channel then add choose them
    u_id_valid = -1
    for user in users:
        if user not in channels[channel_id_valid - 1]['all_members']:
            u_id_valid = user['u_id']

    u_id_valid = users[2]['u_id']
    auth_user_id_valid = channels[channel_id_valid - 1]['owner_members'][0]['u_id']

    # save channel details before inviting user at index 2
    channel_name_before = channels[channel_id_valid - 1]['name']
    channel_all_members_before = channels[channel_id_valid - 1]['all_members']

    # invite user at index 2 and save channel details
    channel_invite_v1(auth_user_id_valid, channel_id_valid, u_id_valid)

    # record all new channel details
    channel_details_after = channel_details_v1(auth_user_id_valid, channel_id_valid)
    channel_name_after = channel_details_after['name']
    channel_all_members_after = channel_details_after['all_members']

    new_user_index = len(channel_all_members_after) - 1

    # assert someone was added
    # assert the right person was added
    print(channel_all_members_after)
    assert len(channel_all_members_after) == len(channel_all_members_before) + 1
    assert channel_all_members_after[new_user_index]['u_id'] == users[u_id_valid - 1]['u_id']

     # assert nothing else was changed (if not the channel_details_before is faulty)
    assert channel_name_before == channel_name_after

    clear_v1()

                                    #####################################
                                    ##   channel_messages_v1_test.py   ##
                                    #####################################

# 1. channel_id does not refer to a valid channel (InputError)
def test_channel_messages_v1_invalid_channel_id(set_test_variables):
    '''
    Test that when an InputError is raised when channel_id does not
    refer to a valid channel
    '''
    data = set_test_variables

    channel_id_invalid = len(data['channels']) + 1
    auth_user_id_valid = data['users'][0]['u_id']
    start_valid = 0

    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id_valid, channel_id_invalid, start_valid)

    clear_v1()

# 2. start is greater than the total number of messages in the channel (InputError)
def test_channel_messages_v1_messages_invalid_start(set_test_variables):
    '''
    Test that when start is greater than the total emount of messages in
    the given channel, an InputError is raised.
    '''
    data = set_test_variables
                                        #channels[ id = 0][messages[...]]
    max_start = len(data['channels'][0]['channel_messages']) - 1
    if max_start < 0:
        max_start = 0

    channel_id_valid = data['channels'][0]['channel_id']
    auth_user_id_valid = data['channels'][0]['owner_members'][0]['u_id']
    start_invalid = max_start + 1
    print(max_start, start_invalid)
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id_valid, channel_id_valid, start_invalid)

    clear_v1()




######## new test #######

def test_global_owner_join_private_channel():
    clear_v1()

    user1_global = auth_register_v1("a@gmail.com", "1234567890", "John", "Doe")
    user2_member = auth_register_v1("b@gmail.com", "0987654321", "John", "Doe")

    private_channel_1 = channels_create_v1(user2_member["auth_user_id"], "channel1", False)
    #### This shouldn't throw an error, because user1 is a global owner.
    channel_join_v1(user1_global['auth_user_id'], private_channel_1['channel_id'])
    
    assert channel_details_v1(user1_global['auth_user_id'], private_channel_1['channel_id']) == {
        "name": "channel1",
        "is_public": False,
        "owner_members": [
            {
                'u_id': user2_member['auth_user_id'],
                'email': 'b@gmail.com',
                'name_first': 'John',
                'name_last': 'Doe',
                'handle_str': 'johndoe0',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            },
        ],
        "all_members": [
            {
                'u_id': user2_member['auth_user_id'],
                'email': 'b@gmail.com',
                'name_first': 'John',
                'name_last': 'Doe',
                'handle_str': 'johndoe0',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            },
            {
                'u_id': user1_global['auth_user_id'],
                'email': 'a@gmail.com',
                'name_first': 'John',
                'name_last': 'Doe',
                'handle_str': 'johndoe',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ]
    }

    private_channel_2 = channels_create_v1(user1_global["auth_user_id"], "channel2", False)

    with pytest.raises(AccessError):
        channel_join_v1(user2_member['auth_user_id'], private_channel_2['channel_id'])

    channel_invite_v1(user1_global['auth_user_id'], private_channel_2['channel_id'], user2_member['auth_user_id'])

    assert channel_details_v1(user2_member['auth_user_id'], private_channel_2['channel_id']) == {
        "name": "channel2",
        "is_public": False,
        "owner_members": [
            {
                'u_id': user1_global['auth_user_id'],
                'email': 'a@gmail.com',
                'name_first': 'John',
                'name_last': 'Doe',
                'handle_str': 'johndoe',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            },
        ],
        "all_members": [
            {
                'u_id': user1_global['auth_user_id'],
                'email': 'a@gmail.com',
                'name_first': 'John',
                'name_last': 'Doe',
                'handle_str': 'johndoe',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            },
            {
                'u_id': user2_member['auth_user_id'],
                'email': 'b@gmail.com',
                'name_first': 'John',
                'name_last': 'Doe',
                'handle_str': 'johndoe0',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ]
    }

@pytest.mark.parametrize('first1, last1, handle1, first2, last2, handle2', [
    ('abcdefghij', 'klmnopqrs', 'abcdefghijklmnopqrs', 'abcdefghij', 'klmnopqrs', 'abcdefghijklmnopqrs0'),
    ('abcdefghij', 'klmnopqrst', 'abcdefghijklmnopqrst', 'abcdefghij', 'klmnopqrst', 'abcdefghijklmnopqrst0'),
    ('@bcdefgh!j', 'klmn opqrst', 'bcdefghjklmnopqrst', 'bcdefghj', 'klmnopqrst', 'bcdefghjklmnopqrst0'),
    ('abc', 'def0', 'abcdef0', 'abc', 'def', 'abcdef1'),
])

def test_handles_generated_correctly(first1, last1, handle1, first2, last2, handle2):
    clear_v1()
    email1 = 'blah1@email.com'
    email2 = 'blah2@email.com'

    user_woody = auth_register_v1('sheriff.woody@andysroom.com', 'qazwsx!!', 'sheriff', 'woody')
    woodys_public_toybox = channels_create_v1(user_woody['auth_user_id'], 'woodys toybox', True)

    auth_register_v1('blah3@email.com', 'password1', 'abc', 'def')

    u_id1 = auth_register_v1(email1, 'password1', first1, last1)['auth_user_id']
    channel_join_v1(u_id1, woodys_public_toybox['channel_id'])

    u_id2 = auth_register_v1(email2, 'password1', first2, last2)['auth_user_id']
    channel_join_v1(u_id2, woodys_public_toybox['channel_id'])
    print(data_store.get())
    ch_deets = channel_details_v1(user_woody['auth_user_id'], woodys_public_toybox['channel_id'])
    for k in ch_deets['all_members']:
        if k['u_id'] == u_id1:
            assert k['email'] == email1
            assert k['name_first'] == first1
            assert k['name_last'] == last1
            assert k['handle_str'] == handle1
        if k['u_id'] == u_id2:
            assert k['email'] == email2
            assert k['name_first'] == first2
            assert k['name_last'] == last2
            assert k['handle_str'] == handle2

# These are now tested on a http level

# def test_invalid_parameters_1():
#     '''
#     test all sorts of invalid parameters
#     '''
#     clear_v1()
#     user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
#     channel = channels_create_v1(user['auth_user_id'], 'woodys toybox', True)
    
#     with pytest.raises(InputError):
#         channel_details_v1(user["auth_user_id"], -1)
#     # not necessary as http wrapper covers this.
#     # with pytest.raises(AccessError):
#     #     channel_details_v1(-1, channel['channel_id'])

# def test_invalid_parameters_2():
#     clear_v1()
#     user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
#     channel = channels_create_v1(user['auth_user_id'], 'woodys toybox', True)
    
#     # with pytest.raises(AccessError):
#     #     channel_details_v1(-1, channel['channel_id'])
    
# def test_invalid_parameters_3():
#     clear_v1()
#     user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
#     channel = channels_create_v1(user['auth_user_id'], 'woodys toybox', True)
#     user2 = auth_register_v1('buzz.lightyear@starcommand.com', 'qazwsx@@', 'buzz', 'lightyear')
    
#     # with pytest.raises(AccessError):
#     #     channel_invite_v1(-1, channel['channel_id'], user2['auth_user_id'])
   
# def test_invalid_parameters_4():
#     clear_v1()
#     user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")   
    
#     # with pytest.raises(InputError):
#     #     channel_join_v1(user['auth_user_id'], -1)

# def test_invalid_parameters_5():
#     clear_v1()
#     user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
#     channel = channels_create_v1(user['auth_user_id'], 'woodys toybox', True)
    
#     # with pytest.raises(AccessError):
#     #     channel_join_v1(-1, channel['channel_id'])

def test_no_messages():
    clear_v1()
    user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
    channel = channels_create_v1(user['auth_user_id'], 'woodys toybox', True)
    
    assert channel_messages_v1(user['auth_user_id'], channel['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1
    }

def test_access_error_when_user_is_non_member():
    clear_v1()
    user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
    channel = channels_create_v1(user['auth_user_id'], 'woodys toybox', True)   
    user2 = auth_register_v1('buzz.lightyear@starcommand.com', 'qazwsx@@', 'buzz', 'lightyear')
    
    with pytest.raises(AccessError):
        channel_messages_v1(user2['auth_user_id'], channel['channel_id'], 0)

def test_access_error_when_invalid_token_given():
    clear_v1()
    user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
    channel = channels_create_v1(user['auth_user_id'], 'woodys toybox', True)   
    
    with pytest.raises(AccessError):
        channel_messages_v1(-1, channel['channel_id'], 0)
    
                                ###################################
                                ##     channel_leave_v1_test.py   ##
                                ###################################

# test_leave_basic - tests that members are correctly removed from channels and
# leave other users.
def test_leave_basic():
    '''
    Contains basic tests for channel_join_v1.  Test will fail if 
    channel_leave_v1 does not remove user from database.
    Reliant on auth_register_v1, channels_create_v1,
    channel_join_v1, and channel_details_v1.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])

    assert user2_id['auth_user_id'] in [users['u_id'] for users in channel_details_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['all_members']]

    channel_leave_v1(user1_id['auth_user_id'], channel1_id['channel_id'])

    assert user1_id['auth_user_id'] not in [users['u_id'] for users in channel_details_v1(user2_id['auth_user_id'], channel1_id['channel_id'])['all_members']]

    assert user1_id['auth_user_id'] not in [users['u_id'] for users in channel_details_v1(user2_id['auth_user_id'], channel1_id['channel_id'])['owner_members']]

    assert user2_id['auth_user_id'] in [users['u_id'] for users in channel_details_v1(user2_id['auth_user_id'], channel1_id['channel_id'])['all_members']]

    channel_leave_v1(user2_id['auth_user_id'], channel1_id['channel_id'])

    with pytest.raises(AccessError):
        assert channel_details_v1(user2_id['auth_user_id'], channel1_id['channel_id'])['all_members']

# test_leave_AccessError - tests that accesserror is thrown if user is not a
# current channel member.
def test_leave_AccessError():
    '''
    Contains AccessError tests for channel_leave_v1.  Test will fail if 
    channel_leave_v1 does not throw an AccessError when user is not in valid
    selected channel.
    Reliant on auth_register_v1, channels_create_v1,
    channel_join_v1, and channel_details_v1.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
  
    with pytest.raises(AccessError):
        assert channel_leave_v1(user2_id['auth_user_id'], channel1_id['channel_id'])

def test_leave_InputError():
    '''
    Contains InputError tests for channel_leave_v1.  Test will fail if 
    channel_leave_v1 does not throw an InputError when the selected channel is
    not valid.
    Reliant on auth_register_v1, channels_create_v1,
    channel_join_v1, and channel_details_v1.
    '''
    clear_v1()

    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    with pytest.raises(InputError):
        assert channel_leave_v1(user2_id['auth_user_id'], 0)

    channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
  
    with pytest.raises(InputError):
        assert channel_leave_v1(user2_id['auth_user_id'], 600)

def test_leave_multiChannel():
    '''
    Contains multi-channel tests for channel_leave_v1.  Test will fail if 
    channel_leave_v1 does not operate correctly when multiple channels exist.
    Reliant on auth_register_v1, channels_create_v1,
    channel_join_v1, and channel_details_v1.
    '''
    clear_v1()

    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    with pytest.raises(InputError):
        assert channel_leave_v1(user2_id['auth_user_id'], 0)

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
  
    with pytest.raises(InputError):
        assert channel_leave_v1(user2_id['auth_user_id'], 600)

    channel2_id = channels_create_v1(user2_id['auth_user_id'], 'Channel 2', True)

    with pytest.raises(InputError):
        assert channel_leave_v1(user2_id['auth_user_id'], 600)

    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    channel_join_v1(user1_id['auth_user_id'], channel2_id['channel_id'])

    assert user2_id['auth_user_id'] in [users['u_id'] for users in \
        channel_details_v1(user2_id['auth_user_id'], \
            channel1_id['channel_id'])['all_members']]
    assert user2_id['auth_user_id'] in [users['u_id'] for users in \
         channel_details_v1(user2_id['auth_user_id'], \
             channel2_id['channel_id'])['all_members']]
    assert user1_id['auth_user_id'] in [users['u_id'] for users in \
        channel_details_v1(user1_id['auth_user_id'], \
            channel1_id['channel_id'])['all_members']]
    assert user1_id['auth_user_id'] in [users['u_id'] for users in \
        channel_details_v1(user1_id['auth_user_id'], \
            channel2_id['channel_id'])['all_members']]

    channel_leave_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    
    assert user2_id['auth_user_id'] not in [users['u_id'] for users in \
        channel_details_v1(user1_id['auth_user_id'], \
            channel1_id['channel_id'])['all_members']]
    assert user2_id['auth_user_id'] in [users['u_id'] for users in \
        channel_details_v1(user2_id['auth_user_id'], \
            channel2_id['channel_id'])['all_members']]
    assert user1_id['auth_user_id'] in [users['u_id'] for users in \
        channel_details_v1(user1_id['auth_user_id'], \
            channel1_id['channel_id'])['all_members']]
    assert user1_id['auth_user_id'] in [users['u_id'] for users in \
        channel_details_v1(user1_id['auth_user_id'], \
            channel2_id['channel_id'])['all_members']]

    channel_leave_v1(user2_id['auth_user_id'], channel2_id['channel_id'])
    assert user2_id['auth_user_id'] not in [users['u_id'] for users in \
        channel_details_v1(user1_id['auth_user_id'], \
            channel1_id['channel_id'])['all_members']]
    assert user2_id['auth_user_id'] not in [users['u_id'] for users in \
        channel_details_v1(user1_id['auth_user_id'], \
            channel2_id['channel_id'])['all_members']]
    assert user1_id['auth_user_id'] in [users['u_id'] for users in \
        channel_details_v1(user1_id['auth_user_id'], \
            channel1_id['channel_id'])['all_members']]
    assert user1_id['auth_user_id'] in [users['u_id'] for users in \
        channel_details_v1(user1_id['auth_user_id'], \
            channel2_id['channel_id'])['all_members']]

                    #####################################
                    ##   channel_add_owner_v1_test.py  ##
                    #####################################
## channel_add_owner_v1 tests ##
# basic functionality test, checks output is correct for valid input args.
def test_add_owner_basic_tests():
    '''
    Tests that channel_add_owner returns the correct output and updates 
    datastore.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    assert channel_details_v1(user1_id['auth_user_id'], \
                                                channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    assert channel_details_v1(user2_id['auth_user_id'], \
                                                channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    assert channel_add_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id']) == {}
    assert channel_details_v1(user2_id['auth_user_id'], \
                                                 channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
           {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

def test_add_owner_multi_user_and_channel_tests():
    '''
    Tests that channel_add_owner returns the correct output and updates 
    datastore.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')
    user3_id = auth_register_v1('testemail3@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy3')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channels_create_v1(user3_id['auth_user_id'], 'Channel 1', True)

    assert channel_details_v1(user1_id['auth_user_id'], \
                                                channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    assert channel_details_v1(user2_id['auth_user_id'], \
                                                channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    assert channel_add_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id']) == {}
    assert channel_details_v1(user2_id['auth_user_id'], \
                                                 channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
           {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

def test_add_owner_inputError_channel_id_invalid_tests():
    '''
    Tests that channel_add_owner raises inputError when channel id is invalid.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')
    with pytest.raises(InputError):
        assert channel_add_owner_v1(user1_id['auth_user_id'], 10000, user2_id['auth_user_id'])
    
    channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    with pytest.raises(InputError):
        assert channel_add_owner_v1(user1_id['auth_user_id'], 10000, user2_id['auth_user_id'])

def test_add_owner_inputError_user_id_invalid_tests():
    '''
    Tests that channel_add_owner raises inputError when user id (to be promoted) 
    is invalid.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    with pytest.raises(InputError):
        assert channel_add_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], 10000)

def test_add_owner_inputError_user_not_member_tests():
    '''
    Tests that channel_add_owner raises inputError when user id (to be promoted) 
    is not a current channel member.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    with pytest.raises(InputError):
        assert channel_add_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id'])

def test_add_owner_inputError_user_already_owner_tests():
    '''
    Tests that channel_add_owner raises inputError when user id (to be promoted) 
    is already an owner.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    
    channel_add_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id'])
    
    with pytest.raises(InputError):
        assert channel_add_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id'])

def test_add_owner_accessError_user_not_owner_tests():
    '''
    Tests that channel_add_owner raises accessError when user id (promoter) 
    does not have owner permissions in the channel.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')
    
    user3_id = auth_register_v1('testemail3@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy3')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    channel_join_v1(user3_id['auth_user_id'], channel1_id['channel_id'])
    
    with pytest.raises(AccessError):
        assert channel_add_owner_v1(user2_id['auth_user_id'], channel1_id['channel_id'], user3_id['auth_user_id'])

                    ########################################
                    ##   channel_remove_owner_v1_test.py  ##
                    ########################################
## channel_add_owner_v1 tests ##
# basic functionality test, checks output is correct for valid input args.
def test_remove_owner_basic_tests():
    '''
    Tests that channel_remove_owner returns the correct output and updates 
    datastore.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    assert channel_details_v1(user1_id['auth_user_id'], \
                                                channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    assert channel_details_v1(user2_id['auth_user_id'], \
                                                channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    assert channel_add_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id']) == {}
    assert channel_details_v1(user2_id['auth_user_id'], \
                                                 channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
           {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

    assert channel_remove_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id']) == {}
    assert channel_details_v1(user1_id['auth_user_id'], \
                                                 channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
           {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

def test_remove_owner_multi_user_and_channel_tests():
    '''
    Tests that channel_remove_owner returns the correct output and updates 
    datastore.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')
    user3_id = auth_register_v1('testemail3@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy3')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channels_create_v1(user3_id['auth_user_id'], 'Channel 1', True)

    assert channel_details_v1(user1_id['auth_user_id'], \
                                                channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    assert channel_details_v1(user2_id['auth_user_id'], \
                                                channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    assert channel_add_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id']) == {}
    assert channel_details_v1(user2_id['auth_user_id'], \
                                                 channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
           {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

    assert channel_remove_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id']) == {}
    assert channel_details_v1(user1_id['auth_user_id'], \
                                                 channel1_id['channel_id']) == {
        'name' : 'Channel 1',
        'is_public' : True,
        'owner_members': [
           {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

def test_remove_owner_inputError_channel_id_invalid_tests():
    '''
    Tests that channel_remove_owner raises inputError when channel id is invalid.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')
    with pytest.raises(InputError):
        assert channel_remove_owner_v1(user1_id['auth_user_id'], 10000, user2_id['auth_user_id'])
    
    channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    with pytest.raises(InputError):
        assert channel_remove_owner_v1(user1_id['auth_user_id'], 10000, user2_id['auth_user_id'])

def test_remove_owner_inputError_user_id_invalid_tests():
    '''
    Tests that channel_remove_owner raises inputError when user id (to be promoted) 
    is invalid.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    with pytest.raises(InputError):
        assert channel_remove_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], 10000)

def test_remove_owner_inputError_user_not_owner_tests():
    '''
    Tests that channel_remove_owner raises inputError when user id (to be promoted) 
    is not a current channel owner.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])

    with pytest.raises(InputError):
        assert channel_remove_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id'])

def test_remove_owner_inputError_user_only_owner_tests():
    '''
    Tests that channel_remove_owner raises inputError when user id (to be promoted) 
    is the only remaining channel owner.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    
    with pytest.raises(InputError):
        assert channel_remove_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user1_id['auth_user_id'])

def test_remove_owner_accessError_user_not_owner_tests():
    '''
    Tests that channel_remove_owner raises accessError when user id (promoter) 
    does not have owner permissions in the channel.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy1')
    
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy2')
    
    user3_id = auth_register_v1('testemail3@hotmail.com', 'pass123', \
                                                            'Test', 'Dummy3')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    channel_join_v1(user3_id['auth_user_id'], channel1_id['channel_id'])

    channel_add_owner_v1(user1_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id'])

    with pytest.raises(AccessError):
        assert channel_remove_owner_v1(user3_id['auth_user_id'], channel1_id['channel_id'], user2_id['auth_user_id'])
"""