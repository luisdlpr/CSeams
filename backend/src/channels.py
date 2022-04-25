'''
This python file contains the functions for creating channels and listing channels.
coded up by Westley Lo
z5363938
'''

from src.data_store import data_store
from src.error import AccessError, InputError
from src.helpers import utc_now
from src.config import url as BASE_URL
from src.helpers import check_valid_token, new_workspace_point, new_userstat_point
import jwt

SECRET = 'placeholder'

def channels_list_v1(token):
    '''
    < Given the authorised user ID, provide a list of all the channels
    (and their associated details) the authorised user is part of. >

    Arguments:
        token (string)          - authorised user's token

    Exceptions:
        AccessError - Occurs when auth_user_id is not valid

    Return Value:
        Returns a python object containing a list of all the channels and their associated details
        (channel_id and name) that the authorised user is a part of assuming no errors raised.
        So it will look like this:
        {
            'channels': [
                {
                    'channel_id':,
                    'name':
                }
            ]
        }
    '''

    store = data_store.get()
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    # auth_user_id not valid.
    '''
    if auth_user_id not in [user['u_id'] for user in users_list]:
        raise AccessError(description="You are not a registered user, how did you even get here?")
    '''

    #return all channels that the user is part of.
    return {
        'channels': [
            {
                'channel_id': channel["channel_id"],
                'name': channel["channel_name"],
            } for channel in store["channels"]
            if auth_user_id in [member['u_id'] for member in channel['all_members']]
        ]
    }


def channels_listall_v1(token):
    '''
    < Given the authorised user ID, provide a list of all the channels,
    including private channels, and their details >

    Arguments:
        token (string)          - authorised user's token

    Exceptions:
        AccessError - Occurs when auth_user_id is not valid

    Return Value:
        Returns a python dictionary containing a list of all the channels
        and their associated details (channel_id and name), assuming no errors raised.
        So it looks like this:
        {
            'channels': [
                {
                    'channel_id':,
                    'name':
                }
            ]
        }
    '''

    store = data_store.get()
    check_valid_token(token)
    '''   auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']'''
    # auth_user_id not valid.
    '''
    if auth_user_id not in [user['u_id'] for user in users_list]:
        raise AccessError(description="You are not a registered user, how did you even get here?")
    '''

    return {
        'channels' : [
            {
                'channel_id': channel["channel_id"],
                'name': channel["channel_name"]
            } for channel in store["channels"]
        ]
    }

def channels_create_v1(token, name, is_public):
    '''
    < Creates a new channel with the given name that is either a public or private channel.
    The authorised user who created it automatically joins the channel. >

    Arguments:
        token (string)      - authorised user's token
        name (string)       - name of the newly created channel
        is_public (boolean) - whether the channel is public or private.

    Exceptions:
        InputError  - Occurs when the channel name has less than 1 or more than 20 characters.

        AccessError - Occurs when auth_user_id is not valid

    Return Value:
        Returns a python dictionary containing the channel id of the newly created
        channel if InputError and AccessError aren't raised, looked like this:
        {
            'channel_id':
        }
    '''

    # channel name not between 1 to 20 characters inclusive.
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    if len(name) < 1 or len(name) > 20:
        raise InputError(description="Channel name must between 1 and 20 characters inclusive.")
    store = data_store.get()

    # extracting user info (except password).
    users, channels = store["users"], store["channels"]
    user_details = users[auth_user_id - 1]
    # creating a seperate dictionary of user-details minus the password
    user_details_for_channels = {
        'u_id': user_details['u_id'],
        'email': user_details['email'],
        'name_first': user_details['name_first'],
        'name_last': user_details['name_last'],
        'handle_str': user_details['handle_str'],
        'profile_img_url': user_details['profile_img_url']
    }
    # creating channel profile and append it to the datastore
    channels += [
        {
            'max_message_id': 0,
            'channel_id': len(channels) + 1,
            'channel_name': name,
            'is_public': bool(is_public),
            'owner_members': [user_details_for_channels],
            'all_members': [user_details_for_channels],
            'channel_messages': [],
            'standup': {
                'is_active': False,
                'time_finish': None 
            }
        }
    ]
    user_details['channels_joined'].append(len(channels))
    user_details['channels_interacted'].append(len(channels))
   
    user_stats = user_details['user_stats']
    utc_timestamp = utc_now()
    workspace_stats = store['workspace_stats']
    workspace_stat_point = new_workspace_point(store, utc_timestamp, 1, 0 ,0)
    workspace_stats['channels_exist'] += workspace_stat_point['channels_exist']
    
    userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 1, 0, 0)
    '''    
    user_stats['channels_joined'] += userstat_point['channels_joined']
    user_stats['involvment_rate'] = userstat_point['involvement_rate']
    '''
    store['users'][auth_user_id - 1]['user_stats']['channels_joined'] += userstat_point['channels_joined']
    data_store.set(store)

    ### returning the channel_id of the new channel
    return {
        'channel_id': len(channels),
    }
