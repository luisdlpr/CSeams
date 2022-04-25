'''
Helper functions 
- session (make_new_session_id)
- token (make_token, decode_token, check_valid_token)
- password (hash)
- messages (make_message)
'''

import jwt
import hashlib, datetime 
from src.data_store import data_store
from src.config import url
from src.error import InputError, AccessError

SECRET = 'placeholder'
SESSIONS_TRACKER = 0
BASE_URL = url

def reset_sessions():
    '''
    resets session_id when clear_v1 is called
    '''
    global SESSIONS_TRACKER
    SESSIONS_TRACKER = 0

def make_new_session_id():
    '''
    generates a new session id
    '''
    global SESSIONS_TRACKER
    SESSIONS_TRACKER += 1

    return SESSIONS_TRACKER
    

def make_token(user_id, session_id):
    '''
    redundant with encode_token
    makes token from given u_id
    '''
    if session_id is None:
        session_id = make_new_session_id()

    token = jwt.encode({"auth_user_id": user_id, "session_id": session_id}, SECRET, algorithm ="HS256")
    return token

def decode_token(token):
    '''
    takes in token and decodes it
    '''
    try:
        decode = jwt.decode(token, SECRET, algorithms=["HS256"])
        return decode
    except (jwt.InvalidSignatureError) as error:
        raise AccessError(description='Token Invalid, wrong secret.') from error


def check_valid_token(token):
    '''
    takes in a token and returns whether it is valid or not (boolean)

    token is valid when:
    - auth_user_id is between 1 and len(users_list) (inclusive)
    - session_id is between 1 and SESSIONS_TRACKER (inclusive)

    '''
    store = data_store.get()
    users_list = store['users']
    max_u_id = len(users_list)

    token_data = decode_token(token)
    u_id = token_data["auth_user_id"]
    session_id = token_data["session_id"]

    if u_id < 0 or u_id > max_u_id:
        raise AccessError(description="Token Invalid")
    elif session_id < 0 or session_id > SESSIONS_TRACKER:
        raise AccessError(description="Token Invalid")

    is_valid = False
    for user in users_list:
        for tok in user['token']:
            if tok == token:
                is_valid = True

    if is_valid == False:
        raise AccessError(description="Token Invalid")

    # # check for correct secret
    # correct_tok = jwt.encode({"auth_user_id": u_id, "session_id": session_id}, 'placeholder', algorithm='HS256')
    # if correct_tok != token:
    #     return False
    return True



def hash(password):
    '''
    hashes a password using sha256
    '''
    return hashlib.sha256(password.encode()).hexdigest()


def utc_now():
    '''
        returns current unix timestamp.
    '''
    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    return utc_timestamp

def new_userstat_point(workspace_stats, user_stats, timestamp, channelchange=0, dmschange=0, messagechange=0):
    
        #Returns new user_stat datapoint.
    
    num_channels_joined = user_stats['channels_joined'][-1]['num_channels_joined'] + channelchange
    num_dms_joined = user_stats['dms_joined'][-1]['num_dms_joined'] + dmschange
    num_messages_sent = user_stats['messages_sent'][-1]['num_messages_sent'] + messagechange
    
    num_channels = workspace_stats['channels_exist'][-1]['num_channels_exist']
    num_dms = workspace_stats['dms_exist'][-1]['num_dms_exist']
    num_messages = workspace_stats['messages_exist'][-1]['num_messages_exist']
    numerator = num_channels_joined + num_dms_joined + num_messages_sent
    denominator = num_channels + num_dms + num_messages
    
    return {
        'channels_joined': [{'num_channels_joined': num_channels_joined,'time_stamp': timestamp}],
        'dms_joined': [{'num_dms_joined': num_dms_joined,'time_stamp': timestamp}],
        'messages_sent': [{'num_messages_sent': num_messages_sent,'time_stamp': timestamp}],
        'involvement_rate': 0 if denominator == 0 else numerator/denominator
    }
    
def new_workspace_point(store, timestamp, channelchange=0, dmschange=0, messagechange=0):
    
        #Returns new workspace datapoint
    
    workspace_stats = store['workspace_stats']
    num_channels = workspace_stats['channels_exist'][-1]['num_channels_exist'] + channelchange
    num_dms = workspace_stats['dms_exist'][-1]['num_dms_exist'] + dmschange
    num_messages = workspace_stats['messages_exist'][-1]['num_messages_exist'] + messagechange
    
    actual_users = [user for user in store['users'] if not user['removed']]
    actual_involved_users = [user for user in actual_users if ((len(user['channels_joined']) != 0 or len(user['dms_joined']) != 0))]
    
    return {
        'channels_exist': [{'num_channels_exist': num_channels, 'time_stamp':timestamp}], 
        'dms_exist': [{'num_dms_exist': num_dms, 'time_stamp': timestamp}], 
        'messages_exist': [{'num_messages_exist': num_messages, 'time_stamp':timestamp}], 
        'utilization_rate': len(actual_involved_users)/len(actual_users)
    }
