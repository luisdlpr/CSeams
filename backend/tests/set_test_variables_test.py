"""# This file contains the tests for the set_test_variables fixture 
# Written by z5367441 Reuel Nkomo

import pytest
from tests.test_data import set_test_variables
from src.other import clear_v1

def test_set_test_variables_channel_ids(set_test_variables):
    '''
    This function makes sure all channel datails created in test_data.set_test_variables
    are correct.
    '''
    
    data = set_test_variables
    channels = data['channels']

    assert len(channels) == 5
    # check channel names and IDs are correct
    for channel in (channels):
        assert channel['name'] == 'channel' + chr(channel['channel_id'] + 48)
        assert channel['channel_id'] == channels.index(channel) + 1

    clear_v1()

def test_set_test_variables_channels_owners(set_test_variables):
    '''
    This function makes sure all channel owners datails created in test_data.set_test_variables
    are correct.
    '''

    data = set_test_variables
    
    # check channel owners are correct
    public_channels = data['channels'][0:3]
    for channel in public_channels:
        assert channel['is_public']                     # check channel is public
        assert len(channel['owner_members']) == 1       # check there's only one owner
        assert channel['owner_members'][0]['u_id'] == data['public_owner_u_id'] # check for correct owner

    private_channels = data['channels'][3:5]
    for channel in private_channels:
        assert not channel['is_public']                 # check channel is private
        assert len(channel['owner_members']) == 1       # check there are exactlty two owners
        assert channel['owner_members'][0]['u_id'] == data['private_owner_u_id'] # check for correct owners
    
    clear_v1()

def test_set_test_variables_channels_members(set_test_variables):
    '''
    This function makes sure all channel members datails created in test_data.set_test_variables
    are correct.
    '''


    data = set_test_variables

    public_channels = data['channels'][0:3]
    private_channels = data['channels'][3:5]

    # check all members are correctly assigned
    for channel in public_channels: 
        assert len(channel['all_members']) == 1         # check only the owner is the member
        assert channel['all_members'][0] == channel['owner_members'][0]

    for channel in private_channels: 
        assert len(channel['all_members']) == 1         # check only the owner is members
        assert channel['all_members'][0] == channel['owner_members'][0]

    clear_v1()

def test_set_test_variables_users(set_test_variables):
    '''
    This function makes sure all user datails created in test_data.set_test_variables
    are correct.
    '''

    names_first = ['Solid', 'David', 'Dora', 'Geralt', 'Bat', 'Jack', 'Nathan', 'Arthur', 'Ali', 'Riley']
    names_last = ['Snake', 'Blane', 'Explorer', 'OfRevia', 'Man', 'Sparrow', 'Drake', 'Morgan', 'G', 'Freeman']

    data = set_test_variables
    users = data['users']

    for user in users:
        assert user['u_id'] == users.index(user) + 1           # check user id = user index + 1
        assert user['name_first'] == names_first[user['u_id'] - 1] # check that both the u_id and names are correct
        assert user['name_last'] == names_last[user['u_id'] - 1]
        
        assert user['handle_str'] == user['name_first'] + user['name_last'] # check that handle_str email are 
        assert user['email'] == user['name_first'] + user['name_last'] + '@gmail.com' # correctly concatenated    
    clear_v1()
"""