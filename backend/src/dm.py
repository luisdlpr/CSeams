'''
This python file contains the functions for making dms work.
It includes functions for creating, listing and removing dms.
Also methods for priting out dm details and leaving a dm.
coded up by Westley Lo
z5363938
'''

from src.data_store import data_store
from src.error import AccessError, InputError
from src.helpers import check_valid_token, utc_now, new_userstat_point, new_workspace_point
import jwt
SECRET = 'placeholder'
def dm_create_v1(token, u_ids):
    '''
    <   Creates a new DM with the creator and the users listed in u_id. The creator will have owner permissions.
        The dm name will be a an alphabetically-sorted, comma-and-space-separated list of user handles
        e.g: 'ahandle1, bhandle2, chandle3'
    >

    Arguments:
        token (string)          - token of the authorised user
        u_ids (list of integers)- a list containing the u_ids of the user this DM is directed to.

    Exceptions:
        InputError  - Occurs when:
            - any of the u_id in u_ids doesn't refer to a valid user.
            - any duplicate u_id in u_ids

        AccessError - Occurs when auth_user_id doesn't refer to a valid user.

    Return Value:
        Returns a python dictionary containing the DM's id of the newly created
        DM if InputError and AccessError aren't raised, looked like this:
        {
            'dm_id': (integer) 
        }
    '''
    
    store = data_store.get()
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    ### check to see if auth_user_id is even valid ###
    '''
    if auth_user_id not in [user['u_id'] for user in users_list]:
        raise AccessError(description="You are not a registered user, how did you even get here?")
    '''
    
    ### see if there are duplicate u_ids.
    desired_uids = [auth_user_id] + u_ids
    if len(set(desired_uids)) != len(desired_uids):
        raise InputError(description="There's a duplicate u_id in your sending list")

    for u_id in u_ids:
        if u_id not in [user["u_id"] for user in store["users"]]:
            raise InputError(description= "The u_id you requested does not refer to an actual user.")
        
    users, dms = store['users'], store['dms']
    
    ### get the user's details. ###
        
    user_details_list = []
    for u_id in desired_uids:
        user_details = store['users'][u_id - 1]
        user_details_for_dm = {
            'u_id': user_details['u_id'],
            'email': user_details['email'],
            'name_first': user_details['name_first'],
            'name_last': user_details['name_last'],
            'handle_str': user_details['handle_str'],
            'profile_img_url': user_details['profile_img_url']
        }
        user_details['dms_joined'].append(len(dms) + 1)
        user_details['dms_interacted'].append(len(dms) + 1)
        store['users'][u_id - 1] = user_details
        user_details_list.append(user_details_for_dm)
    
    ### make the DM name ###
    dm_name = ', '.join(sorted([users[u_id - 1]['handle_str'] for u_id in desired_uids]))    
    dms += [{
        'removed': False,
        'max_message_id': 0,
        'dm_id': len(dms) + 1,
        'dm_name': dm_name,
        'all_members': user_details_list,
        'owner_members': [user_details_list[0]],
        'dm_messages': []
    }]
    
    #### taggi
    for u_id in u_ids:
        tagged_user_profile = store['users'][u_id - 1]
        auth_user_handle = users[auth_user_id - 1]['handle_str']
        tagged_user_profile['notifications'].insert(0, {
                'channel_id': -1,
                'dm_id': len(dms),
                'notification_message': f"{auth_user_handle} added you to {dm_name}"
            }
        )

    utc_timestamp = utc_now()
    workspace_stats = store['workspace_stats']
    workspace_stat_point = new_workspace_point(store, utc_timestamp, 0, 1 ,0)
    workspace_stats['dms_exist'] += workspace_stat_point['dms_exist']
    
    for u_id in desired_uids:
        user_stats = users[u_id - 1]['user_stats']
        userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 0, 1, 0)
        store['users'][u_id - 1]['user_stats']['dms_joined'] += userstat_point['dms_joined']

    data_store.set(store)
    return {
        'dm_id': len(dms)
    }
    
def dm_list_v1(token):
    '''
    <Returns the list of DMs that the user is a member of.>

    Arguments:
        token (string)          - token of the authorised user

    Exceptions:
        AccessError - Occurs when auth_user_id doesn't refer to a valid user.

    Return Value:
        Returns a list of python dictionaries which contain the dm_id and name of every DM the user is part of.
        {
            'dms' [
                {
                    'dm_id':
                    'name':
                }, ...
            ]
        }
    '''
    store = data_store.get()
    dms = store['dms']
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    '''
    if auth_user_id not in [user['u_id'] for user in users_list]:
        raise AccessError(description="You are not a registered user, how did you even get here?")
    '''
    return {
        'dms': [
            {
                'dm_id': dm['dm_id'],
                'name': dm['dm_name'],
            } for dm in dms if auth_user_id in [member['u_id'] for member in dm['all_members']]
        ]
    }

def dm_remove_v1(token, dm_id):
    '''
    <Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.>

    Arguments:
        token (string)          - token of the authorised user.
        dm_id (integer)         - id of the DM the user wants to remove.

    Exceptions:
        InputError  - Occurs when:
            - dm_id doesn't refer to a valid DM.

        AccessError - Occurs when:
            - dm_id is valid but the auth_user_id is not the original creator of the DM.
            - dm_id is valid but the authorised user is no longer in the DM.

    Return Value:
        Returns an empty python dictionary if no errors are raised.
    '''
    store = data_store.get()
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    if dm_id not in [dm['dm_id'] for dm in store['dms'] if not dm["removed"]]:
        raise InputError(description="The dm_id you specified doesn't refer to a valid DM.")
    
    desired_dm = store['dms'][dm_id - 1]
    if auth_user_id not in [owner['u_id'] for owner in desired_dm['owner_members']]:
        raise AccessError(description="You are not the creator of this DM.")

    for member in desired_dm['all_members']:
        user_deets = store['users'][member['u_id'] - 1]
        store['users'][member['u_id'] - 1]['dms_joined'].remove(dm_id)
        store['users'][member['u_id'] - 1]['dms_interacted'].remove(dm_id)
        user_stats = user_deets['user_stats']
        utc_timestamp = utc_now()
        workspace_stats = store['workspace_stats']
        workspace_stat_point = new_workspace_point(store, utc_timestamp, 0, -1 ,-(len(desired_dm['dm_messages'])))
        workspace_stats['dms_exist'] += workspace_stat_point['dms_exist']
        workspace_stats['messages_exist'] += workspace_stat_point['messages_exist']  
        workspace_stats['utilization_rate'] = workspace_stat_point['utilization_rate'] 
        
        userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 0, -1, 0)
        user_stats['dms_joined'] += userstat_point['dms_joined']
        user_stats['involvment_rate'] = userstat_point['involvement_rate']

    desired_dm['owner_members'] = desired_dm['all_members'] = desired_dm['dm_messages'] = []
    desired_dm['removed'] = True
    
    data_store.set(store)    
    return {}

def dm_details_v1(token, dm_id):
    '''
    <Given a DM with ID dm_id that the authorised user is a member of, provide basic details about the DM.>

    Arguments:
        token (string)          - token of the authorised user.
        dm_id (integer)         - ID of the DM.

    Exceptions:
        InputError  - Occurs when:
            - dm_id doesn't refer to a valid DM.

        AccessError - Occurs when:
            - dm_id is valid but the authorised user is not a member of the DM.

    Return Value:
        Returns a python dictionary containing the name and the list of all members in the DM.
        Look like this:
        {
            'name':,
            'members': [
                {
                    'u_id':,
                    'email':,
                    'name_first':,
                    'name_last':,
                    'handle_str':
                }, ...
            ]
        }
    '''
    store = data_store.get()
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    if dm_id not in [dm['dm_id'] for dm in store['dms'] if not dm['removed']]:
        raise InputError(description="The dm_id you specified doesn't refer to a valid DM.")
    
    desired_dm = store['dms'][dm_id - 1]
    
    if auth_user_id not in [user['u_id'] for user in desired_dm['all_members']]:
        raise AccessError(description="You are not even part of the DM.")
    
    return {
        'name': desired_dm['dm_name'],
        'members': desired_dm['all_members']
    }

def dm_leave_v1(token, dm_id):
    '''
    <Given a DM ID, the user is removed as a member of this DM. 
    The creator is allowed to leave and the DM will still exist if this happens. 
    This does not update the name of the DM.>

    Arguments:
        auth_user_id (integer)  - ID of the user calling this function.
        dm_id (integer)         - ID of the DM.

    Exceptions:
        InputError  - Occurs when:
            - dm_id doesn't refer to a valid DM.

        AccessError - Occurs when:
            - dm_id is valid but the authorised user is no longer a member of the DM.

    Return Value:
        Returns an empty python dictionary if no errors are raised.
    '''
    store = data_store.get()
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    if dm_id not in [dm['dm_id'] for dm in store['dms'] if not dm['removed']]:
        raise InputError(description="The dm_id you specified doesn't refer to a valid DM.")
    
    desired_dm = store['dms'][dm_id - 1]
    
    ### removing the user from all_members ###
    if auth_user_id not in [user['u_id'] for user in desired_dm['all_members']]:
        raise AccessError(description="You are not even part of the DM.")   
    del desired_dm['all_members'][[user['u_id'] for user in desired_dm['all_members']].index(auth_user_id)]

    ### if the user is also an owner of the dm, remove that as well. ###
    if auth_user_id in [user['u_id'] for user in desired_dm['owner_members']]:
        del desired_dm['owner_members'][[user['u_id'] for user in desired_dm['owner_members']].index(auth_user_id)]
        
    auth_user = store['users'][auth_user_id - 1]
    auth_user['dms_joined'].remove(dm_id)
    
    user_stats = store['users'][auth_user_id - 1]['user_stats']
    utc_timestamp = utc_now()
    workspace_stats = store['workspace_stats']    
    userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 0, -1, 0)
    store['users'][auth_user_id - 1]['user_stats']['dms_joined'] += userstat_point['dms_joined']
    
    data_store.set(store)
    
    return {}


def dm_messages_v1(token, dm_id, start):
    '''
    When passed a valid auth_user_id, dm_id
    and start smaller than the number of messages
    in dm of dm_id "dm_id",
    return all message from start to start + 50. If start + 50
    is greater than the number of messages
    in dm of dm_id "dm_id", return  all messages
    from start to the end of the message list.

    Arguments:
        token (string)          - token of the authorised user.
        dm_id      - integer (Id of the dm containing messages to be displayed)
        start           - integer (index of the lastest message requested)

    Exceptions:
        InputError  - Occurs when:
            dm_id does not refer to a valid dm
            start is greater than the total number of messages in the dm

        AccessError - Occurs when:
            dm_id is valid and the authorised user is not a member of the dm

    Return Value:
        Returns {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_sent': 1582426789,
            }
        ],
        'start': start,
        'end': end,
    }
        unless an InputError or an AccessError is raised
    '''
    # making sure that start will always be 0 or above.
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    start = 0 if start < 0 else start

    data = data_store.get()
    dms = data['dms']

    # dm_id does not refer to a valid dm raise InputError
    if dm_id not in [dm['dm_id'] for dm in dms]:
        raise InputError(description="dm id not valid.")
    
    
    desired_dm = dms[dm_id - 1]
    # dm_id is valid and the authorised user is not a member of the dm raise AccessError
    if auth_user_id not in [member['u_id'] for member in desired_dm['all_members']]:
        raise AccessError(description="You are not even in the dm.")
    
    # start is greater than the total number of messages in the dm
    if start >= len(desired_dm['dm_messages']) and start > 0:
        raise InputError(description="Start is greater than the total number of messages.")


    dm_messages = desired_dm['dm_messages']
    # CASE 1: There are more than 50 messages between start and the end of the messages list
    messages = []
    end = start
    if len(dm_messages) - start >= 50:
        for message_idx in range(start, start + 50):
            messages.append(dm_messages[message_idx])
        end = start + 50

    # CASE 2: There are less 50 messages between start and the end of the messages list
    else:
        for message_idx in range(start, len(dm_messages)):
            messages.append(dm_messages[message_idx])
        end = - 1

    data_store.set(data)
    for msg in messages:
        for react in msg['reacts']:
            if auth_user_id in react['u_ids']:
                react['is_this_user_reacted'] = True
            else:
                react['is_this_user_reacted'] = False

    return {
        'messages': messages,
        'start': start,
        'end': end,
    }
    
