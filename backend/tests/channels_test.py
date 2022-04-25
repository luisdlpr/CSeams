"""'''
All test assumes that the functions in auth.py, channel.py and other.py works.
Typed up by Westley Lo
z5363938
'''

import pytest
import jwt
from src.channels import channels_listall_v1, channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.channel import channel_invite_v1, channel_details_v1
from src.error import InputError, AccessError
from src.config import url as BASE_URL

####### channel_listall_v1() focused tests ######

def test_listall_empty_channel_list():
    '''
        If there are no channels, then the funciton should return an empty list.
    '''
    clear_v1()
    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password1', 'emily', 'luxa')

    assert channels_listall_v1(e_luxa_details["token"]) == {
        'channels' : [],
    }

    clear_v1()

def test_listall_private_and_public_channels():
    '''
        Create 2 channels, 1 public and 1 private, listall_v1 should then return a list of the
        channel details of both.
    '''
    clear_v1()
    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password1', 'emily', 'luxa')
    channel_1name = "channel1"
    channel_2name = "channel2"
    channel1_details = channels_create_v1(e_luxa_details["token"], channel_1name, True)
    channel2_details = channels_create_v1(e_luxa_details["token"], channel_2name, False)
    channel1_details["name"] = channel_1name
    channel2_details["name"] = channel_2name
    assert channels_listall_v1(e_luxa_details["token"]) == {
        'channels': [channel1_details, channel2_details]
    }

    clear_v1()

    def test_non_user_listall():
    '''
        If the auth_user_id don't match any in datastore, an AccessError should be raised.
    '''
    clear_v1()
    with pytest.raises(AccessError):
        channels_listall_v1(-1)


####### channel_list_v1() focused tests ######

def test_list_empty_channel_list():
    '''
        If the user is not in any channels,
        then channels_list_v1 should return an empty list.
    '''
    clear_v1()
    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa')

    assert channels_list_v1(e_luxa_details["token"]) == {
        'channels': []
    }

    clear_v1()


def test_list_one_and_multiple_channels():
    '''
        Create a channel, then use channels_list_v1, it should list that channel's details.
        Create another channel with the same user, then user channels_list_v1 again,
        there should now be 2 items in the list.
    '''

    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa')

    test_channel_details = channels_create_v1(e_luxa_details["token"], "test_channel", True)

    assert channels_list_v1(e_luxa_details["token"]) == {
        'channels': [
            {
                'channel_id': test_channel_details["channel_id"],
                'name': "test_channel"
            }
        ]
    }

    another_test_channel_details = channels_create_v1(
        e_luxa_details["token"], "another_test_channel", False)

    assert channels_list_v1(e_luxa_details["token"]) == {
        'channels': [
            {
                'channel_id': test_channel_details["channel_id"],
                'name': "test_channel"
            },
            {
                'channel_id': another_test_channel_details["channel_id"],
                'name': 'another_test_channel'
            }
        ]
    }
    clear_v1()


def test_list_multiple_users_in_different_channels():
    '''
        Make two users, then make two channel for the first user.
        Ensure that the second user isn't in any channel.
        Make a channel for the second user, channels_list should then list only the third channel.
        have the second user join one of the first user's channel and list it again.
    '''
    clear_v1()
    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa')
    h_smith_details = auth_register_v1('hayden.smith@unsw.edu.au', 'password', 'hayden', 'smith')

    channel1_details = channels_create_v1(e_luxa_details["token"], "channel1", True)
    channels_create_v1(e_luxa_details["token"], "channel2", False)

    # it should return an empty list because hayden isn't in any channel
    assert channels_list_v1(h_smith_details["token"]) == {
        'channels': []
    }

    # a channel is created for hayden, so there should be the details of one channel.
    channel3_details = channels_create_v1(h_smith_details["token"], "channel3", True)
    assert channels_list_v1(h_smith_details["token"]) == {
        'channels': [
            {
                'channel_id': channel3_details["channel_id"],
                'name': 'channel3',
            }
        ]
    }

    channel_invite_v1(e_luxa_details["token"], channel1_details["channel_id"],
                      h_smith_details["auth_user_id"])

    assert channels_list_v1(h_smith_details["token"]) == {
        'channels': [
            {
                'channel_id': channel1_details["channel_id"],
                'name': 'channel1',
            },
            {
                'channel_id': channel3_details["channel_id"],
                'name': 'channel3',
            }
        ]
    }

    clear_v1()

    def test_non_user_list():
    '''
        should raise AccessError if the user isn't even authorised.
    '''
    with pytest.raises(AccessError):
        channels_list_v1(-1)

######## channel_create_v1() focused tests ########

def test_make_public_channel():
    '''
    Make a public channel
    '''

    clear_v1()
    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password', 'Emily', 'Luxa')

    created_channel_name = "channel1"
    channel_details = channels_create_v1(e_luxa_details["token"], created_channel_name, True)

    # The channel creator's name must be listed in the channel's members section and owners section
    assert channel_details_v1(e_luxa_details["token"], channel_details["channel_id"]) == {
        'name': created_channel_name,
        'is_public': True,
        'owner_members': [
            {
                'u_id': e_luxa_details["auth_user_id"],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Emily',
                'name_last': 'Luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members': [
            {
                'u_id': e_luxa_details["auth_user_id"],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Emily',
                'name_last': 'Luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    clear_v1()


def test_make_private_channel():
    '''
    Make a private channel
    '''
    clear_v1()
    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password', 'Emily', 'Luxa')

    channel_name = "channel1"

    channel_details = channels_create_v1(e_luxa_details["token"], channel_name, False)

    # The channel creator's name must be listed in the channel's members section and owners section
    print (channel_details_v1(e_luxa_details["token"], channel_details["channel_id"]))
    assert channel_details_v1(e_luxa_details["token"], channel_details["channel_id"]) == {
        'name': channel_name,
        'is_public': False,
        'owner_members': [
            {
                'u_id': e_luxa_details["auth_user_id"],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Emily',
                'name_last': 'Luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
        'all_members': [
            {
                'u_id': e_luxa_details["auth_user_id"],
                'email': 'e.luxa@student.unsw.edu.au',
                'name_first': 'Emily',
                'name_last': 'Luxa',
                'handle_str': 'emilyluxa',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"  
            }
        ],
    }
    clear_v1()


def test_channel_input_error():
    '''
    Make a public channel, with empty string, should raise InputError.
    '''
    clear_v1()
    # InputError should be raised for channel names less than 1 character, or greater than 20
    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa')
    with pytest.raises(InputError):
        channels_create_v1(e_luxa_details["token"], "", True)
    clear_v1()


def test_channel_input_error_2():
    '''
    Make a public channel, with really long name, should raise InputError.
    '''

    # InputError should be raised for channel names less than 1 character, or greater than 20
    e_luxa_details = auth_register_v1('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa')
    with pytest.raises(InputError):
        channels_create_v1(e_luxa_details["token"], "dfoiausofiaufpoauifdp", True)
    clear_v1()

    def test_non_user_create():
    '''
        should raise AccessError if the user isn't even authorised.
    '''
    with pytest.raises(AccessError):
        channels_create_v1(-1, "unauthorised", True)
"""