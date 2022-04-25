'''
This file contains all implementations fo message function
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''

import jwt, re, datetime, time,threading
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import check_valid_token, new_userstat_point, new_workspace_point, utc_now

MESSAGE_MAX = 1000000
SECRET = 'placeholder'
def message_send_v1(token, channel_id, message, shared_message=""):
    '''
    Description:
        Send a message from the authorised user to the channel specified by channel_id.
        Each message should have its own unique ID, i.e. no messages should share an ID with another message,
        even if that other message is in a different channel.
        
    Arguments:
        token           - string
        channel_id      - int
        message         - string
        
    Exceptions:
        InputError when:
            - channel_id does not refer to a valid channel.
            - length of message is less than 1 or over 1000 characters.
        AccessError when:
            - channel_id is valid and the authorised user is not a member of the channel.
            
    Return Value:
        { message_id } where message_id is int
    '''
    data = data_store.get()
            
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    # channel_id does not refer to a valid channel
    if channel_id not in [channel['channel_id'] for channel in data['channels']]:
        raise InputError(description="Channel ID not valid")
    
    # channel_id is valid and the authorised user does not exist
    target_channel = data['channels'][channel_id - 1]   
    
    # channel_id is valid and the authorised user is not a member of the channel
    if auth_user_id not in [user['u_id'] for user in target_channel['all_members']]:
        raise AccessError(description="The authorised user is not a member of the channel") 

    # length of message is less than 1 or over 1000 characters
    if len(message + shared_message) < 1 or len(message) > 1000:
        raise InputError(description="message must be between 1 and 1000 characters inclusive")
    
    message_id = 0
    if len(target_channel['channel_messages']) == 0:
        message_id = channel_id * MESSAGE_MAX
    else:
        message_id = target_channel['max_message_id'] + 1
    message = shared_message + message
    target_channel['max_message_id'] = message_id
    
    ###the taggi
    list_of_handles = [member["handle_str"] for member in target_channel['all_members']]
    auth_user_handle = data['users'][auth_user_id - 1]['handle_str']
    regex = r"@[A-Za-z0-9]+"
    tagged_handles = re.findall(regex, message)
    tagged_handles = list(set([handle[1:] for handle in tagged_handles]))
    tagged_handles = [handle for handle in tagged_handles if handle in list_of_handles]
    for handle in tagged_handles:
        handle_index = list_of_handles.index(handle)
        tagged_user_u_id = target_channel['all_members'][handle_index]['u_id']
        tagged_user_profile = data['users'][tagged_user_u_id - 1]
        notif_message = message[:20] if len(message) >= 20 else message
        channel_name = target_channel['channel_name']
        tagged_user_profile['notifications'].insert(0, {
                'channel_id': channel_id,
                'dm_id': -1,
                'notification_message': f"{auth_user_handle} tagged you in {channel_name}: {notif_message}"
            }
        )
    utc_timestamp = utc_now()
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': int(utc_timestamp),
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False,
            }
        ],
        'is_pinned': False,
    }
    
    target_channel['channel_messages'].insert(0, message_dict)
    
    user_stats = data['users'][auth_user_id - 1]['user_stats']
    utc_timestamp = utc_now()
    workspace_stats = data['workspace_stats']
    workspace_stat_point = new_workspace_point(data, utc_timestamp, 0, 0 ,1)
    workspace_stats['messages_exist'] += workspace_stat_point['messages_exist']
    
    userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 0, 0, 1)
    data['users'][auth_user_id - 1]['user_stats']['messages_sent'] += userstat_point['messages_sent']
    
    data_store.set(data)
    return {
        'message_id': message_id,
    }

def message_send_dm_v1(token, dm_id, message, shared_message=""):
    '''
    Description:
        Send a message from the authorised user to the channel specified by dm_id.
        Each message should have its own unique ID, i.e. no messages should share an ID with another message,
        even if that other message is in a different channel.
        
    Arguments:
        token           - string
        channel_id      - int
        message         - string
        
    Exceptions:
        InputError when:
            - channel_id does not refer to a valid channel.
            - length of message is less than 1 or over 1000 characters.
        AccessError when:
            - channel_id is valid and the authorised user is not a member of the channel.
            
    '''
    data = data_store.get()
            
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    # dm_id does not refer to a valid dm
    if dm_id not in [dm['dm_id'] for dm in data['dms'] if not dm['removed']]:
        raise InputError(description="The dm_id you provide does not refer to a valid dm.")

    target_dm = data['dms'][dm_id - 1]
    # dm_id is valid and the authorised user is not a member of DM
    if auth_user_id not in [user['u_id'] for user in target_dm['all_members']]:
        raise AccessError(description="You are not even a member of this DM")

    # length of message is less than 1 or over 1000 characters
    if len(message + shared_message) < 1 or len(message) > 1000:
        raise InputError(description="messages must between 1 and 1000 characters inclusive.")
    
    message_id = -1*(dm_id * MESSAGE_MAX) if len(target_dm['dm_messages']) == 0 else target_dm['max_message_id'] - 1
    message = shared_message + message
    target_dm['max_message_id'] = message_id
    
    ###the taggi
    list_of_handles = [member["handle_str"] for member in target_dm['all_members']]
    auth_user_handle = data['users'][auth_user_id - 1]['handle_str']
    regex = r"@[A-Za-z0-9]+"
    tagged_handles = re.findall(regex, message)
    tagged_handles = list(set([handle[1:] for handle in tagged_handles]))
    tagged_handles = [handle for handle in tagged_handles if handle in list_of_handles]
    for handle in tagged_handles:
        handle_index = list_of_handles.index(handle)
        tagged_user_u_id = target_dm['all_members'][handle_index]['u_id']
        tagged_user_profile = data['users'][tagged_user_u_id - 1]
        notif_message = message[:20] if len(message) >= 20 else message
        dm_name = target_dm['dm_name']
        tagged_user_profile['notifications'].insert(0, {
                'channel_id': -1,
                'dm_id': dm_id,
                'notification_message': f"{auth_user_handle} tagged you in {dm_name}: {notif_message}"
            }
        )
    utc_timestamp = utc_now()
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': int(utc_timestamp),
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False,  
            }
        ],
        'is_pinned': False,
    }

    target_dm['dm_messages'] = [message_dict] + target_dm['dm_messages']
    user_stats = data['users'][auth_user_id - 1]['user_stats']
    utc_timestamp = utc_now()
    workspace_stats = data['workspace_stats']
    workspace_stat_point = new_workspace_point(data, utc_timestamp, 0, 0 ,1)
    workspace_stats['messages_exist'] += workspace_stat_point['messages_exist']
    
    userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 0, 0, 1)
    data['users'][auth_user_id - 1]['user_stats']['messages_sent'] += userstat_point['messages_sent']
    
    data_store.set(data)
    return {
        'message_id': message_id,
    }

def message_edit_v1(token, message_id, message):
    '''
    Description:
        Given a message, update its text with new text.
        If the new message is an empty string, the message is deleted.
    Arguments:
        - token         (string)    - token of the user wanting to edit a message
        - message_id    (integer)   - Id of the message the user want to edit
        - message       (string)    - The new message
        
    Exceptions:
        InputError, occurs when:
            - length of message is over 1000 characters.
            - message_id does not refer to a valid message within a channel/DM that the authorised user is part of.
        
        AccessError, occurs when:
            - message_id refers to a valid message in a channel/DM the authorised user is part of,
              but none of the following are true:
                - The message is sent by the authorised user.
                - The authorised user has owner permissions within the channel/DM
         
    Return Value:
        Empty python dictionary if no errors are raised.
    '''
    
    store = data_store.get()
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    auth_user_details = {}
    for user in store['users']:
        auth_user_details = user if user['u_id'] == auth_user_id else auth_user_details
        
    #### message_id > 0, channel, message_id < 0, dms ####
    if abs(message_id) < MESSAGE_MAX:
        raise InputError(description="message id does not refer to a valid message")
    store_id = abs(message_id) // MESSAGE_MAX
    
    #### channel messages #######
    
    if message_id > 0:
        desiredchannel = store['channels'][store_id - 1]
        if auth_user_id not in [users['u_id'] for users in desiredchannel['all_members']]:
            raise AccessError(description="You are not even in the channel with that message")
        if message_id not in [message['message_id'] for message in desiredchannel['channel_messages']]:
            raise InputError(description="The message id you provided does not refer to a valid message in the channel")
        
        message_index = [message['message_id'] for message in desiredchannel['channel_messages']].index(message_id)
        desiredmessage = desiredchannel['channel_messages'][message_index]
        
        # R U EVEN AUTHOR #
        if desiredmessage['u_id'] != auth_user_id:
            # R U EVEN OWNER #
            if auth_user_id not in [user['u_id'] for user in desiredchannel['owner_members']]:
                # R U EVEN GLOBAL OWNER #
                if auth_user_details["permission_id"] != 1:
                    raise AccessError(description="You didn't author the message and you don't have owner permission")

        if (len(message) > 1000):
            raise InputError(description="The message can't be longer than 1000 characters")    


        list_of_handles = [member["handle_str"] for member in desiredchannel['all_members']]
        auth_user_handle = store['users'][auth_user_id - 1]['handle_str']
        regex = r"@[A-Za-z0-9]+"
        tagged_handles = re.findall(regex, message)
        tagged_handles = list(set([handle[1:] for handle in tagged_handles]))
        tagged_handles = [handle for handle in tagged_handles if handle in list_of_handles]
        for handle in tagged_handles:
            handle_index = list_of_handles.index(handle)
            tagged_user_u_id = desiredchannel['all_members'][handle_index]['u_id']
            tagged_user_profile = store['users'][tagged_user_u_id - 1]
            notif_message = message[:20] if len(message) >= 20 else message
            channel_name = desiredchannel['channel_name']
            tagged_user_profile['notifications'].insert(0, {
                    'channel_id': store_id,
                    'dm_id': -1,
                    'notification_message': f"{auth_user_handle} tagged you in {channel_name}: {notif_message}"
                }
            )

        desiredmessage["message"] = message
        if message == "":
            del desiredchannel['channel_messages'][desiredchannel['channel_messages'].index(desiredmessage)]
            utc_timestamp = utc_now()
            workspace_stats = store['workspace_stats']
            workspace_stat_point = new_workspace_point(store, utc_timestamp, 0, 0 ,-1)
            workspace_stats['messages_exist'] += workspace_stat_point['messages_exist']
    else:
        #### dm messages #######
        desireddm = store['dms'][abs(store_id) - 1]
        if auth_user_id not in [users['u_id'] for users in desireddm['all_members']]:
            raise AccessError(description="You are not even in the DM with that message")
        if message_id not in [message['message_id'] for message in desireddm['dm_messages']]:
            raise InputError(description="The message id you provided does not refer to a valid message in the DM")
        
        ### redability fixes ###
        message_index = [message['message_id'] for message in desireddm['dm_messages']].index(message_id)
        desiredmessage = desireddm['dm_messages'][message_index]
        
        ### R U EVEN AUTHOR ###
        if desiredmessage['u_id'] != auth_user_id:
            ### R U EVEN OWNER ###
            if auth_user_id not in [user['u_id'] for user in desireddm['owner_members']]:
                raise AccessError(description="You didn't author the message and you aren't the creator of the DM")

        if (len(message) > 1000):
            raise InputError(description="The message can't be longer than 1000 characters")    

        list_of_handles_uid = [member["handle_str"] for member in desireddm['all_members']]
        auth_user_handle = store['users'][auth_user_id - 1]['handle_str']
        regex = r"@[A-Za-z0-9]+"
        tagged_handles = re.findall(regex, message)
        tagged_handles = list(set([handle[1:] for handle in tagged_handles]))
        tagged_handles = [handle for handle in tagged_handles if handle in [user['handle_str'] for user in store['users'] if not user['removed']]]
        for handle in tagged_handles:
            handle_index = list_of_handles_uid.index(handle)
            tagged_user_u_id = desireddm['all_members'][handle_index]['u_id']
            tagged_user_profile = store['users'][tagged_user_u_id - 1]
            notif_message = message[:20] if len(message) >= 20 else message
            dm_name = desireddm['dm_name']
            tagged_user_profile['notifications'].insert(0, {
                    'channel_id': -1,
                    'dm_id': store_id,
                    'notification_message': f"{auth_user_handle} tagged you in {dm_name}: {notif_message}"
                }
            )

        desiredmessage["message"] = message
        if message == "":
            del desireddm['dm_messages'][desireddm['dm_messages'].index(desiredmessage)]
            utc_timestamp = utc_now()
            workspace_stats = store['workspace_stats']
            workspace_stat_point = new_workspace_point(store, utc_timestamp, 0, 0 ,-1)
            workspace_stats['messages_exist'] += workspace_stat_point['messages_exist']

    data_store.set(store)
    return {}


def message_remove_v1(token, message_id):
    '''
    Description:
        Given a message_id for a message, this message is removed from the channel/DM
        
    Arguments:
        - token         (string)    - token of the user wanting to edit a message
        - message_id    (integer)   - ID of the message the user want to delete
        
    Exceptions:
        InputError, occurs when:
            - length of message is over 1000 characters.
            - message_id does not refer to a valid message within a channel/DM that the authorised user has joined.
        
        AccessError, occurs when:
            - message_id refers to a valid message in a channel/DM the authorised user is part of,
              but none of the following are true:
                - The message is sent by the authorised user.
                - The authorised user has owner permissions within the channel/DM
         
    Return Value:
        Empty python dictionary if no errors are raised.
    '''   
    
    
    ######## we will just straight up remove the message from the list of messages in the channel/DM ########
    
    store = data_store.get()
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    auth_user_details = store['users'][auth_user_id - 1]
    #### message_id > 0, channel, message_id < 0, dms ####
    if abs(message_id) < MESSAGE_MAX:
        raise InputError(description="message id does not refer to a valid message")
    store_id = abs(message_id) // MESSAGE_MAX
    
    #### channel messages #######
    
    if message_id > 0:
        desiredchannel = store['channels'][store_id - 1]
        if auth_user_id not in [users['u_id'] for users in desiredchannel['all_members']]:
            raise AccessError(description="You are not even in the channel with that message")
        if message_id not in [message['message_id'] for message in desiredchannel['channel_messages']]:
            raise InputError(description="The message id you provided does not refer to a valid message in the channel")
        
        #### readability fixes ####
        message_index = [message['message_id'] for message in desiredchannel['channel_messages']].index(message_id)
        desiredmessage = desiredchannel['channel_messages'][message_index]
        
        ### R U EVEN AUTHOR ####
        if desiredmessage['u_id'] != auth_user_id: 
            ### R U EVEN OWNER ####
            if auth_user_id not in [users['u_id'] for users in desiredchannel['owner_members']]:
                #### R U EVEN GLOBAL OWNER ####
                if auth_user_details["permission_id"] != 1:
                    raise AccessError(description="You didn't author the message and you don't have owner permission")

        del desiredchannel['channel_messages'][desiredchannel['channel_messages'].index(desiredmessage)]
    else:
        #### dm messages #######
        desireddm = store['dms'][abs(store_id) - 1]
        if auth_user_id not in [users['u_id'] for users in desireddm['all_members']]:
            raise AccessError(description="You are not even in the DM with that message")
        if message_id not in [message['message_id'] for message in desireddm['dm_messages']]:
            raise InputError(description="The message id you provided does not refer to a valid message in the DM")
        
        #### readability fixes ####
        message_index = [message['message_id'] for message in desireddm['dm_messages']].index(message_id)
        desiredmessage = desireddm['dm_messages'][message_index]
        
        ### R U EVEN AUTHOR ####
        if (desiredmessage['u_id'] != auth_user_id):
            ### R U EVEN OWNER ####
            if auth_user_id not in [users['u_id'] for users in desireddm['owner_members']]:
                raise AccessError(description="You didn't author the message and you aren't the creator of the DM")
        
        del desireddm['dm_messages'][desireddm['dm_messages'].index(desiredmessage)]

    utc_timestamp = utc_now()
    workspace_stats = store['workspace_stats']
    workspace_stat_point = new_workspace_point(store, utc_timestamp, 0, 0 ,-1)
    workspace_stats['messages_exist'] += workspace_stat_point['messages_exist']
    data_store.set(store)
    return {}

##################### ITERATION 3 #################
def message_share_v1(token, og_message_id, channel_id, dm_id, message=None):
    '''
        InputError when any of:
      
        both channel_id and dm_id are invalid
        neither channel_id nor dm_id are -1
        
        og_message_id does not refer to a valid message within a channel/DM
        that the authorised user has joined
        length of message is more than 1000 characters
      
        AccessError when:
      
        the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid)
        and the authorised user has not joined the channel or DM they are trying to share the message to
    '''
    check_valid_token(token)
    data = data_store.get()
    channels = data['channels']
    dms = data['dms']

    auth_user_details = jwt.decode(token, SECRET, algorithms = ['HS256'])
    auth_user_id = auth_user_details['auth_user_id']
    
    channel_id_list = [channel['channel_id'] for channel in channels]
    dm_id_list = [dm['dm_id'] for dm in dms if not dm['removed']]
    
    # InputErrors
    # sharing to an invalid channel/DM
    if channel_id not in channel_id_list and dm_id not in dm_id_list:
        raise InputError(description="No valid channel or dm with this indentifier")
    
    # no -1 id given
    if channel_id != -1 and dm_id != -1:
        raise InputError(description="Are you specifying a channel or a DM?")
    
    if abs(og_message_id) < MESSAGE_MAX:
        raise InputError(description="message id does not refer to a valid message")
    origin_id = abs(og_message_id) // MESSAGE_MAX

    # message id does not refer to a valid dm/channel id
    if (origin_id > len(channels) and origin_id > len(dms)) or origin_id <= 0:
        raise InputError(description="Invalid channel or dm")
    
    # origin is a channel if we pass a channel or dm if we pass dm
    origin = channels[origin_id - 1] if og_message_id > 0 else dms[origin_id - 1]
    message_origin = 'channel' if og_message_id  > 0 else 'dm'

    # AccessErrors 
    # auth_user_id not a member of og_channel
    if auth_user_id not in [user['u_id'] for user in origin['all_members']]:
        raise AccessError(description="User is not authorised to perform this action")

    # message id does not refer to valid  message within dm/channel
    if og_message_id not in [msg['message_id'] for msg in origin[message_origin + '_messages']]:
        raise InputError(description="Message does not exist")

    # message too long
    if message and len(message) > 1000:
        raise InputError(description="Message too long")
    
    # send to a channel
    shared_message_id = 42
    og_message = [msg['message'] for msg in origin[message_origin + '_messages'] if msg['message_id'] == og_message_id][0]
    optional_message = message if message else ''
    altered_og_message = og_message.replace("\n", "\n\t")
    if dm_id == -1:
        shared_message_id = message_send_v1(token, channel_id, optional_message, f'>\n\t{altered_og_message}\n<\n')
    # send to dm
    else:
        shared_message_id = message_send_dm_v1(token, dm_id, optional_message, f'>\n\t{altered_og_message}\n<\n')

    data_store.set(data)
    return {
        'shared_message_id': shared_message_id['message_id']
    }

def message_react_v1(token, message_id, react_id):
    '''
    Description:
        Given a message within a channel or DM the authorised user
        is part of, add a "react" to that particular message.    
        
    Arguments:
        token           - string
        message_id      - int
        react_id        - int
        
    Exceptions:
        InputError when:
            - message_id is not a valid message within
              a channel or DM that the authorised user has joined.
            - react_id is not a valid react ID.
            - the message already contains a react with ID react_id from the authorised user.
        AccessError when:
            - message_id refer to a message within channel or DM
              that the authorised user has not joined.
            
    Return Value:
        {}  - empty dictionary
    '''
    check_valid_token(token)
    data = data_store.get()
    channels = data['channels']
    dms = data['dms']

    auth_user_details = jwt.decode(token, SECRET, algorithms = ['HS256'])
    auth_user_id = auth_user_details['auth_user_id']

    # InputErrors
    if message_id > -MESSAGE_MAX and message_id < MESSAGE_MAX:
        raise InputError(description="Invalid message")
    
    # get the appropriate channel/dm as origin
    origin_id = abs(message_id) // MESSAGE_MAX
    
    origin = channels[origin_id - 1] if message_id > 0 else dms[origin_id - 1]
    message_origin = 'channel' if message_id  > 0 else 'dm'

    '''
    # AccessErrors
    if auth_user_id not in [user['u_id'] for user in origin['all_members']]:
        raise AccessError(description="You are not authorise to unreact to this message")
    '''

    if react_id != 1:
        raise InputError(description="Invalid react")
    
    target_message = ''
    for message in origin[message_origin + '_messages']:
        target_message = message if message['message_id'] == message_id else target_message
    
    # valid message_id but not found
    if len(target_message) < 1:
        raise InputError(description="The message you are trying to react to does not exist")

    reacts_uids_list = []
    for react in target_message['reacts']:
        if react['react_id'] == react_id:
            reacts_uids_list = react['u_ids']

    # AccessErrors
    if auth_user_id not in [user['u_id'] for user in origin['all_members']]:
        raise AccessError(description="You are not authorise to react to this message")

    ### notifying the message author
    #### notifying the added user.
    name = origin['channel_name'] if message_origin == 'channel' else origin['dm_name']
    author_user_profile = data['users'][target_message['u_id'] - 1]
    auth_user_handle = data['users'][auth_user_id - 1]['handle_str']
    author_user_profile['notifications'].insert(0, {
            'channel_id': origin_id if message_origin == 'channel' else -1,
            'dm_id': origin_id if message_origin == 'dm' else -1,
            'notification_message': f"{auth_user_handle} reacted to your message in {name}"
        }
    )

    if auth_user_id in reacts_uids_list:
        raise InputError(description="You have already reacted to this message")
    
    # add a reaction from the authorised user
    for react in target_message['reacts']:
        if react['react_id'] == react_id:
            react['u_ids'].append(auth_user_id)

    data_store.set(data)
    return {}

def message_unreact_v1(token, message_id, react_id):
    '''
    Description:
        Given a message within a channel or DM the authorised user is part of,
        remove a "react" to that particular message.  
        
    Arguments:
        token           - string
        message_id      - int
        react_id        - int
        
    Exceptions:
        InputError when:
            - message_id is not a valid message within
              a channel or DM that the authorised user has joined.
            - react_id is not a valid react ID.
            - the message does not contain a react with ID react_id from the authorised user.
            
    Return Value:
        {}  - empty dictionary
    '''
    check_valid_token(token)
    data = data_store.get()
    channels = data['channels']
    dms = data['dms']

    auth_user_details = jwt.decode(token, SECRET, algorithms = ['HS256'])
    auth_user_id = auth_user_details['auth_user_id']
    
    # InputErrors
    if message_id > -MESSAGE_MAX and message_id < MESSAGE_MAX:
        raise InputError(description="Invalid message")
    
    # get the appropriate channel/dm as origin
    origin_id = abs(message_id) // MESSAGE_MAX
    origin = channels[origin_id - 1] if message_id > 0 else dms[origin_id - 1]
    message_origin = 'channel' if message_id  > 0 else 'dm'
    
    '''
    # AccessErrors
    if auth_user_id not in [user['u_id'] for user in origin['all_members']]:
        raise AccessError(description="You are not authorised to unreact to this message")
    '''
    
    target_message = ''
    for message in origin[message_origin + '_messages']:
        target_message = message if message['message_id'] == message_id else target_message

    if react_id != 1:
        raise InputError(description="Invalid react")

    # valid message_id but not found
    if len(target_message) < 1:
        raise InputError(description="The message you are trying to react to does not exist")

    # AccessErrors
    if auth_user_id not in [user['u_id'] for user in origin['all_members']]:
        raise AccessError(description="You are not authorised to unreact to this message")

    reacts_uids_list = []
    for react in target_message['reacts']:
        if react['react_id'] == react_id:
            reacts_uids_list = react['u_ids']

    if auth_user_id not in reacts_uids_list:
        raise InputError(description="You have not reacted to this message")
 
    # remove the reaction from the authorised user
    for react in target_message['reacts']:
        if react['react_id'] == react_id:
            react['u_ids'].remove(auth_user_id)

    data_store.set(data)
    return {}

def message_pin_v1(token, message_id):
    '''
    Description:
        Given a message within a channel or DM, mark it as "pinned".
        
    Arguments:
        token           - string
        message_id      - int
        
    Exceptions:
        InputError when:
            - message_id is not a valid message within
              a channel or DM that the authorised user has joined.
            - the message is already pinned
        AccessError when:
            - message_id refers to a valid message in a joined channel/DM
              and the authorised user does not have owner permissions in the channel/DM
            
    Return Value:
        {}  - empty dictionary
    '''
    check_valid_token(token)
    data = data_store.get()
    channels = data['channels']
    dms = data['dms']

    auth_user_details = jwt.decode(token, SECRET, algorithms = ['HS256'])
    auth_user_id = auth_user_details['auth_user_id']
    
    # InputErrors
    if message_id > -MESSAGE_MAX and message_id < MESSAGE_MAX:
        raise InputError(description="Invalid message")

    # get the appropriate channel/dm as origin
    origin_id = abs(message_id) // MESSAGE_MAX
    origin = channels[origin_id - 1] if message_id > 0 else dms[origin_id - 1]
    message_origin = 'channel' if message_id  > 0 else 'dm'

    # AccessErrors
    if message_origin == 'channel' and auth_user_id not in [usr['u_id'] for usr in origin['owner_members']]:
        ## R U EVEN GLOBAL OWNER IN CHANNEL? ##
        if auth_user_id not in [usr['u_id'] for usr in origin['all_members']] or data['users'][auth_user_id - 1]["permission_id"] != 1:
            raise AccessError(description="You do not have permission to pin messages in this channel")
    elif auth_user_id not in [usr['u_id'] for usr in origin['owner_members']]:
        # If this is a DM and you are not the owner, you don't have permission.
        raise AccessError(description="You do not have permission to pin messages in this DM")

    target_message = ''
    for message in origin[message_origin + '_messages']:
        target_message = message if message['message_id'] == message_id else target_message
    
    # valid message_id but not found
    if len(target_message) < 1:
        raise InputError(description="The message you are trying to pin does not exist")
    
    if target_message['is_pinned']:
        raise InputError(description="This message is already pinned")

    # pin the message otherwise
    target_message['is_pinned'] = True
    
    data_store.set(data)
    return {}

def message_unpin_v1(token, message_id):
    '''
    Description:
        Given a message within a channel or DM, remove its mark as pinned.
        
    Arguments:
        token           - string
        message_id      - int
        
    Exceptions:
        InputError when:
            - message_id is not a valid message within
              a channel or DM that the authorised user has joined.
            - the message is not already pinned
        AccessError when:
            - message_id refers to a valid message in a joined channel/DM
              and the authorised user does not have owner permissions in the channel/DM
            
    Return Value:
        {}  - empty dictionary
    '''
    check_valid_token(token)
    data = data_store.get()
    channels = data['channels']
    dms = data['dms']

    auth_user_details = jwt.decode(token, SECRET, algorithms = ['HS256'])
    auth_user_id = auth_user_details['auth_user_id']
    
    # InputErrors
    if message_id > -MESSAGE_MAX and message_id < MESSAGE_MAX:
        raise InputError(description="Invalid message")

    # get the appropriate channel/dm as origin
    origin_id = abs(message_id) // MESSAGE_MAX
    origin = channels[origin_id - 1] if message_id > 0 else dms[origin_id - 1]
    message_origin = 'channel' if message_id  > 0 else 'dm'

    # AccessErrors
    if message_origin == 'channel' and auth_user_id not in [usr['u_id'] for usr in origin['owner_members']]:
    
        ## R U EVEN GLOBAL OWNER IN CHANNEL? ##
        if auth_user_id not in [usr['u_id'] for usr in origin['all_members']] or data['users'][auth_user_id - 1]["permission_id"] != 1:
            raise AccessError(description="You do not have permission to pin messages in this channel")
    elif auth_user_id not in [usr['u_id'] for usr in origin['owner_members']]:
        # If this is a DM and you are not the owner, you don't have permission.
        raise AccessError(description="You do not have permission to unpin messages in this DM")
    
    target_message = ''
    for message in origin[message_origin + '_messages']:
        target_message = message if message['message_id'] == message_id else target_message
    
    # valid message_id but not found
    if len(target_message) < 1:
        raise InputError(description="The message you are trying to unpin does not exist")
    
    if not target_message['is_pinned']:
        raise InputError(description="This message has not been pinned")
    
    # unpin the message otherwise
    target_message['is_pinned'] = False

    data_store.set(data)
    return {}


def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Description:
        Send a message to the channel at a specified future time automativally.
        
    Arguments:
        - token         (string)    - token of the user wanting to edit a message
        - channel_id    (integer)   - ID of the channel to send message
        - message       (string)    - message string
        - time_sent     (integer)   - UTC timecode for desired time
        
    Exceptions:
        InputError, occurs when:
            - channel_id does not refer to a valid channel
            - length of message is over 1000 characters.
            - time_sent is in the past
        
        AccessError, occurs when:
            - channel_id is valid and the authorised user is not a member of the channel.
         
    Return Value:
        Message_id - will only be valid once specified time is passed.
    '''   
    check_valid_token(token)
    data = data_store.get()
            
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    # channel_id does not refer to a valid channel
    if channel_id not in [channel['channel_id'] for channel in data['channels']]:
        raise InputError(description="Channel ID not valid")
    
    # channel_id is valid and the authorised user does not exist
    target_channel = data['channels'][channel_id - 1]   
    # channel_id is valid and the authorised user is not a member of the channel
    if auth_user_id not in [user['u_id'] for user in target_channel['all_members']]:
        raise AccessError(description="The authorised user is not a member of the channel") 

    # length of message is less than 1 or over 1000 characters
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="message must be between 1 and 1000 characters inclusive")
    
    current_time = time.mktime(datetime.datetime.now().timetuple())
    length = time_sent - current_time

    if (length < 0):
        raise InputError(description='time_sent is in the past.')

    message_id = 0
    if len(target_channel['channel_messages']) == 0:
        message_id = channel_id * MESSAGE_MAX
    else:
        message_id = target_channel['max_message_id'] + 1
    target_channel['max_message_id'] = message_id

    # after specified time execute function to finish standup
    t = threading.Timer(length, message_send_givenid_v1, args = [token, channel_id, message, message_id])
    t.start()

    return { 'message_id': message_id }

def message_send_givenid_v1(token, channel_id, message, message_id):
    '''
    Description:
        Send a message from the authorised user to the channel specified by channel_id.
        Each message should have its own unique ID, i.e. no messages should share an ID with another message,
        even if that other message is in a different channel.
        
    Arguments:
        token           - string
        channel_id      - int
        message         - string
        message_id      - int
        
    Exceptions:
        Assumed previously checked

    Return Value:
        { message_id } where message_id is int
    '''

    data = data_store.get()
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    target_channel = data['channels'][channel_id - 1]
    
    utc_timestamp = utc_now()
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': utc_timestamp,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False,
            }
        ],
        'is_pinned': False,
    }
    
    list_of_handles = [member["handle_str"] for member in target_channel['all_members']]
    auth_user_handle = data['users'][auth_user_id - 1]['handle_str']
    regex = r"@[A-Za-z0-9]+"
    tagged_handles = re.findall(regex, message)
    tagged_handles = list(set([handle[1:] for handle in tagged_handles]))
    tagged_handles = [handle for handle in tagged_handles if handle in list_of_handles]
    for handle in tagged_handles:
        handle_index = list_of_handles.index(handle)
        tagged_user_u_id = target_channel['all_members'][handle_index]['u_id']
        tagged_user_profile = data['users'][tagged_user_u_id - 1]
        notif_message = message[:20] if len(message) >= 20 else message
        channel_name = target_channel['channel_name']
        tagged_user_profile['notifications'].insert(0, {
                'channel_id': channel_id,
                'dm_id': -1,
                'notification_message': f"{auth_user_handle} tagged you in {channel_name}: {notif_message}"
            }
        )
    
    target_channel['channel_messages'] = [message_dict] + target_channel['channel_messages']
    user_stats = data['users'][auth_user_id - 1]['user_stats']
    utc_timestamp = utc_now()
    workspace_stats = data['workspace_stats']
    workspace_stat_point = new_workspace_point(data, utc_timestamp, 0, 0 ,1)
    workspace_stats['messages_exist'] += workspace_stat_point['messages_exist']
    
    userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 0, 0, 1)
    data['users'][auth_user_id - 1]['user_stats']['messages_sent'] += userstat_point['messages_sent']
    
    data_store.set(data)
    return {
        'message_id': message_id,
    }

def message_sendlater_dm_v1(token, dm_id, message, time_sent):
    '''
    Description:
        Send a message to the channel at a specified future time automativally.
        
    Arguments:
        - token         (string)    - token of the user wanting to edit a message
        - dm_id         (integer)   - ID of the channel to send message
        - message       (string)    - message string
        - time_sent     (integer)   - UTC timecode for desired time
        
    Exceptions:
        InputError, occurs when:
            - dm_id does not refer to a valid dm
            - length of message is over 1000 characters.
            - time_sent is in the past
        
        AccessError, occurs when:
            - channel_id is valid and the authorised user is not a member of the channel.
         
    Return Value:
        Message_id - will only be valid once specified time is passed.
    '''   
    data = data_store.get()
            
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    # dm_id does not refer to a valid dm
    if dm_id not in [dm['dm_id'] for dm in data['dms'] if not dm['removed']]:
        raise InputError(description="The dm_id you provide does not refer to a valid dm.")
    
    target_dm = data['dms'][dm_id - 1]
    # dm_id is valid and the authorised user is not a member of DM
    if auth_user_id not in [user['u_id'] for user in target_dm['all_members']]:
        raise AccessError(description="You are not even a member of this DM")

    # length of message is less than 1 or over 1000 characters
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="message must be between 1 and 1000 characters inclusive")
    
    current_time = time.mktime(datetime.datetime.now().timetuple())
    length = time_sent - current_time

    if (length < 0):
        raise InputError(description='time_sent is in the past.')

    message_id = -1*(dm_id * MESSAGE_MAX) if len(target_dm['dm_messages']) == 0 else target_dm['max_message_id'] - 1
    target_dm['max_message_id'] = message_id

    # after specified time execute function to finish standup
    t = threading.Timer(length, message_senddm_givenid_v1, args = [token, dm_id, message, message_id])
    t.start()

    return { 'message_id': message_id }

def message_senddm_givenid_v1(token, dm_id, message, message_id):
    '''
    Description:
        Send a message from the authorised user to the channel specified by dm_id.
        Each message should have its own unique ID, i.e. no messages should share an ID with another message,
        even if that other message is in a different channel.
        
    Arguments:
        token           - string
        channel_id      - int
        message         - string
        message_id      - int
        
    Exceptions:
        Assumed previously checked

    Return Value:
        { message_id } where message_id is int
    '''

    data = data_store.get()

    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    target_dm = data['dms'][dm_id - 1]
    utc_timestamp = utc_now()
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': utc_timestamp,
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False,
            }
        ],
        'is_pinned': False,
    }
    target_dm['dm_messages'] = [message_dict] + target_dm['dm_messages']
    
    list_of_handles = [member["handle_str"] for member in target_dm['all_members']]
    auth_user_handle = data['users'][auth_user_id - 1]['handle_str']
    regex = r"@[A-Za-z0-9]+"
    tagged_handles = re.findall(regex, message)
    tagged_handles = list(set([handle[1:] for handle in tagged_handles]))
    tagged_handles = [handle for handle in tagged_handles if handle in list_of_handles]
    for handle in tagged_handles:
        handle_index = list_of_handles.index(handle)
        tagged_user_u_id = target_dm['all_members'][handle_index]['u_id']
        tagged_user_profile = data['users'][tagged_user_u_id - 1]
        notif_message = message[:20] if len(message) >= 20 else message
        dm_name = target_dm['dm_name']
        tagged_user_profile['notifications'].insert(0, {
                'channel_id': -1,
                'dm_id': dm_id,
                'notification_message': f"{auth_user_handle} tagged you in {dm_name}: {notif_message}"
            }
        )
    
    user_stats = data['users'][auth_user_id - 1]['user_stats']
    utc_timestamp = utc_now()
    workspace_stats = data['workspace_stats']
    workspace_stat_point = new_workspace_point(data, utc_timestamp, 0, 0 ,1)
    workspace_stats['messages_exist'] += workspace_stat_point['messages_exist']
    
    userstat_point = new_userstat_point(workspace_stats, user_stats, utc_timestamp, 0, 0, 1)
    data['users'][auth_user_id - 1]['user_stats']['messages_sent'] += userstat_point['messages_sent']
    
    data_store.set(data)
    return {
        'message_id': message_id,
    }
