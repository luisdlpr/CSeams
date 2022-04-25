'''
All functions in this file were implemented by
z5206766 Luis Reyes
UNSW comp1531 22t1
'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.message import message_send_v1
from src.helpers import check_valid_token
import datetime
import threading
import time, jwt

SECRET = 'placeholder'

def standup_start_v1(token, channel_id, length):
    '''
    Within the given channel, start a period of 'length' seconds for standups 
    to be sent.  Upon completion of timer if messages were sent in the queue,
    send the message, otherwise send no message.

    Arguments:
        auth_user_id    - integer (u_id of the authorised user)
        channel_id      - integer (ID of the channel to which a new user is 
                            invited)
        length          - integer (delay in seconds between standup start and 
                            send)

    Exceptions:
        InputError - Occurs when:
            Channel_id does not refer to a valid channel
            Length is a negative integer
            Active standup is currently running in the channel

        AccessError - Occurs when:
            channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns { time_finish } - integer (unix timestamp)
    '''
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    data = data_store.get()
    channels = data['channels']

    # channel_id does not refer to a valid channel InputError
    if channel_id not in [channel['channel_id'] for channel in channels]:
        raise InputError(description="Channel id not valid.")

    # length is negative - raise InputError
    if (length < 0):
        raise InputError(description="length must be a positive integer")

    # variable with desired channel details
    desiredchannel = data['channels'][channel_id - 1]
    
    # check if standup is ongoing
    if desiredchannel['standup']['is_active'] == True:
        raise InputError(description="A standup is already ongoing")

    # channel_id is valid and the authorised user is not a member of the channel
    if auth_user_id not in [member['u_id'] for member in desiredchannel['all_members']]:
        raise AccessError(description="You are not even a member of the channel")

    # if everything is fine start standup
    # set channel to active standup
    data['channels'][channel_id - 1]['standup']['is_active'] = True
    data['channels'][channel_id - 1]['standup']['host'] = auth_user_id
    data['channels'][channel_id - 1]['standup']['time_finish'] = \
        time.mktime(datetime.datetime.now().timetuple()) + length
    data_store.set(data)

    # after specified time execute function to finish standup
    t = threading.Timer(length, finishStandup, args = [auth_user_id, channel_id])
    t.start()

    # return expected finish time
    return { "time_finish": data['channels'][channel_id - 1]['standup']['time_finish'] }

def finishStandup(auth_user_id, channel_id):
    '''
    Execute operations on standup finish time including sending data in buffer
    as channel message if any exists and returning standup active status to
    false.

    Arguments:
        auth_user_id    - integer (u_id of the authorised user)
        channel_id      - integer (ID of the channel to which a new user is 
                            invited)

    Exceptions:
        if user is removed during standup duration, token error will be raised
        and message will not be sent.

    Return Value:
        None.
    '''

    # check datastore for any messages in buffer
    data = data_store.get()
    
    desiredchannel = data['channels'][channel_id - 1]
    desireduser = data['users'][auth_user_id - 1]
    token = desireduser['token'][0]

    users = list(desiredchannel['standup'].keys())
    messages = list(desiredchannel['standup'].values())
    
    # if messages exist, use message send to print a single message containing
    # all.
    if len(users) > 3:
        message = ""
        for i in range(3, len(users)):
            message = message + str(users[i]) + ": " + str(messages[i]) + "\n"
        message_send_v1(token, channel_id, message)
    
    # reset standup status to false in channel and delete data in buffer
    data['channels'][channel_id - 1]['standup'] = { 
        'is_active': False,
        'time_finish': None 
    }

    # send updates to database and return
    data_store.set(data)
    return

def standup_active_v1(token, channel_id):
    '''
    Within the given channel, return wether a standup is active in it and what
    time it finishes.  otherwise time_finish returns None

    Arguments:
        auth_user_id    - integer (u_id of the authorised user)
        channel_id      - integer (ID of the channel to which a new user is 
                            invited)

    Exceptions:
        InputError - Occurs when:
            Channel_id does not refer to a valid channel

        AccessError - Occurs when:
            channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns 
        { 
            "is_active": bool,
            "time_finish": integer (unix timestamp) or None     
        }
    '''
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    data = data_store.get()
    channels = data['channels']

    # channel_id does not refer to a valid channel InputError
    if channel_id not in [channel['channel_id'] for channel in channels]:
        raise InputError(description="Channel id not valid.")

    desiredchannel = data['channels'][channel_id - 1]

    # channel_id is valid and the authorised user is not a member of the channel
    if auth_user_id not in [member['u_id'] for member in desiredchannel['all_members']]:
        raise AccessError(description="You are not even a member of the channel")

    # otherwise return details stored in 'standup'
    return {
        'is_active': desiredchannel['standup']['is_active'],
        'time_finish': desiredchannel['standup']['time_finish']
    }

def standup_send_v1(token, channel_id, message):
    '''
    Within the given channel, sends a message to standup buffer assuming standup
    is currently active.

    Arguments:
        auth_user_id    - integer (u_id of the authorised user)
        channel_id      - integer (ID of the channel to which a new user is 
                            invited)
        message         - string

    Exceptions:
        InputError - Occurs when:
            Channel_id does not refer to a valid channel
            message length is > 1000 chars
            the channel standup is not currently active

        AccessError - Occurs when:
            channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns {}
    '''
    check_valid_token(token)
    auth_user_id = jwt.decode(token, SECRET, algorithms = ['HS256'])['auth_user_id']
    data = data_store.get()
    channels = data['channels']

    # channel_id does not refer to a valid channel InputError
    if channel_id not in [channel['channel_id'] for channel in channels]:
        raise InputError(description="Channel id not valid.")

    if len(message) > 1000:
        raise InputError(description="Message too long (must be < 1000 characters)")

    desiredchannel = data['channels'][channel_id - 1]

    if desiredchannel['standup']['is_active'] == False:
        raise InputError(description="A standup is not currently active")

    # channel_id is valid and the authorised user is not a member of the channel
    if auth_user_id not in [member['u_id'] for member in desiredchannel['all_members']]:
        raise AccessError(description="You are not even a member of the channel")

    desireduser = data['users'][auth_user_id - 1]
    handle = desireduser['handle_str']

    data['channels'][channel_id - 1]['standup'][handle] = message

    data_store.set(data)

    return {}