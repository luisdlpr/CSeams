'''
auth.py
4/3/22
Amy Pham z5359018 - W11B CAMEL
Contains auth_login and auth_register
implemented according to the project specification
'''

import re
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import make_token, hash, check_valid_token, utc_now
from src.config import url as BASE_URL
SECRET = 'placeholder'


def auth_login_v1(email, password):
    '''
    Given a registered user's email and password,
    returns their `auth_user_id` value.

    Arguments:
        email (string) - user's email in format ___@___.___
        password (string) - user's password (6 characters is min. length)

    Exceptions:
    InputError  - Occurs when email is not already registered
                - Occurs when password does not match registered password

    Return Value:
        Returns auth_user_id of the logged in user in a dictionary
        on the condition that no Input Errors are raised
    '''

    store = data_store.get()
    users_list = store['users']

    # check for registered email
    if email not in [user['email'] for user in users_list]:
        raise InputError(description="Email entered does not belong to a user")

    # retriving the profile
    user_profile = users_list[[user['email'] for user in users_list].index(email)]
    # see if password match
    if hash(password) != user_profile['password']:
        raise InputError(description="Password is not correct")

    tok = make_token(user_profile['u_id'], None)
    # update token
    for user in users_list:
        if user['u_id'] == user_profile['u_id']:
            user['token'].append(tok)
            data_store.set(store)
    
    return {
        'auth_user_id': user_profile['u_id'],
        'token': tok
    }

def auth_register_v1(email, password, name_first, name_last):
    '''
    Given a user's first and last name, email address, and password,
    create a new account for them and return a new `auth_user_id`.

    Arguments:
        email (string)      - user's email in format: ___@___.___
        password (string)   - user's password (6 chars is min. length)
        name_first (string) - user's first name (length is 1-50 characters inclusive)
        name_last (string)  - user's last name (length is 1-50 characters inclusive)

    Exceptions:
    InputError  - Occurs when email is in an invalid format
                - Occurs when password is under 6 chars long
                - Occurs when name_first is outside range of 1-50 chars
                - Occurs when name_last is outside range of 1-50 chars
                - Occurs when email has already been registered

    Return Value:
        Returns auth_user_id  (where auth_user_id starts from 1)
        of the newly registered user in a dictionary
        on the condition that no Input Errors are raised

    '''

    # retrieves users from data_store
    store = data_store.get()
    users_list = store['users']

    # checks correct data is given
    correct_input(email, password, name_first, name_last)

    # no repeat emails
    for user in users_list:
        if email in user['email'] and not user['removed']:
            raise InputError(description="Email address is already being used by another user")

    # create user handle (max 20 char) to store in users list
    # normalise the first and last name, removing all non alphanumeric characters.
    normalised_first = ''.join(character for character in name_first if character.isalnum())
    normalised_last = ''.join(character for character in name_last if character.isalnum())

    handle = (normalised_first + normalised_last).lower()
    if len(handle) >= 20:
        handle = handle[:20]

    # ensure no duplicate handles
    user_handles = [user['handle_str'] for user in users_list if not user['removed']]

    handle = handle_unique(user_handles, handle)

    # create user id
    user_id = len(users_list) + 1

    # create permission_id
    perm_id = 1 if user_id == 1 else 2
    
    # make token
    tok = make_token(user_id, None)

    utc_timestamp = utc_now()
    # make dictionary containing user details
    
    ### TODO: make if statement that if this is the first user joined, alter the data_store's workspace stat as well.
    
    user_details = {
        'u_id': user_id,
        'email': email,
        'password': hash(password),
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': handle,
        'permission_id': perm_id,
        'dms_interacted': [],
        "channels_interacted": [],
        'dms_joined': [],
        "channels_joined": [],
        'removed': False,
        'token': [tok],
        'reset_code': None,
        'notifications': [],
        'profile_img_url': f"{BASE_URL}/images/default.jpg",
        'user_stats': {
            'channels_joined': [{'num_channels_joined': 0,'time_stamp': utc_timestamp}],
            'dms_joined': [{'num_dms_joined': 0,'time_stamp': utc_timestamp}],
            'messages_sent': [{'num_messages_sent': 0,'time_stamp': utc_timestamp}],
        }
    }
    
    ## workspace stats stuff.
    if len(users_list) == 0:    
        store['workspace_stats'] = {
            'channels_exist': [{'num_channels_exist': 0, 'time_stamp': utc_timestamp}], 
            'dms_exist': [{'num_dms_exist': 0, 'time_stamp': utc_timestamp}], 
            'messages_exist': [{'num_messages_exist': 0, 'time_stamp': utc_timestamp}], 
        }

    users_list.append(user_details)
    data_store.set(store)
    return {
        'auth_user_id': user_id,
        'token': tok
    }

def correct_input(email, password, name_first, name_last):
    '''
    Checks user input passed in auth_register
    is valid and raises InputError if conditions are not satified

    correct_input is passed the following arguments:
        email (string)      - user's email in format: ___@___.___
        password (string)   - user's password (6 chars is min. length)
        name_first (string) - user's first name (length is 1-50 characters inclusive)
        name_last (string)  - user's last name (length is 1-50 characters inclusive)

    correct_input raises the following exceptions:
    InputError  - Occurs when email is in an invalid format
                - Occurs when password is under 6 chars long
                - Occurs when name_first is outside range of 1-50 chars
                - Occurs when name_last is outside range of 1-50 chars
    '''

    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(regex, email):
        raise InputError(description="Email entered is not a valid email")

    if len(password) < 6:
        raise InputError(description="Length of password is less than 6 characters")

    if len(name_first) > 50 or name_first == "":
        raise InputError(description="First name must be between 1-50 characters long")

    if len(name_last) > 50 or name_last == "":
        raise InputError(description="Last name must be between 1-50 characters long")

    #if name_first == "Removed" and name_last == "user":
    #    raise InputError("Forbidden name combination.  Please choose another.")

def handle_unique(user_handles, handle):
    '''
    Enumerate duplicate handle to make unique handle

    handle_unique is passed the following arguments:
        user_handles (list of strings) - list with handles of all registered users
        handle (string) - handle created from first + last name

    handle_unique returns new_handle (string) on completion
    '''

    # changed it so now it won't automatically add a zero.
    num = 0
    newhandle = handle
    while newhandle in user_handles:
        newhandle = handle + str(num)
        num += 1
    return newhandle


def auth_logout_v1(token):
    '''
    Given an active token, invalidates the token to log the user out.

    Arguments:
        token - jwt encoded with payload {
                 "auth_user_id":
                 "session_id:   
                }

    Exceptions:
    AccessError - Occurs when invalid token is passed

    Return Value:
        Returns an empty dictionary {}
        on the condition that no AccessErrors are raised
    '''
    check_valid_token(token)
    store = data_store.get()
    users_list = store['users']

    '''
    is_valid = False
    # check token belongs to a user and is also valid
    for user in users_list:
        for tok in user['token']:
            if tok == token:
                is_valid = True

    if is_valid == False:
        raise AccessError(description="Token entered does not belong to a user")
    '''
    # removes invalidated token
    for user in users_list:
        for tok in user['token']:
            if tok == token:
                user['token'].remove(tok)
                data_store.set(store)


    return {}

def auth_passwordreset_request_v1(email):
    '''
    Given an email address, identifies if the email is registered.
    When a user requests a password reset,
    they should be logged out of all current sessions.

    Arguments:
        email (string) - user's email in format: ___@___.___

    Exceptions:
        NONE

    Return Value:
        Returns 'True' if the email is registered 
        and 'False' for unregistered emails
    '''
    store = data_store.get()
    users_list = store['users']

    # check for registered email
    if email not in [user['email'] for user in users_list]:
        return False

    # removes stored tokens of that user (logs out)
    # adds reset_code to that user
    code = hash(email)
    for user in users_list:
        if user['email'] == email:
            user['token'] = []
            user['reset_code'] = code
            data_store.set(store)
   
    return True

def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    Given an email address, identifies if the email is registered.
    When a user requests a password reset,
    they should be logged out of all current sessions.

    Arguments:
        reset_code(string)   - unique code used to reset a password
        new_password(string) - user's new password (6 chars is min. length)

    Exceptions:
        InputError  - Occurs when reset_code is invalid 
                    - Occurs when new_password is under 6 chars long

    Return Value:
        Returns empty dictionary {} on the condition 
        that no Input Errors are raised
    '''
    store = data_store.get()
    users_list = store['users']

    # check length of new_pass
    if len(new_password) < 6:
        raise InputError(description="Length of password is less than 6 characters")
    
    # checks reset code is valid
    u_id = 0
    for user in users_list:
        if user['reset_code'] == reset_code:
            u_id = user['u_id']
    if u_id == 0:
        raise InputError(description="Invalid reset code")

    # resets password and removes reset_code
    for user in users_list:
        if user['u_id'] == u_id:
            user['password'] = hash(new_password)
            user['reset_code'] = None
    data_store.set(store)

    return {}
    
