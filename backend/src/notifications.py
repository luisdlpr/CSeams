'''
    Contains the notfications/get functionalities
    Coded up by Westley Lo
    z5363938
'''
from src.data_store import data_store
from src.helpers import check_valid_token
import jwt
SECRET = 'placeholder'

def get_notifications(token):
    '''
    <Return the user's most recent 20 notifications, ordered from most recent to least recent.>

    Arguments:
        auth_user_id (integer)  - user_id assigned to the user when creating account.

    Exceptions:
        AccessError - Occurs when auth_user_id is not valid

    Return Value:
        Returns a python dictionary containing a list of python dictionaries which details
        the notification message and which DM/Channel it came from.
        Look like this:
        {
            'notifications': [
                {
                    'channel_id': (integer),
                    'dm_id': (integer),
                    'notification_message': (string)
                }, 
                ...
            ]
        }
    '''
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    store = data_store.get()
    users = store['users']
    ### we only want 20 notifications.
    notifications = users[auth_user_id - 1]['notifications']
    notifications = notifications[:20] if len(notifications) >= 20 else notifications
    data_store.set(store)
    
    return {
        'notifications': notifications
    }    
    