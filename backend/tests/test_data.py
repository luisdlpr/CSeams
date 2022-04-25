"""# This is an implementation of fixtures for any tests on iteration 1
# Written by: z5367441 Reuel Nkomo
from calendar import c
import pytest
import datetime 
import random
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1

# code obtained from https://www.askpython.com/python/examples/generate-random-strings-in-python
def generate_string():
    MIN_LIMIT = 32    # from 'a' ascii value to
    MAX_LIMIT = 126   # '~' ascii value
    
    random_string = ''
 
    for _ in range(20):
        random_integer = random.randint(MIN_LIMIT, MAX_LIMIT)
    # Keep appending random characters using chr(x)
        random_string += (chr(random_integer))
    
    return random_string


# fixture to set the variables needed for the tests
@pytest.fixture(name = 'set_test_variables')
def set_test_variables():
    '''
    Creates test data to be used in any test for iteration 1
    '''

    clear_v1()
    users = []
    channels = []
    
    channels_count = 5
    public_channels_count = 3
    private_channels_count = 2 
    user_count = 10
    public_owner_u_id = 1
    private_owner_u_id = 2

    # genera 10 valid users 
    names_first = ['Solid', 'David', 'Dora', 'Geralt', 'Bat', 'Jack', 'Nathan', 'Arthur', 'Ali', 'Riley']
    names_last = ['Snake', 'Blane', 'Explorer', 'OfRevia', 'Man', 'Sparrow', 'Drake', 'Morgan', 'G', 'Freeman']
    # u_id is expected to be i + 1
    for u_id in range(user_count):
        u_id_returned = auth_register_v1(names_first[u_id] + names_last[u_id] + '@gmail.com', '123456789password',
                                        names_first[u_id], names_last[u_id])
        users.append(
            { 
            'u_id': u_id_returned['auth_user_id'],
            'handle_str': names_first[u_id] + names_last[u_id],
            'name_first': names_first[u_id],
            'name_last': names_last[u_id],
            'email': names_first[u_id] + names_last[u_id] + '@gmail.com',
            }
        )

    # These users are now 'valid users'

    # generate 3 public channels (all owned by user 1)
    for channel_id in range(public_channels_count):
        channel_id_returned = channels_create_v1(public_owner_u_id, 'channel' + chr(channel_id + 1 + 48), False)  

        channels.append(
            {
                'channel_id': channel_id_returned['channel_id'], # channels_create_v1(1, 'channel' + chr(channel_id + 48), True),
                'name' : 'channel' + chr(channel_id + 1 + 48), # 48 is the offset to get a digit's ascii value
                'is_public': True,
                'all_members': [users[public_owner_u_id - 1]],
                'owner_members': [users[public_owner_u_id - 1]],
                'channel_messages': [],
            }
        )
    # generate 2 private channels (all ownded by user 1 and 2)
    for channel_id in range(public_channels_count, channels_count): 
        channel_id_returned = channels_create_v1(private_owner_u_id, 'channel' + chr(channel_id + 1 + 48), False)  

        channels.append(
            {
                'channel_id': channel_id_returned['channel_id'],
                'name' : 'channel' + chr(channel_id + 1 + 48),
                'is_public': False,
                'all_members': [users[private_owner_u_id - 1]],
                'owner_members': [users[private_owner_u_id - 1]],
                'channel_messages': [],
            }

        )

    # ** ASSUMPTION: channel_ids are taken from 0 to len(channels) -1
    # thus len(channels) must be an invalid channel id. (same thing applies to users)
    # auth_user_id is from the caller while i is from the invitee

    data = {
        'channels': channels,
        'channels_public': channels[0:public_channels_count],
        'channels_private': channels[public_channels_count:channels_count],
        'users': users,
        'user_count': user_count,
        'channels_count': channels_count,
        'public_channels_count': public_channels_count,
        'private_channels_count': private_channels_count,
        'public_owner_u_id': public_owner_u_id,
        'private_owner_u_id': private_owner_u_id,
    }

    # store all newly recorded data

    return data
"""