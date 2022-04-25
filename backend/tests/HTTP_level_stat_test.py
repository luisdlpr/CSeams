'''
    A bunch of tests for user/stats/v1 and users/stats/v1
    Coded up by Westley Lo
'''
import requests, random
from src.config import url
import datetime
BASE_URL = url

'''
    Bucket List:
    
    # 2 users, user 2 print users/stats/v1 and user/stats/v1, admin/remove user 2 , user2 print users/stats/v1 and user/stats/v1, throw AccessError.
'''

def generate_string():
    MIN_LIMIT = 32    # from 'a' ascii value to
    MAX_LIMIT = 126   # '~' ascii value
    
    random_string = ''
 
    for _ in range(20):
        random_integer = random.randint(MIN_LIMIT, MAX_LIMIT)
    # Keep appending random characters using chr(x)
        random_string += (chr(random_integer))
    
    return random_string

def send_message_request(token, channel_id, message):
    '''
    Makes a /message/send/v1 POST request then returns the response

    Arguments:
        Takes in a valid user token, channel_id (refering to a valid channel) and
        a message (string)
    Return Value:
        {'message_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/message/send/v1', json = {
        'token': token,
        'channel_id': channel_id,
        'message': message
        }
    )

def message_send_dm_request(token, dm_id, message):
    '''
    Makes a /message/senddm/v1 POST request then returns the response

    Arguments:
        Takes in a valid user token, dm_id (refering to a valid dm) and
        a message (string)
    Return Value:
        {'dm_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/message/senddm/v1', json = {
        'token': token,
        'dm_id': dm_id,
        'message': message
        }
    )

def register_user_request(email, password, name_first, name_last):
    '''
    BLACKBOX
    Makes a /auth/register/v2 POST request then returns the response.
    
    Arguements:
        Takes in user details email, password, name_first and name_last.
    Return Value:
        {'token', 'auth_user_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/auth/register/v2', json = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
        }
    )

def utc_now():
    '''
        Returns the unix time_stamp now.
        
        Arguments:
            none
        
        Return Value:
            - unix time_stamp (int)
    '''
    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    return int(utc_time.timestamp())
    
def workspace_stats_request(token):
    '''
    BLACKBOX
    Makes a users/stats/v1 GET request then returns the response.
    
    Arguements:
        Takes in a token.
    Return Value:
        {
            'workspace_stats': {
                channels_exist: {num_channels_exist, time_stamp}, 
                dms_exist: {num_dms_exist, time_stamp},
                messages_exist: {num_messages_exist, time_stamp}, 
                utilization_rate: number
            }
        }
    Return Type:
        Response object
    '''
    return requests.get(f"{BASE_URL}/users/stats/v1", params={
        'token': token
    })
    
def user_stats_request(token):
    '''
    BLACKBOX
    Makes a user/stats/v1 GET request then returns the response.
    
    Arguements:
        Takes in a token.
    Return Value:
        {
            'user_stats':  {
                channels_joined: {num_channels_joined, time_stamp},
                dms_joined: {num_dms_joined, time_stamp}, 
                messages_sent: {num_messages_sent, time_stamp}, 
                involvement_rate 
            }
        }
    Return Type:
        Response object
    '''
    return requests.get(f"{BASE_URL}/user/stats/v1", params={
        'token': token
    })

def channels_create_request(token, name, is_public):
    '''
    BLACKBOX
    Makes a /channels/create/v2 POST request then returns the response

    Arguments:
        Takes in a valid user token, name (for channel's name) and privacy status
        is_public.
    Return Value:
        {'channle_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/channels/create/v2', json = {
        'token': token,
        'name': name,
        'is_public': is_public
        }
    )

def dm_create_request(token, u_ids):
    '''
    BLACKBOX
    Makes a /dm/create/v1 POST request then returns the response

    Arguments:
        Takes in a valid user token, and a list of u_ids
    Return Value:
        {'dm_id'}
    Return Type:
        Response object
    '''
    return requests.post(f'{BASE_URL}/dm/create/v1', json = {
        'token': token,
        'u_ids': u_ids
        }
    )

######### The actual tests ###########
def test_stats_no_channels_no_dms():
    requests.delete(f"{BASE_URL}/clear/v1")
    expected_time_stamp = utc_now()
    e_luxa_details = register_user_request('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa')
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 0
    assert workspace_stats['channels_exist'][0]['num_channels_exist'] == 0
    assert abs(workspace_stats['channels_exist'][0]['time_stamp'] - expected_time_stamp) <= 2
    assert workspace_stats['dms_exist'][0]['num_dms_exist'] == 0
    assert abs(workspace_stats['dms_exist'][0]['time_stamp'] - expected_time_stamp) <= 2
    assert workspace_stats['messages_exist'][0]['num_messages_exist'] == 0
    assert abs(workspace_stats['messages_exist'][0]['time_stamp'] - expected_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 0
    assert user_stats['channels_joined'][0]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][0]['time_stamp'] - expected_time_stamp) <= 2
    assert user_stats['dms_joined'][0]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][0]['time_stamp'] - expected_time_stamp) <= 2
    assert user_stats['messages_sent'][0]['num_messages_sent'] == 0
    assert abs(user_stats['messages_sent'][0]['time_stamp'] - expected_time_stamp) <= 2
 
def test_stats_some_channels_dms():
    
    ''' 1 user, make 1 channel, print users/stats/v1 and user/stats/v1, make 1 dm print users/stats/v1 and user/stats/v1,
    make 4 more channel, print users/stats/v1 and user/stats/v1, make 4 more dms, print users/stats/v1 and user/stats/v1
    remove 1 dm, print users/stats/v1 and user/stats/v1.'''
    requests.delete(f"{BASE_URL}/clear/v1")
    creation_time_stamp = utc_now()
    e_luxa_details = register_user_request('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa')
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    channel_time_stamp = utc_now()
    channels_create_request(e_luxa_details['token'], "channel1", True).json()
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 0
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - creation_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 0
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - creation_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - creation_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 0
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - creation_time_stamp) <= 2
    
    # make a dm here
    dm_time_stamp = utc_now()
    dm1_deets = dm_create_request(e_luxa_details['token'], []).json()
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - dm_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 0
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - creation_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - dm_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 0
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - creation_time_stamp) <= 2
    
    #### make four more channels
    for count in range(4):
        channel_time_stamp = utc_now()
        channels_create_request(e_luxa_details['token'], f"channel{count}", True)
        
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 5
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - dm_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 0
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - creation_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 5
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - dm_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 0
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - creation_time_stamp) <= 2

    ### make 4 more dms
    for count in range(4):
        dm_time_stamp = utc_now()
        dm_create_request(e_luxa_details['token'], [])
        
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 5
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 5
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - dm_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 0
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - creation_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 5
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 5
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - dm_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 0
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - creation_time_stamp) <= 2
    
    '''remove 1 dm, print users/stats/v1 and user/stats/v1.'''
    dm_time_stamp = utc_now()
    requests.delete(f'{BASE_URL}/dm/remove/v1', json={
        'token': e_luxa_details['token'],
        'dm_id': dm1_deets['dm_id']
    })
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 5
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 4
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - dm_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 0
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - creation_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 5
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 4
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - dm_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 0
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - creation_time_stamp) <= 2
   
def test_stats_multiple_users():
    '''# 3 users, 1 (creator) and 2 get into a Channel, 2 (creator) and 3 get into a dm, print out user/stats/v1 and users/stats/v1 for each, 
    User 2 leave channel and User 3 leave dm, print users/stats/v1 (unchanged) and user/stats/v1 again.
    use dm/remove, print users/stats/v1 and user/stats/v1 again (unchanged).'''
    requests.delete(f"{BASE_URL}/clear/v1")
    
    ### three users
    e_luxa_time_stamp = utc_now()
    e_luxa_details = register_user_request('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa').json()
    
    h_smith_time_stamp = utc_now()
    h_smith_details = register_user_request('hayden.smith@unsw.edu.au', 'password', 'hayden', 'smith').json()
    
    j_renzella_time_stamp = utc_now()
    j_renzella_details = register_user_request('jake.renzella@unsw.edu.au', 'password', 'jake', 'renzella').json()


    ### user 1 and 2 join channel
    channel_time_stamp = utc_now()
    channel1_deets = channels_create_request(e_luxa_details['token'], "channel1", True).json()
    
    user_stats = user_stats_request(h_smith_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 0
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - h_smith_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - h_smith_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 0
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - h_smith_time_stamp) <= 2
    
    channel_join_time_stamp = utc_now()
    requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': h_smith_details['token'],
        'channel_id': channel1_deets['channel_id']
    })
    
    ### user 2 and 3 join dm
    dm_time_stamp = utc_now()
    dm1_deets = dm_create_request(h_smith_details['token'], [j_renzella_details['auth_user_id']]).json()
    
    ### print out the stats
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - dm_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1/2
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    
    user_stats = user_stats_request(h_smith_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_join_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - dm_time_stamp) <= 2
    
    user_stats = user_stats_request(j_renzella_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1/2
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - j_renzella_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - dm_time_stamp) <= 2
    
    '''User 2 leave channel and User 3 leave dm, print users/stats/v1 (changed) and user/stats/v1 again.'''
    channel_leave_time_stamp = utc_now()
    requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": h_smith_details['token'],
        "channel_id": channel1_deets['channel_id'],
    })
    
    dm_leave_time_stamp = utc_now()
    requests.post(f'{BASE_URL}/dm/leave/v1', json={
        'token': j_renzella_details['token'],
        'dm_id': dm1_deets['dm_id']
    })
    
    ### see if the stats updated
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 2/3
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - dm_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1/2
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    
    user_stats = user_stats_request(h_smith_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1/2
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_leave_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - dm_time_stamp) <= 2
    
    user_stats = user_stats_request(j_renzella_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 0
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - j_renzella_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - dm_leave_time_stamp) <= 2

def test_stats_messages():
    '''
        # 1 user, make channel, print out user/stats/v1 and users/stats/v1, 
    send 50 messages into channel, print out user/stats/v1 (changed) and users/stats/v1 (changed)
    delete some messages, print out user/stats/v1 (unchanged) and users/stats/v1 (changed)
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    
    ### three users
    # 1 user, make channel, print out user/stats/v1 and users/stats/v1, 
    e_luxa_time_stamp = utc_now()
    e_luxa_details = register_user_request('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa').json()
    channel_create_time_stamp = utc_now()
    channel1_deets = channels_create_request(e_luxa_details['token'], "channel1", True).json()
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 0
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 0
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 0
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    
    
    
    ### send 50 messages into channel, print out user/stats/v1 (changed) and users/stats/v1 (changed)
    message_time_stamp = utc_now()
    message_list = []
    for message_count in range(51):
        message_list.append(generate_string() + '--|' +  str(message_count))
    
    message_id_list = []
    for message in message_list:
        message_time_stamp = utc_now()
        message_details = send_message_request(e_luxa_details['token'], channel1_deets['channel_id'], message)
        assert message_details.status_code == 200
        message_id_list.append(message_details.json()['message_id'])

    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 0
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 51
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 51
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    
    #### edit some messages, nothing should change. ####
    requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": e_luxa_details['token'],
        "message_id": message_id_list[0],
        "message": "Real new message"
    })
    requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": e_luxa_details['token'],
        "message_id": message_id_list[1],
        "message": "Real new message"
    })
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 0
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 51
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 51
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    
    
    #### delete some messages via edit and remove, print out user/stats/v1 (unchanged) and users/stats/v1 (changed)"""
    requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": e_luxa_details['token'],
        "message_id": message_id_list[0],
        "message": ""
    })
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 0
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert len(workspace_stats['messages_exist']) == 53
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 50
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 51
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": e_luxa_details['token'],
        "message_id": message_id_list[5],
    })
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 1
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 0
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert len(workspace_stats['messages_exist']) == 54
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 49
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 1
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 0
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 51
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    
def test_stats_messages_dm():
    '''
        # 1 user, make dm, print out user/stats/v1 and users/stats/v1, 
    send 50 messages into dm, print out user/stats/v1 (changed) and users/stats/v1 (changed)
    delete some messages, print out user/stats/v1 (unchanged) and users/stats/v1 (changed)
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    
    ### three users
    # 1 user, make channel, print out user/stats/v1 and users/stats/v1, 
    e_luxa_time_stamp = utc_now()
    e_luxa_details = register_user_request('e.luxa@student.unsw.edu.au', 'password', 'emily', 'luxa').json()
    channel_create_time_stamp = utc_now()
    dm1_deets = dm_create_request(e_luxa_details['token'], []).json()
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 0
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 0
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 0
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    
    
    
    ### send 50 messages into dm, print out user/stats/v1 (changed) and users/stats/v1 (changed)
    message_time_stamp = utc_now()
    message_list = []
    for message_count in range(51):
        message_list.append(generate_string() + '--|' +  str(message_count))
    
    message_id_list = []
    for message in message_list:
        message_time_stamp = utc_now()
        message_details = message_send_dm_request(e_luxa_details['token'], dm1_deets['dm_id'], message)
        assert message_details.status_code == 200
        message_id_list.append(message_details.json()['message_id'])

    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 0
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 51
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 51
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    
    #### edit some messages, nothing should change. ####
    requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": e_luxa_details['token'],
        "message_id": message_id_list[0],
        "message": "Real new message"
    })
    requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": e_luxa_details['token'],
        "message_id": message_id_list[1],
        "message": "Real new message"
    })
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 0
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 51
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 51
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    
    
    #### delete some messages via edit and remove, print out user/stats/v1 (unchanged) and users/stats/v1 (changed)"""
    requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": e_luxa_details['token'],
        "message_id": message_id_list[0],
        "message": ""
    })
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 0
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert len(workspace_stats['messages_exist']) == 53
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 50
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 51
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": e_luxa_details['token'],
        "message_id": message_id_list[5],
    })
    
    workspace_stats = workspace_stats_request(e_luxa_details['token'])
    assert workspace_stats.status_code == 200
    workspace_stats = workspace_stats.json()['workspace_stats']
    
    assert workspace_stats['utilization_rate'] == 1
    assert workspace_stats['channels_exist'][-1]['num_channels_exist'] == 0
    assert abs(workspace_stats['channels_exist'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert workspace_stats['dms_exist'][-1]['num_dms_exist'] == 1
    assert abs(workspace_stats['dms_exist'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert len(workspace_stats['messages_exist']) == 54
    assert workspace_stats['messages_exist'][-1]['num_messages_exist'] == 49
    assert abs(workspace_stats['messages_exist'][-1]['time_stamp'] - message_time_stamp) <= 2
    
    user_stats = user_stats_request(e_luxa_details['token'])
    assert user_stats.status_code == 200
    user_stats = user_stats.json()['user_stats']

    assert user_stats['involvement_rate'] == 1
    assert user_stats['channels_joined'][-1]['num_channels_joined'] == 0
    assert abs(user_stats['channels_joined'][-1]['time_stamp'] - channel_create_time_stamp) <= 2
    assert user_stats['dms_joined'][-1]['num_dms_joined'] == 1
    assert abs(user_stats['dms_joined'][-1]['time_stamp'] - e_luxa_time_stamp) <= 2
    assert user_stats['messages_sent'][-1]['num_messages_sent'] == 51
    assert abs(user_stats['messages_sent'][-1]['time_stamp'] - message_time_stamp) <= 2