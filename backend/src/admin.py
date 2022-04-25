'''
All functions in this file were implemented by
z5206766 Luis Reyes
UNSW comp1531 22t1
'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.config import url as BASE_URL
from src.helpers import check_valid_token
import jwt
SECRET = 'placeholder'

def admin_user_remove_v1(token, u_id):
    '''
    Given a user by their u_id, remove them from the Seams.  Specifically:
    - Removed from all channels/DMs
    - Details overwritten in 'users' with:
        - name_first: 'Removed'
        - name_last: 'user'

    Arguments:
        token           - string  (token of the authorised user)
        u_id            - integer (ID of the user to be removed from seams)

    Exceptions:
        InputError - Occurs when:
            u_id does not refer to a valid user.
            u_id refers to a user who is the only remaining global owner.

        AccessError - Occurs when:
            Authorised user is not a global owner.

    Return Value:
        Returns {} an empty dictionary unless an InputError or an AccessError is raised.
    '''

    data = data_store.get()
    users = data['users']
    channels = data['channels']
    dms = data['dms']
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    
    permissions = [user['u_id'] for user in users if user['permission_id'] == 1 and not user['removed']]
    ##check AccessError: auth_user_id is not a global owner
    if auth_user_id not in permissions:
        raise AccessError(description="You do not have global owner permissions")
    
    # u_id does not refer to a valid user raise InputError
    if u_id not in [user['u_id'] for user in users if not user['removed']]:
        raise InputError(description="User id not valid.")

    # u_id is the only remaining global owner raise InputError

    if len(permissions) <= 1 and (u_id in permissions):
        raise InputError(description="User id is the only remaining global owner.")

    desireduser = data['users'][u_id - 1]
    desireduser_local_channel_details = {
        'u_id': desireduser['u_id'],
        'email': desireduser['email'],
        'name_first': desireduser['name_first'],
        'name_last': desireduser['name_last'],
        'handle_str': desireduser['handle_str'],
        'profile_img_url': desireduser['profile_img_url']
    }
    
    ''' 
    for channel in channels:
        if u_id in [user['u_id'] for user in channel['all_members']]:
            new_all_members = [users for users in channel['all_members'] if users != desireduser_local_channel_details]
            channel['all_members'] = new_all_members
        if u_id in [user['u_id'] for user in channel['owner_members']]:
            new_owner_members = [users for users in channel['owner_members'] if users != desireduser_local_channel_details]
            channel['owner_members'] = new_owner_members
        for message in channel['channel_messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'        
    '''
    #### altered a bit to optimise time by searching searching for channels the user had interacted with #######
    for channel_id in desireduser['channels_interacted']:
        channel = data['channels'][channel_id - 1]
        if u_id in [user['u_id'] for user in channel['all_members']]:
            new_all_members = [users for users in channel['all_members'] if users != desireduser_local_channel_details]
            channel['all_members'] = new_all_members
        if u_id in [user['u_id'] for user in channel['owner_members']]:
            new_owner_members = [users for users in channel['owner_members'] if users != desireduser_local_channel_details]
            channel['owner_members'] = new_owner_members
        for message in channel['channel_messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'


    data['channels'] = channels

    '''
    for dm in dms:
        if u_id in [user['u_id'] for user in dm['all_members']]:
            new_all_members = [users for users in dm['all_members'] if users != desireduser_local_channel_details]
            dm['all_members'] = new_all_members
        if u_id in [user['u_id'] for user in dm['owner_members']]:
            new_owner_members = [users for users in dm['owner_members'] if users != desireduser_local_channel_details]
            dm['owner_members'] = new_owner_members
        for message in dm['dm_messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'
    '''        
    #### altered a bit to optimise time by searching searching for DM the user had interacted with #######
    for dm_id in desireduser['dms_interacted']:
        dm = data['dms'][dm_id - 1]
        if u_id in [user['u_id'] for user in dm['all_members']]:
            new_all_members = [users for users in dm['all_members'] if users != desireduser_local_channel_details]
            dm['all_members'] = new_all_members
        if u_id in [user['u_id'] for user in dm['owner_members']]:
            new_owner_members = [users for users in dm['owner_members'] if users != desireduser_local_channel_details]
            dm['owner_members'] = new_owner_members
        for message in dm['dm_messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'

    data['dms'] = dms

    for user in data['users']:
        if user['u_id'] == u_id:
            user['channels_joined'] = user['dms_joined'] = []
            user['name_first'] = 'Removed'
            user['name_last'] = 'user'
            user['removed'] = True
            user['token'] = []

    data_store.set(data)

    return {}

def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    Authenticated by a current global owner (permission id 1).  Given a user by 
    their u_id, change their permission id.

    Arguments:
        token           - string  (token of the authorised user)
        u_id            - integer (ID of the user to be removed from seams)
        permission_id   - integer (1 - global owner, 2 - member)

    Exceptions:
        InputError - Occurs when:
            u_id does not refer to a valid user.
            u_id refers to a user who is the only remaining global owner 
                and they are being demoted to member.
            permission_id is invalid (not == 1 or 2)
            permission_id change will have no effect

        AccessError - Occurs when:
            Authorised user is not a global owner.

    Return Value:
        Returns {} an empty dictionary unless an InputError or an AccessError is raised.
    '''

    data = data_store.get()
    users = data['users']
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']

    #if authorisation user is found, and they breach accesserror, raise and do not set
    for user in users:
        if user['u_id'] == auth_user_id:
            if user['permission_id'] != 1:
                raise AccessError(description="authorisation user is not a global owner.")

    # u_id does not refer to a valid user raise InputError
    if u_id not in [user['u_id'] for user in users]:
        raise InputError(description="User id not valid.")

    # u_id is the only remaining global owner raise InputError
    permissions = [user['u_id'] for user in users if user['permission_id'] == 1]
    if len(permissions) <= 1 and (u_id in permissions) and permission_id == 2:
        raise InputError(description="User id is the only remaining global owner.")

    if permission_id != 1 and permission_id != 2:
        raise InputError(description="Invalid permission id.")

    for user in users:
        #if target user is found, check for last input error and update permission id
        if user['u_id'] == u_id:
            if user['permission_id'] == permission_id:
                raise InputError(description="Invalid permission id.")
            else:
                user['permission_id'] = permission_id


    data_store.set(data)

    return {}
