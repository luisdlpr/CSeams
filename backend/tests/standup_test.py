"""'''
This file contains test function for standup_test.py
Written by:
z5206766 Luis Reyes
'''
import pytest
from src.channel import channel_join_v1, channel_details_v1, \
    channel_messages_v1, channel_invite_v1, channel_leave_v1, \
        channel_add_owner_v1, channel_remove_owner_v1
from src.auth import auth_register_v1
from src.standup import standup_start_v1, finishStandup, standup_active_v1, standup_send_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.data_store import data_store
from src.config import url as BASE_URL
import datetime
import time
import threading

# does nothing for threading delays.
def nullfunction():
    return


                    ###################################
                    ##     standup_start_v1_test     ##
                    ###################################

# test_standup_start_basic - tests that function can be used for public and private 
# channels, by any member, and that the return is correct within a tolerance.
def test_standup_start_basic():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    user3_id = auth_register_v1('testemail3@hotmail.com', 'pass123', 'Test', 'Dummy3')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    channel_join_v1(user3_id['auth_user_id'], channel1_id['channel_id'])

    channel2_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 2', False)
    channel_invite_v1(user1_id['auth_user_id'], channel2_id['channel_id'], user2_id['auth_user_id'])
    channel_invite_v1(user1_id['auth_user_id'], channel2_id['channel_id'], user3_id['auth_user_id'])

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
            }, {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 3,
                'email': 'testemail3@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy3',
                'handle_str': 'testdummy3',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

    assert channel_details_v1(user1_id['auth_user_id'], channel2_id['channel_id']) == {
        'name' : 'Channel 2',
        'is_public' : False,
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
            }, {
                'u_id': 3,
                'email': 'testemail3@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy3',
                'handle_str': 'testdummy3',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

    length = 1

    finish = standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], length)["time_finish"]

    current = time.mktime(datetime.datetime.now().timetuple())
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()
    # check within 2 second tolerance
    tolerance = 1
    assert finish <= current + length + tolerance
    assert current + length - tolerance <= finish 

    finish = standup_start_v1(user2_id['auth_user_id'], channel1_id['channel_id'], length)["time_finish"]

    current = time.mktime(datetime.datetime.now().timetuple())
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()
    # check within 2 second tolerance
    tolerance = 1
    assert finish <= current + length + tolerance
    assert current + length - tolerance <= finish 

    finish = standup_start_v1(user2_id['auth_user_id'], channel2_id['channel_id'], length)["time_finish"]

    current = time.mktime(datetime.datetime.now().timetuple())
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()

    # check within 2 second tolerance
    tolerance = 1
    assert finish <= current + length + tolerance
    assert current + length - tolerance <= finish 

# test_standup_start_InputErr_ch_id - tests that function returns correct error 
# (InputError) when channel_id refers to invalid channel.
def test_standup_start_InputErr_ch_id():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    with pytest.raises(InputError):
        assert standup_start_v1(user1_id['auth_user_id'], 10000, 4)
        assert standup_start_v1(user1_id['auth_user_id'], -10000, 4)

# test_standup_start_InputErr_neg_length - tests that function returns correct
# error (InputError) when length given is a negative integer.
def test_standup_start_InputErr_neg_length():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    with pytest.raises(InputError):
        assert standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], -100)
        assert standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], -1)

# test_standup_start_InputErr_stup_active - tests that function returns correct
# error (InputError) when standup is already active in channel.
def test_standup_start_InputErr_stup_active():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    
    standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], 1)
    
    with pytest.raises(InputError):
        assert standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], 1)

    time.sleep(1)

# test_standup_start_AccessErr_non_member - tests that function returns correct
# error (AccessError) when auth user is not a member of the selected channel.
def test_standup_start_AccessErr_non_member():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channel2_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 2', False)
    
    with pytest.raises(AccessError):
        assert standup_start_v1(user2_id['auth_user_id'], channel1_id['channel_id'], 1)
        assert standup_start_v1(user2_id['auth_user_id'], channel2_id['channel_id'], 1)

## TEST FOR WHAT MESSAGE SENDS AT THE END

## TEST FOR NO MESSAGES SENT WHEN NO ONE CONTRIBUTES TO STANDUP

                    ###################################
                    ##     standup_active_v1_test    ##
                    ###################################

# test_standup_active_basic - tests that function can be used for public and private 
# channels, by any member, and that the return is correct
def test_standup_active_basic():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])

    channel2_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 2', False)
    channel_invite_v1(user1_id['auth_user_id'], channel2_id['channel_id'], user2_id['auth_user_id'])

    response = {
        'is_active': False,
        'time_finish': None
    }

    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id']) == response
    assert standup_active_v1(user2_id['auth_user_id'], channel2_id['channel_id']) == response

    length = 1

    time_finish = standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], length)

    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id']) == {
        'is_active': True,
        'time_finish': time_finish['time_finish']
    }

    time_finish = standup_start_v1(user2_id['auth_user_id'], channel2_id['channel_id'], length)

    assert standup_active_v1(user2_id['auth_user_id'], channel2_id['channel_id']) == {
        'is_active': True,
        'time_finish': time_finish['time_finish']
    }

# test_standup_active_InputError_ch_id - tests that function raises InputError
# when an invalid channel is selected
def test_standup_active_InputError_ch_id():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channels_create_v1(user1_id['auth_user_id'], 'Channel 2', False)

    with pytest.raises(InputError):
        assert standup_active_v1(user1_id['auth_user_id'], -10000)
        assert standup_active_v1(user1_id['auth_user_id'], 10000)

# test_standup_active_AccessError_non_mem - tests that function raises AccessErr
# when auth user is not a channel member
def test_standup_active_AccessError_non_mem():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channel2_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 2', False)

    with pytest.raises(AccessError):
        assert standup_active_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
        assert standup_active_v1(user2_id['auth_user_id'], channel2_id['channel_id'])
    
                    ###################################
                    ##     standup_send_v1_test      ##
                    ###################################

# test_standup_send_basic - tests that function can be used for public and private 
# channels, by any member, and that the return is correct
def test_standup_send_basic():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])

    channel2_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 2', False)
    channel_invite_v1(user1_id['auth_user_id'], channel2_id['channel_id'], user2_id['auth_user_id'])

    length = 1
    standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], length)
    
    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['is_active'] \
        == True
    assert standup_send_v1(user1_id['auth_user_id'], channel1_id['channel_id'], 'testmessage1') \
        == {}
    assert standup_send_v1(user2_id['auth_user_id'], channel1_id['channel_id'], 'testmessage2') \
        == {}
    
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()

    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['is_active'] \
        == False
    assert channel_messages_v1(user1_id['auth_user_id'], \
        channel1_id['channel_id'], 0)['messages'][0]['message'] \
            == "testdummy1: testmessage1\ntestdummy2: testmessage2\n"

    standup_start_v1(user2_id['auth_user_id'], channel2_id['channel_id'], length)
    
    assert standup_active_v1(user1_id['auth_user_id'], channel2_id['channel_id'])['is_active'] \
        == True
    assert standup_send_v1(user1_id['auth_user_id'], channel2_id['channel_id'], 'testmessage1') \
        == {}
    assert standup_send_v1(user2_id['auth_user_id'], channel2_id['channel_id'], 'testmessage2') \
        == {}
    
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join()

    assert standup_active_v1(user1_id['auth_user_id'], channel2_id['channel_id'])['is_active'] \
        == False
    assert channel_messages_v1(user1_id['auth_user_id'], \
        channel2_id['channel_id'], 0)['messages'][0]['message'] \
            == "testdummy1: testmessage1\ntestdummy2: testmessage2\n"

# test_standup_send_InputError_ch_id - tests that function raises InputError
# when an invalid channel is selected
def test_standup_send_InputError_ch_id():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channels_create_v1(user1_id['auth_user_id'], 'Channel 2', False)

    with pytest.raises(InputError):
        assert standup_send_v1(user1_id['auth_user_id'], -10000, 'testmessage1')
        assert standup_send_v1(user1_id['auth_user_id'], 10000, 'testmessage2')

# test_standup_send_InputError_long_message - tests that function raises InputError
# when a message is longer than 1000 chars
def test_standup_send_InputError_long_message():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    length = 1

    i = 0
    long_message = ""
    while i <= 1000:
        long_message += "a"
        i += 1
    
    standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], length)
    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['is_active'] \
        == True
    with pytest.raises(InputError):
        assert standup_send_v1(user1_id['auth_user_id'], channel1_id['channel_id'], long_message)

# test_standup_send_InputError_not_active - tests that function raises InputError
# when a standup is not active in the channel
def test_standup_send_InputError_not_active():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)

    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['is_active'] \
        == False

    with pytest.raises(InputError):
        assert standup_send_v1(user1_id['auth_user_id'], channel1_id['channel_id'], 'testmessage1')

    length = 1
    standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], length)
    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['is_active'] \
        == True
    
    t = threading.Timer(length, nullfunction)
    t.start()
    t.join() 

    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['is_active'] \
        == False

    with pytest.raises(InputError):
        assert standup_send_v1(user1_id['auth_user_id'], channel1_id['channel_id'], 'testmessage2')

# test_standup_start_AccessErr_non_member - tests that function returns correct
# error (AccessError) when auth user is not a member of the selected channel.
def test_standup_send_AccessErr_non_member():
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    channel1_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 1', True)
    channel2_id = channels_create_v1(user1_id['auth_user_id'], 'Channel 2', False)
    
    standup_start_v1(user1_id['auth_user_id'], channel1_id['channel_id'], 3)
    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['is_active'] \
        == True

    standup_start_v1(user1_id['auth_user_id'], channel2_id['channel_id'], 3)
    assert standup_active_v1(user1_id['auth_user_id'], channel1_id['channel_id'])['is_active'] \
        == True

    with pytest.raises(AccessError):
        assert standup_send_v1(user2_id['auth_user_id'], channel1_id['channel_id'], 'testmessage1')
        assert standup_send_v1(user2_id['auth_user_id'], channel2_id['channel_id'], 'testmessage2')
"""