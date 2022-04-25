'''
All functions in this file were implemented by
z5206766 Luis Reyes and
z5367441 Reuel Nkomo
UNSW comp1531 22t1
'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.config import url as BASE_URL
from src.helpers import check_valid_token, new_userstat_point, new_workspace_point, utc_now
import jwt

SECRET = 'placeholder'

def channel_invite_v1(token, channel_id, u_id):
    '''
    When passed valid auth_user_id, channel_id and u_id,
    user of u_id "u_id" is added to channel of channel_id "channel_id".

    Arguments:
        token           - string  (authorised user's token)
        channel_id      - integer (ID of the channel to which a new user is invited)
        u_id            - integer (ID of the user to be invited to a new channel)

    Exceptions:
        InputError - Occurs when:
            channel_id does not refer to a valid channel
            u_id does not refer to a valid user
            u_id refers to a user who is already a member of the channel

        AccessError - Occurs when:
            channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns {} an empty dictionary unless an InputError or an AccessError is raised
    '''

    data = data_store.get()
    users = data['users']
    channels = data['channels']
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    # channel_id does not refer to a valid channel InputError
    if channel_id not in [channel['channel_id'] for channel in channels]:
        raise InputError(description="Channel id not valid.")
    
    channel = channels[channel_id - 1]
    # channel_id is valid and the authorised user is not a member of the channel raise AccessError
    if auth_user_id not in [member['u_id'] for member in channel['all_members']]:
        raise AccessError(description="You are not even a member of the channel")

    # u_id does not refer to a valid user raise InputError
    if u_id not in [user['u_id'] for user in users]:
        raise InputError(description="User id not valid.")

    # u_id refers to a user who is already a member of the channel raise InputError
    if u_id in [member['u_id'] for member in channel['all_members']]:
        raise InputError(description="the user is already a member of the channel")

    # if everything is fine add the user of u_id "u_id" the channel of given channel_id
    user = users[u_id - 1]
    user_details_for_channels = {
        'u_id': user['u_id'],
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str'],
        'profile_img_url': user['profile_img_url']
    }
    user['channels_joined'].append(channel_id)
    channel['all_members'].append(user_details_for_channels)
    user['channels_interacted'].append(channel_id)

    user_stats = user['user_stats']
    utc_timestamp = utc_now()
    workspace_stats = data['workspace_stats']    
    userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 1, 0, 0)
    '''    
    user_stats['channels_joined'] += userstat_point['channels_joined']
    user_stats['involvment_rate'] = userstat_point['involvement_rate']
    '''
    data['users'][auth_user_id - 1]['user_stats']['channels_joined'] += userstat_point['channels_joined']
    
    #### notifying the added user.
    invited_user_profile = data['users'][u_id - 1]
    auth_user_handle = users[auth_user_id - 1]['handle_str']
    channel_name = channel['channel_name']
    invited_user_profile['notifications'].insert(0, {
            'channel_id': channel_id,
            'dm_id': -1,
            'notification_message': f"{auth_user_handle} added you to {channel_name}"
        }
    )

    data_store.set(data)

    return {}

def channel_details_v1(token, channel_id):
    '''
    Given a channel with ID channel_id that the authorised user is a member of,
    provide basic details about the channel.

    Arguments:
        token           - string  (authorised user's token)
        channel_id      - integer (ID of the channel on which the function called on)

    Exceptions:
        InputError - Occurs when:
            channel_id does not refer to a valid channel

        AccessError - Occurs when:
            channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns
        {
            name:
            is_public,
            owner_members,
            all_members,
        }
        unless an InputError or an AccessError is raised
    '''

    ## Import Current Database
    database = data_store.get()
    
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    
    if channel_id not in [channel['channel_id'] for channel in database['channels']]:
        raise InputError(description="Channel id not valid.")

    desiredchannel = database['channels'][channel_id - 1]

    ##if authorised user is not in the channel.
    if auth_user_id not in [users['u_id'] for users in desiredchannel['all_members']]:
        raise AccessError(description="You are not even in the channel.")

    details = {
        'name': desiredchannel['channel_name'],
        'is_public' : desiredchannel['is_public'],
        'owner_members': desiredchannel['owner_members'],
        'all_members': desiredchannel['all_members']
    }

    return details

def channel_messages_v1(token, channel_id, start):
    '''
    When passed a valid auth_user_id, channel_id
    and start smaller than the number of messages
    in channel of channel_id "channel_id",
    return all message from start to start + 50. If start + 50
    is greater than the number of messages
    in channel of channel_id "channel_id", return  all messages
    from start to the end of the message list.

    Arguments:
        token           - string  (authorised user's token)
        channel_id      - integer (Id of the channel containing messages to be displayed)
        start           - integer (index of the lastest message requested)

    Exceptions:
        InputError  - Occurs when:
            channel_id does not refer to a valid channel
            start is greater than the total number of messages in the channel

        AccessError - Occurs when:
            channel_id is valid and the authorised user is not a member of the channel

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
    start = 0 if start < 0 else start

    data = data_store.get()
    channels = data['channels']
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    # channel_id does not refer to a valid channel raise InputError
    if channel_id not in [channel['channel_id'] for channel in channels]:
        raise InputError(description="Channel id not valid.")
    
    # channel_id is valid and the authorised user is not a member of the channel raise AccessError
    channel = channels[channel_id - 1]
    if auth_user_id not in [member['u_id'] for member in channel['all_members']]:
        raise AccessError(description="You are not even in the channel.")

    # start is greater than the total number of messages in the channel
    if start >= len(channels[channel_id - 1]['channel_messages']) and start > 0:
        raise InputError(description="Start is greater than the total number of messages.")


    channel_messages = channels[channel_id - 1]['channel_messages']
    # CASE 1: There are more than 50 messages between start and the end of the messages list
    messages = []
    end = start
    if len(channel_messages) - start >= 50:
        for message_idx in range(start, start + 50):
            messages.append(channel_messages[message_idx])
        end = start + 50

    # CASE 2: There are less 50 messages between start and the end of the messages list
    else:
        for message_idx in range(start, len(channel_messages)):
            messages.append(channel_messages[message_idx])
        end = -1

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

def channel_join_v1(token, channel_id):
    '''
    < Adds user_id to channel_id members >

    Arguments:
        token (string)          - authorised user's token
        channel_id (integer)    - unique integer representing channel.

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel or user is already
                    a member of channel.
        AccessError - Occurs when channel_id refers to private channel and user is not a member
                    and not a global owner (u_id == 1) or permission_id == 2.

    Return Value:
        Returns: {} an empty dictionary unless an InputError or an AccessError is raised
    '''

    ## Import Current Database
    database = data_store.get()

    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    ##check InputError: Channel_id does not refer to valid channel
    #if (channel_id - 1) >= len(database['channels']) or (channel_id - 1) <= 0:
    if channel_id not in [channel['channel_id'] for channel in database['channels']]:
        raise InputError(description="Channel Id not valid")

    desiredchannel = database['channels'][channel_id - 1]
    desireduser = database['users'][auth_user_id - 1]

    ##check InputError: user already a part of channel
    if desireduser['u_id'] in [user["u_id"] for user in desiredchannel['all_members']]:
        raise InputError(description="You are already in the channel")

    ##check AccessError: private channel and user not a member and not global owner.
    if not desiredchannel['is_public'] and desireduser['permission_id'] == 2:
        raise AccessError(description="You can't join a private channel")

    ### needed to do this so that removing password won't mess up the data_store.
    desireduser_append_details = {
        'u_id': desireduser['u_id'],
        'email': desireduser['email'],
        'name_first': desireduser['name_first'],
        'name_last': desireduser['name_last'],
        'handle_str': desireduser['handle_str'],
        'profile_img_url': desireduser['profile_img_url']
    }
    desireduser['channels_joined'].append(channel_id)
    desireduser['channels_interacted'].append(channel_id)

    user_stats = desireduser['user_stats']
    utc_timestamp = utc_now()
    workspace_stats = database['workspace_stats']    
    userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 1, 0, 0)
    '''    
    user_stats['channels_joined'] += userstat_point['channels_joined']
    user_stats['involvment_rate'] = userstat_point['involvement_rate']
    '''
    database['users'][auth_user_id - 1]['user_stats']['channels_joined'] += userstat_point['channels_joined']

    database['channels'][channel_id - 1]['all_members'].append(desireduser_append_details)
    data_store.set(database)

    return {}

def channel_leave_v1(token, channel_id):
    '''
    < removes user_id from channel_id members >

    Arguments:
        token (string)          - authorised user's token
        channel_id (integer)    - unique integer representing channel.

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel.
                    - Occurs when authorised user is the starter of an active
                    standup in the channel
        AccessError - Occurs when channel_id refers to a valid channel but the
                        user is not a member of the channel.

    Return Value:
        Returns: {} an empty dictionary unless an InputError or an AccessError is raised
    '''
    ## Import Current Database
    database = data_store.get()

    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
   
    ##check InputError: Channel_id does not refer to valid channel
    #if (channel_id - 1) >= len(database['channels']) or (channel_id - 1) <= 0:
    if channel_id not in [channel['channel_id'] for channel in database['channels']]:
        raise InputError(description="Channel id not valid.")
    
    desired_channel = database['channels'][channel_id - 1]
    
    ## check InputError, user is the host of an active standup in the channel.
    if desired_channel['standup']['is_active'] == True:
        if desired_channel['standup']['host'] == auth_user_id:
            raise InputError(description="You are hosting an active standup")

    #### rely on the fact that auth_user_id is unique to see if the user is even in the channel.
    if auth_user_id not in [users['u_id'] for users in desired_channel['all_members']]:
        raise AccessError(description="You are not even in the channel.")
    
    ### needed to do this so that removing password won't mess up the data_store.
    desireduser = database['users'][auth_user_id - 1]
    desireduser_local_channel_details = {
        'u_id': desireduser['u_id'],
        'email': desireduser['email'],
        'name_first': desireduser['name_first'],
        'name_last': desireduser['name_last'],
        'handle_str': desireduser['handle_str'],
        'profile_img_url': desireduser['profile_img_url']
    }

            
    del desired_channel['all_members'][desired_channel['all_members'].index(desireduser_local_channel_details)]
    
    ### if the user is also an owner of the channel, remove that as well. ###
    if auth_user_id in [user['u_id'] for user in desired_channel['owner_members']]:
        del desired_channel['owner_members'][desired_channel['owner_members'].index(desireduser_local_channel_details)]

    user_stats = desireduser['user_stats']
    utc_timestamp = utc_now()
    workspace_stats = database['workspace_stats']    
    userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, -1, 0, 0)
    '''    
    user_stats['channels_joined'] += userstat_point['channels_joined']
    user_stats['involvment_rate'] = userstat_point['involvement_rate']
    '''
    database['users'][auth_user_id - 1]['user_stats']['channels_joined'] += userstat_point['channels_joined']

    desireduser['channels_joined'].remove(channel_id)

    data_store.set(database)
    
    return {}

def channel_add_owner_v1(token, channel_id, user_id):
    '''
    < adds user_id to channel_id owner members >

    Arguments:
        token (string)          - authorised user's token
        channel_id (integer)    - unique integer representing channel.
        user_id (integer)       - unique integer representing user to 
                                    be promoted.

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel.
        InputError  - Occurs when user_id does not refer to a valid user.
        InputError  - Occurs when user_id does not refer to a member of channel.
        InputError  - Occurs when user_id is already a channel owner.
        AccessError - Occurs when channel_id refers to a valid channel but the
                        user does not have owner permissions.

    Return Value:
        Returns: {} an empty dictionary unless an InputError or an AccessError
                is raised
    '''

    ## Import Current Database
    database = data_store.get()

    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    ##check InputError: Channel_id does not refer to valid channel
    if channel_id not in [channel['channel_id'] for channel in database['channels']]:
        raise InputError(description="Channel Id not valid")

    desiredchannel = database['channels'][channel_id - 1]

    ##See if the authorising user is even in the channel.
    if auth_user_id not in [users['u_id'] for users in desiredchannel['all_members']]:
        raise AccessError(description="You are not even in the channel")

    authuserdetails = database['users'][auth_user_id - 1]
    ##check AccessError: auth_user_id is not an owner and not global owner.
    if auth_user_id not in [users['u_id'] for users in desiredchannel['owner_members']] and authuserdetails['permission_id'] != 1:
        raise AccessError(description="You do not have permissions to add owners to this channel")

    ##check InputError: user_id is not a current member
    if user_id not in [users['u_id'] for users in desiredchannel['all_members']]:
        raise InputError(description="User is not a current member")

    desireduser = database['users'][user_id - 1]

    ##check InputError: user_id is already an owner
    if user_id in [users['u_id'] for users in desiredchannel['owner_members']]:
        raise InputError(description="User is not a current owner member")

    ### needed to do this so that removing password won't mess up the data_store.
    desireduser_local_channel_details = {
        'u_id': desireduser['u_id'],
        'email': desireduser['email'],
        'name_first': desireduser['name_first'],
        'name_last': desireduser['name_last'],
        'handle_str': desireduser['handle_str'],
        'profile_img_url': desireduser['profile_img_url']
    }

    database['channels'][channel_id - 1]['owner_members'].append(desireduser_local_channel_details)

    data_store.set(database)

    return {}

def channel_remove_owner_v1(token, channel_id, user_id):
    '''
    < removes user_id from channel_id owner members >

    Arguments:
        token (string)          - authorised user's token
        channel_id (integer)    - unique integer representing channel.
        user_id (integer)       - unique integer representing user to 
                                    be removed.

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel.
        InputError  - Occurs when user_id does not refer to a valid user.
        InputError  - Occurs when user_id does not refer to a member of channel.
        InputError  - Occurs when user_id is already a channel owner.
        AccessError - Occurs when channel_id refers to a valid channel but the
                        user does not have owner permissions.

    Return Value:
        Returns: {} an empty dictionary unless an InputError or an AccessError
                is raised
    '''

    ## Import Current Database
    database = data_store.get()

    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    ##check InputError: Channel_id does not refer to valid channel
    if channel_id not in [channel['channel_id'] for channel in database['channels']]:
        raise InputError(description="Channel Id not valid")

    desiredchannel = database['channels'][channel_id - 1]

    ## check if authorised user is in the channel ###
    if auth_user_id not in [users['u_id'] for users in desiredchannel['all_members']]:
        raise AccessError(description="You are not even in the channel")

    authuserdetails = database['users'][auth_user_id - 1]
    ##check AccessError: auth_user_id is not an owner and not global owner.
    if auth_user_id not in [users['u_id'] for users in desiredchannel['owner_members']] and authuserdetails['permission_id'] != 1:
        raise AccessError(description="You do not have permissions to remove owners in this channel")

    ##check InputError: user_id does not refer to valid user
    if user_id not in [users['u_id'] for users in database['users']]:
        raise InputError(description="User Id not valid")

    desireduser = database['users'][user_id - 1]

    ##check InputError: user_id is not a current owner member
    if user_id not in [users['u_id'] for users in desiredchannel['owner_members']]:
        raise InputError(description="User is not a current owner member")

    ##check InputError: user_id is the only owner of the channel
    if (len(desiredchannel['owner_members']) <= 1):
        raise InputError(description="User is the only remaining owner")

    ### needed to do this so that removing password won't mess up the data_store.
    desireduser_local_channel_details = {
        'u_id': desireduser['u_id'],
        'email': desireduser['email'],
        'name_first': desireduser['name_first'],
        'name_last': desireduser['name_last'],
        'handle_str': desireduser['handle_str'],
        'profile_img_url': desireduser['profile_img_url']
    }


    database_removed = [users for users in desiredchannel['owner_members'] if users != desireduser_local_channel_details]
    database['channels'][channel_id - 1]['owner_members'] = database_removed

    data_store.set(database)
    return {}