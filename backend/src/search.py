'''
search.py
4/4/22
Amy Pham z5359018 - W11B CAMEL
'''
from src.data_store import data_store
from src.error import InputError
from src.helpers import check_valid_token
import jwt
SECRET = 'placeholder'

def search_v1(token, query_str):
    '''
    Given a query string, return a collection of messages in all of the channels/DMs 
    that the user has joined that contain the query (case-insensitive). 
    There is no expected order for these messages.

    Arguments:
        auth_user_id (int) - u_id of user calling search_v1
        query_str (string) - string of 1-1000 characters

    Exceptions:
    InputError  - Occurs when query_str is less than 1 or over 1000 characters

    Return Value:
        Returns dictionary containing list of messages found in the form
        {
            'messages': []
        }
        on the condition that no Input Errors are raised.
    '''

    # len of query_str must be 1-1000 chars
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError(description="Query must be 1 to 1000 characters in length")
    
    
    store = data_store.get()
    channels_list = store["channels"]
    dms_list = store['dms']


    # finds channels user has joined
    channels_joined = []
    for channel in channels_list:
        if check_user_joined(channel['all_members'], auth_user_id) == True:
            channels_joined += channel['channel_messages']
                
    
    # finds dms user has joined
    dms_joined = []
    for dm in dms_list:
        if check_user_joined(dm['all_members'], auth_user_id) == True:
            dms_joined += dm['dm_messages']
    

    # all dms and channels user is in has been found
    # puts all messages from each into list
    # where channel messages are before dm_messages
    

    # checks for matches in messages_joined
    matches = []
    for message in channels_joined:
        if query_str.lower() in message['message'].lower():
            matches.append(message)
    for message in dms_joined:
        if query_str.lower() in message['message'].lower():
            matches.append(message)
    
    return {
        'messages': matches
    }

def check_user_joined(members_list, auth_user_id):
    '''
    Takes in a list of members in a channel/dm and a user's auth_user_id,
    checks if the user is a member and returns 'True' if they are.
    '''
    for member in members_list:
        if member['u_id'] == auth_user_id:
            return True
    return False
    