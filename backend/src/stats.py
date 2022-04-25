'''
This file contains the functions for stats
'''

from src.helpers import check_valid_token
from src.data_store import data_store
import jwt
SECRET = 'placeholder'

def workspace_stats(token):
    '''
    <Fetches the required statistics about the use of UNSW Seams.>

    Arguments:
        token (string)  - The user's web token.

    Exceptions:
        AccessError - Occurs when token doesn't refer to a valid user.

    Return Value:
        Returns a python dictionary containing time stamped data points to every change in the number of channels,
        number of dms and the number of messages, also the overall utilization rate.
        look like this:
    {
        'workspace_stats': {
            channels_exist: [
                {
                    num_channels_exist: (integer), 
                    time_stamp: (integer),
                }, ...
            ], 
            dms_exist: [
                {
                    num_dms_exist: (integer), 
                    time_stamp: (integer),
                }
            ], 
            messages_exist: [
                {
                    num_messages_exist: (integer), 
                    time_stamp: (integer)
                }
            ], 
            utilization_rate: (float between 0 and 1 inclusive.)
        }
    }
    '''
    
    check_valid_token(token)
    store = data_store.get()

    actual_users = [user for user in store['users'] if not user['removed']]
    actual_involved_users = [user for user in actual_users if ((len(user['channels_joined']) != 0 or len(user['dms_joined']) != 0))]

    return {
        'workspace_stats': {
            'channels_exist': store['workspace_stats']['channels_exist'], 
            'dms_exist': store['workspace_stats']['dms_exist'], 
            'messages_exist': store['workspace_stats']['messages_exist'], 
            'utilization_rate': 0.0 if len(actual_users) == 0 else len(actual_involved_users)/len(actual_users)
        }
    }   

def user_stats(token):
    '''
    <Fetches the required statistics about this user's use of UNSW Seams.>

    Arguments:
        token (string)  - The user's web token.

    Exceptions:
        AccessError - Occurs when token doesn't refer to a valid user.

    Return Value:
        Returns a python dictionary containing time stamped data points to every change in the number of channels joined,
        dms joined and the number of messages sent, also the overall involvement rate.
        look like this:
    {
        'user_stats': {
            channels_exist: [
                {
                    channels_joined: (integer), 
                    time_stamp: (integer),
                }, ...
            ], 
            dms_exist: [
                {
                    dms_joined: (integer), 
                    time_stamp: (integer),
                }
            ], 
            messages_exist: [
                {
                    messages_sent: (integer), 
                    time_stamp: (integer)
                }
            ], 
            utilization_rate: (float between 0 and 1 inclusive.)
        }
    }
    '''
    
    check_valid_token(token)
    store = data_store.get()
    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
    user_stat = store['users'][auth_user_id - 1]['user_stats']
    
    num_channels_joined = user_stat['channels_joined'][-1]['num_channels_joined']
    num_dms_joined = user_stat['dms_joined'][-1]['num_dms_joined']
    num_messages_sent = user_stat['messages_sent'][-1]['num_messages_sent']
    
    num_channels = store['workspace_stats']['channels_exist'][-1]['num_channels_exist']
    num_dms = store['workspace_stats']['dms_exist'][-1]['num_dms_exist']
    num_messages = store['workspace_stats']['messages_exist'][-1]['num_messages_exist']
    numerator = num_channels_joined + num_dms_joined + num_messages_sent
    denominator = num_channels + num_dms + num_messages
    
    involvement = 0.0 if denominator == 0 else numerator/denominator
    if involvement > 1:
        involvement = 1.0
    
    return {
        'user_stats': {
            'channels_joined': user_stat['channels_joined'],
            'dms_joined': user_stat['dms_joined'],
            'messages_sent': user_stat['messages_sent'],
            'involvement_rate': involvement
        }
    }