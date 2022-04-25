

import re, hashlib, imgspy, jwt
from PIL import Image
from src.data_store import data_store
from src.error import AccessError, InputError
import urllib.request
from src.config import url as BASE_URL
from src.helpers import check_valid_token
SECRET = 'placeholder'

def users_all_v1(token):
    '''
    Returns a list of all users and their associated details.

    Arguments:
        auth_user_id (integer) - ID of the authorised user
        
    Exceptions:
        AccessError  - Occurs when:
            auth_user_id does not refer to an actual user

    Return Value:
        If no exceptions are raised.
        Returns a list of pyton dictionaries containing each user's u_id,
        first name, last name, email and handle name.
        In the following format.
        {
            'users': [
                {
                    'u_id': (integer),
                    'email': (string),
                    'name_first': (string),
                    'name_last': (string),
                    'handle_str': (string),
                },...
            ]
        }
    '''
    check_valid_token(token)
    store = data_store.get()
    users_list = store['users']
    
    '''
    if auth_user_id not in [user['u_id'] for user in users_list]:
        raise AccessError(description="You are not a registered user, how did you even get here?")
    '''
    profile_list = []
    for user in users_list:
        if user['removed']:
            continue
        user_details = {
            'u_id': user['u_id'],
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['handle_str'],
            'profile_img_url': user['profile_img_url']
        }
        profile_list.append(user_details)
    return {
        'users': profile_list
    }
    
def user_profile_v1(token, u_id):
    '''
    For a valid user, returns information about their user id, email, first name, last name, and handle

    Arguments:
        auth_user_id    (integer) - ID of the authorised user
        u_id            (integer) - ID of the user who's profile you want to see.
        
    Exceptions:
        InputError   - Occurs when:
            u_id don't refer to a valid user
        AccessError  - Occurs when:
            auth_user_id does not refer to an actual user

    Return Value:
        If no exceptions are raised
        Returns a python dictionary containing the user's u_id,
        first name, last name, email and handle name.
        In the following format.
        {
            'user' : {
                    'u_id': (integer),
                    'email': (string),
                    'name_first': (string),
                    'name_last': (string),
                    'handle_str': (string),
            },...
            
        }
    '''
    check_valid_token(token)
    store = data_store.get()
    users_list = store['users']
    
    '''
    if auth_user_id not in [user['u_id'] for user in users_list]:
        raise AccessError(description="You are not a registered user, how did you even get here?")
    '''
    
    if u_id not in [user['u_id'] for user in users_list]:
        raise InputError(description="user id does not refer to valid user")
    
    desired_user = users_list[u_id - 1]
    return {
        'user': {
            'u_id': desired_user['u_id'],
            'email': desired_user['email'],
            'name_first': desired_user['name_first'],
            'name_last': desired_user['name_last'],
            'handle_str': desired_user['handle_str'],
            'profile_img_url': desired_user['profile_img_url']       
        }
    }
    
def profile_setname_v1(token, name_first, name_last):
    '''
    Update the authorised user's first and last name

    Arguments:
        auth_user_id    (integer) - ID of the authorised user
        name_first      (string)  - The new first name
        name_last       (srting)  - The new last name
        
    Exceptions:
        InputError   - Occurs when:
            length of name_first or name_last is not between 1 and 50 characters inclusive.
        AccessError  - Occurs when:
            auth_user_id does not refer to an actual user

    Return Value:
        If no exceptions are raised, return an empty python dictionary.
    '''
    store = data_store.get()
    users_list = store['users']
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    '''
    if auth_user_id not in [user['u_id'] for user in users_list]:
        raise AccessError(description="You are not a registered user, how did you even get here?")
    '''

    desired_user = users_list[auth_user_id - 1]
    
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="length of first name must be between 1 and 50 characters inclusive")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="length of first name must be between 1 and 50 characters inclusive")    
    
    desired_user['name_first'] = name_first
    desired_user['name_last'] = name_last
    
    ########### change every mentioning of the name to the new one #########
    ## basically, see if 
    ####### channels ########
    for channel in store['channels']:
        for member in channel['all_members']:
            if member['u_id'] == auth_user_id:
                member['name_first'] = name_first
                member['name_last'] = name_last
                
        for member in channel['owner_members']:
            if member['u_id'] == auth_user_id:
                member['name_first'] = name_first
                member['name_last'] = name_last
                

    ####### dms #######
    for dm in store['dms']:
        for member in dm['all_members']:
            if member['u_id'] == auth_user_id:
                member['name_first'] = name_first
                member['name_last'] = name_last
                
        for member in dm['owner_members']:
            if member['u_id'] == auth_user_id:
                member['name_first'] = name_first
                member['name_last'] = name_last
                
    
    data_store.set(store)
    return {}

def profile_setemail_v1(token, email):
    '''
    Update the authorised user's email address

    Arguments:
        auth_user_id    (integer) - ID of the authorised user
        email           (string)  - The new email address
        
    Exceptions:
        InputError   - Occurs when:
            - email entered is not a valid email.
            - email address is already used by another user.
        AccessError  - Occurs when:
            auth_user_id does not refer to an actual user.

    Return Value:
        If no exceptions are raised, return an empty python dictionary.
    '''
    store = data_store.get()
    users_list = store['users']
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    '''
    if auth_user_id not in [user['u_id'] for user in users_list]:
        raise AccessError(description="You are not a registered user, how did you even get here?")
    '''

    ##### email checks #####
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(regex, email):
        raise InputError(description="Email entered is not a valid email")
    if email in [user['email'] for user in users_list]:
        raise InputError(description="Email address is already being used by another user")

    desired_user = users_list[auth_user_id - 1]    
    desired_user['email'] = email
    
    ########### change every mentioning of the name to the new one #########
    ####### channels ########
    for channel in store['channels']:
        for member in channel['all_members']:
            if member['u_id'] == auth_user_id:
                member['email'] = email
                
        for member in channel['owner_members']:
            if member['u_id'] == auth_user_id:
                member['email'] = email
                

    ####### dms #######
    for dm in store['dms']:
        for member in dm['all_members']:
            if member['u_id'] == auth_user_id:
                member['email'] = email
                
        for member in dm['owner_members']:
            if member['u_id'] == auth_user_id:
                member['email'] = email
                
    
    data_store.set(store)
    return {}


def profile_sethandle_v1(token, handle_str):
    '''
    Update the authorised user's handle (i.e. display name)

    Arguments:
        auth_user_id    (integer) - ID of the authorised user
        handle_str      (string)  - The new handle
        
    Exceptions:
        InputError   - Occurs when:
            - length of handle_str is not between 3 and 20 characters inclusive
            - handle_str contains characters that are not alphanumeric
            - the handle is already used by another user
            
        AccessError  - Occurs when:
            auth_user_id does not refer to an actual user.

    Return Value:
        If no exceptions are raised, return an empty python dictionary.
    '''
    
    store = data_store.get()
    users_list = store['users']
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    '''
    if auth_user_id not in [user['u_id'] for user in users_list]:
        raise AccessError(description="You are not a registered user, how did you even get here?")
    '''

    desired_user = users_list[auth_user_id - 1]
    
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description="length of handle must be between 3 and 20 characters inclusive")  
    
    if not handle_str.isalnum():
        raise InputError(description="There are non alphanumeric characters in the handle string")
    
    if handle_str in [user['handle_str'] for user in users_list]:
        raise InputError(description="The handle is in use by another user.")
    
    desired_user['handle_str'] = handle_str
    
    ########### change every mentioning of the name to the new one #########
    ####### channels ########
    for channel in store['channels']:
        for member in channel['all_members']:
            if member['u_id'] == auth_user_id:
                member['handle_str'] = handle_str
        for member in channel['owner_members']:
            if member['u_id'] == auth_user_id:
                member['handle_str'] = handle_str
            
    ####### dms #######
    for dm in store['dms']:
        for member in dm['all_members']:
            if member['u_id'] == auth_user_id:
                member['handle_str'] = handle_str
        for member in dm['owner_members']:
            if member['u_id'] == auth_user_id:
                member['handle_str'] = handle_str
    return {}

def profile_upload_photo_v1(token, img_url, x_start, y_start, x_end, y_end):
    
    '''
    <Given a URL of an image on the internet, crops the image within bounds 
    (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left. >

    Arguments:
        auth_user_id (integer)  - user_id assigned to the user when creating account.
        img_url (string)        - the url of the image.
        x_start (integer)       - starting x coordinate.
        y_start (integer)       - starting y coordinate.
        x_end   (integer)       - ending x coordinate.
        y_end   (integer)       - ending y coordinate. 

    Exceptions:
        AccessError - Occurs when auth_user_id is not valid
        
        InputError  - Occurs when:
            - img_url returns an HTTP status other than 200, 
              or any other errors occur when attempting to retrieve the image
            - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
            - x_end is less than or equal to x_start or y_end is less than or equal to y_start
            - image uploaded is not a JPG

    Return Value:
        If no errors are raised, returns an empty dictionary {}.
    '''

    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    
    try:   
        imageinfo = imgspy.info(img_url)
        width, height = imageinfo['width'], imageinfo['height']
        if imageinfo['type'] != "jpg":
            raise InputError(description="Not a JPG file")
        
        if (x_end <= x_start or y_end <= y_start):
            raise InputError(description="Your crop dimensions are a bit scuffed.")
        
        # checking if the crop size match the image dimension.
        for x_coord in [x_start, x_end]:
            if (x_coord < 0 or x_coord > width):
                raise InputError(description="The crop size aren't within the dimensions of the image")
        for y_coord in [y_start, y_end]:
            if (y_coord < 0 or y_coord > height):
                raise InputError(description="The crop size aren't within the dimensions of the image")
    except Exception as error:
        raise InputError(description="Something's wrong with your Inputs") from error
    
    ### make a new file name.
    url_string = hashlib.sha256(str(auth_user_id).encode()).hexdigest()
    file_path = f"images/{url_string}.jpg"
    urllib.request.urlretrieve(img_url, file_path)
    ### crop it.
    imageObject = Image.open(file_path)
    cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    cropped.save(file_path)
    
    store = data_store.get()
    user_profile = store['users'][auth_user_id - 1]
    user_profile['profile_img_url'] = f"{BASE_URL}/{file_path}"
    
    for channel_id in user_profile['channels_joined']:
        desired_channel_all_members = store['channels'][channel_id - 1]['all_members']
        for user in desired_channel_all_members:
            if user['u_id'] == auth_user_id:
                user['profile_img_url'] = f"{BASE_URL}/{file_path}"
        desired_channel_owner_members = store['channels'][channel_id - 1]['owner_members']
        for user in desired_channel_owner_members:
            if user['u_id'] == auth_user_id:
                user['profile_img_url'] = f"{BASE_URL}/{file_path}"
    for dm_id in user_profile['dms_joined']:
        desired_dm_all_members = store['dms'][dm_id - 1]['all_members']
        for user in desired_dm_all_members:
            if user['u_id'] == auth_user_id:
                user['profile_img_url'] = f"{BASE_URL}/{file_path}"
        desired_dm_owner_members = store['dms'][dm_id - 1]['owner_members']
        for user in desired_dm_owner_members:
            if user['u_id'] == auth_user_id:
                user['profile_img_url'] = f"{BASE_URL}/{file_path}"
           
    data_store.set(store)
    return {}    
    