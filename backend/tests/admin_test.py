"""'''
This file contains test function for admin.py
Written by:
z5306766 Luis Reyes
'''
import pytest
from src.channel import channel_join_v1, channel_details_v1, \
    channel_messages_v1, channel_invite_v1, channel_leave_v1, \
        channel_add_owner_v1, channel_remove_owner_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.dm import dm_create_v1, dm_details_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from tests.test_data import set_test_variables
from src.data_store import data_store
from src.config import url as BASE_URL


                                ########################################
                                ##     admin_user_remove_v1_test.py   ##
                                ########################################
### TD ###
# test repeat email once deleted
# test messages output
# test users/all
# test users/profile

# test_admin_user_remove_basic - will test that users are removed from users list, 
# channels, and DMs. 
def test_admin_user_remove_basic():
    '''
    Contains basic tests for channel_join_v1.  Tests for appropriate return type,
    ability to reuse email and handle, and removal from channels and dms list.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    assert admin_user_remove_v1(user1_id['token'], user2_id['auth_user_id']) == {}

    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    channel1_id = channels_create_v1(user1_id['token'], 'Channel 1', True)
    channel_join_v1(user2_id['token'], channel1_id['channel_id'])
    channel_add_owner_v1(user1_id['token'], channel1_id['channel_id'], user2_id['auth_user_id'])

    dm_id = dm_create_v1(user1_id['token'], [user2_id['auth_user_id']])

    admin_user_remove_v1(user1_id['token'], user2_id['auth_user_id'])
    assert channel_details_v1(user1_id['token'], channel1_id['channel_id']) == {
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
    assert dm_details_v1(user1_id['token'], dm_id['dm_id']) == {
        'name': 'testdummy1, testdummy2',
        'members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ]
    }

# test_admin_user_remove_messages - will test that message contents are overwritten 
# with 'removed user'. 
def test_admin_user_remove_message():
    '''
    Contains test for admin_user_remove_v1.  Tests for overwriting of messages
    with 'removed user'.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    # user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    # assert admin_user_remove_v1(user1_id['token'], user2_id['auth_user_id']) == {}

    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    channel1_id = channels_create_v1(user1_id['token'], 'Channel 1', True)
    channel_join_v1(user2_id['auth_user_id'], channel1_id['channel_id'])
    channel_add_owner_v1(user1_id['token'], channel1_id['channel_id'], user2_id['auth_user_id'])

    dm_id = dm_create_v1(user1_id['token'], [user2_id['auth_user_id']])

    admin_user_remove_v1(user1_id['token'], user2_id['auth_user_id'])
    assert channel_details_v1(user1_id['token'], channel1_id['channel_id']) == {
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
    assert dm_details_v1(user1_id['token'], dm_id['dm_id']) == {
        'name': 'testdummy1, testdummy2',
        'members': [
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
# test_admin_user_remove_InputError_invaliduid - will test that InputError is thrown when
# invalid user id is given.
def test_admin_user_remove_InputError_invaliduid():
    '''
    Contains test for admin_user_remove_v1.  Tests for invalid user id InputError
    thrown.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    with pytest.raises(InputError):
        assert admin_user_remove_v1(user1_id['token'], 10000)

    auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    with pytest.raises(InputError):
        assert admin_user_remove_v1(user1_id['token'], 10000)

# test_admin_user_remove_InputError_only_global_owner - will test that InputError
#  is thrown when user id given is the only remaining global owner
def test_admin_user_remove_InputError_only_global_owner():
    '''
    Contains test for admin_user_remove_v1.  Tests for u_id only global owner InputError
    thrown.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    with pytest.raises(InputError):
        assert admin_user_remove_v1(user1_id['token'], user1_id['auth_user_id'])

    auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    with pytest.raises(InputError):
        assert admin_user_remove_v1(user1_id['token'], user1_id['auth_user_id'])

# test_admin_user_remove_AccessError_not_global_owner - will test that AccessError
#  is thrown when auth_user_id is not a global owner.
def test_admin_user_remove_AccessError_not_global_owner():
    '''
    Contains test for admin_user_remove_v1.  Tests for when auth_user_id is not 
    a global owner that an AccessError is thrown.
    '''
    clear_v1()
    auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    user3_id = auth_register_v1('testemail3@hotmail.com', 'pass123', 'Test', 'Dummy2')

    with pytest.raises(AccessError):
        assert admin_user_remove_v1(user2_id['auth_user_id'], user3_id['auth_user_id'])

            ##################################################
            ##     admin_userpermission_change_v1_test.py   ##
            ##################################################
### TD ###

# test_admin_userpermission_change_basic - will test that users are promoted to
# global owner and returns correct output type
def test_admin_userpermission_change_basic():
    '''
    Contains basic tests for admin_userpermission_change_v1.  Tests for 
    appropriate return type and channel priviledges
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')['auth_user_id']
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')['auth_user_id']
    user3_id = auth_register_v1('testemail3@hotmail.com', 'pass123', 'Test', 'Dummy3')['auth_user_id']

    channel1_id = channels_create_v1(user1_id, 'Channel 1', False)['channel_id']
    channel_invite_v1(user1_id, channel1_id, user3_id)

    with pytest.raises(AccessError):
        assert channel_join_v1(user2_id, channel1_id)

    assert admin_userpermission_change_v1(user1_id, user2_id, 1) == {}

    assert channel_join_v1(user2_id, channel1_id) == {}
    
    assert channel_add_owner_v1(user2_id, channel1_id, user3_id) == {}

    assert channel_details_v1(user2_id, channel1_id) == {
        'name' : 'Channel 1',
        'is_public' : False,
        'owner_members': [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
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
        'all_members' : [
            {
                'u_id': 1,
                'email': 'testemail1@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'handle_str': 'testdummy1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }, {
                'u_id': 3,
                'email': 'testemail3@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy3',
                'handle_str': 'testdummy3',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            },  {
                'u_id': 2,
                'email': 'testemail2@hotmail.com',
                'name_first': 'Test',
                'name_last': 'Dummy2',
                'handle_str': 'testdummy2',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }

    
# test_admin_userpermission_change_InputError_uid_invalid - will test that users are promoted to
# global owner and returns correct output type
def test_admin_userpermission_change_InputError_uid_invalid():
    '''
    Contains basic tests for admin_userpermission_change_v1.  Tests for 
    appropriate return type and channel priviledges
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    with pytest.raises(InputError):
        assert admin_userpermission_change_v1(user1_id['token'], 10000, 1)

    auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    with pytest.raises(InputError):
        assert admin_userpermission_change_v1(user1_id['token'], 10000, 1)

# test_admin_userpermission_change_InputError_only_global_owner - will test that InputError
#  is thrown when user id given is the only remaining global owner and is being demoted
def test_admin_userpermission_change_InputError_only_global_owner():
    '''
    Contains test for admin_userpermission_change_v1.  Tests for u_id only global owner InputError
    thrown.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    with pytest.raises(InputError):
        assert admin_userpermission_change_v1(user1_id['token'], user1_id['auth_user_id'], 2)

    auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    with pytest.raises(InputError):
        assert admin_userpermission_change_v1(user1_id['token'], user1_id['auth_user_id'], 2)

# test_admin_userpermission_change_InputError_permission_id - will test that InputError
#  is thrown when permission id given is invalid.
def test_admin_userpermission_change_InputError_permission_id():
    '''
    Contains test for admin_userpermission_change_v1.  Tests for invalid permissionid InputError
    thrown.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    with pytest.raises(InputError):
        assert admin_userpermission_change_v1(user1_id['token'], user2_id['auth_user_id'], 10000)

# test_admin_userpermission_change_InputError_no_change - will test that InputError
#  is thrown when no change to permission id is made
def test_admin_userpermission_change_InputError_no_change():
    '''
    Contains test for admin_userpermission_change_v1.  Tests for InputError
    throw when no change is made to permission id.
    '''
    clear_v1()
    user1_id = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    with pytest.raises(InputError):
        assert admin_userpermission_change_v1(user1_id['token'], user2_id['auth_user_id'], 2)

# test_admin_userpermission_change_AccessError_auth - will test that AccessError
# is thrown when auth user is not a global owner
def test_admin_userpermission_change_AccessError_auth():
    '''
    Contains test for admin_userpermission_change_v1.  Tests for AccessError
    throw when user authorising action is not a global owner.
    '''
    clear_v1()
    auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_id = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')

    with pytest.raises(AccessError):
        assert admin_userpermission_change_v1(user2_id['auth_user_id'], user2_id['auth_user_id'], 1)"""