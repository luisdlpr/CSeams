'''
    A bunch of tests for notifications/get/v1
    Coded up by Westley Lo
'''

from email import message
import requests
from src.config import url
BASE_URL = url

'''
    Bucket_list

    # notifications when recated message
    
    # twenty one notifications, only twenty of the most recent ones get printed.
    # join a channel and a dm, notifications/get, leave channel, notifications/get, leave dm, notifications/get

'''

def test_notifications_add_to_channel():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()   
    
    channel1_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "channel1",
        'is_public': True
        }
    )
    assert  channel1_details.status_code == 200
    channel1_details =  channel1_details.json()

    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        'token': h_smith_details['token']
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == []

    requests.post(f"{BASE_URL}/channel/invite/v2", json={
        'token': e_luxa_details['token'],
        'channel_id': channel1_details["channel_id"],
        'u_id': h_smith_details['auth_user_id']
    })
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [{
        'channel_id': channel1_details['channel_id'],
        'dm_id': -1,
        'notification_message': "emilyluxa added you to channel1"
    }]
    
def test_notifications_add_to_dm():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()   
    
    dm1_details = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": e_luxa_details['token'],
        "u_ids": [h_smith_details['auth_user_id']]
    })
    assert dm1_details.status_code == 200
    dm1_details = dm1_details.json()
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [{
        'channel_id': -1,
        'dm_id': dm1_details['dm_id'],
        'notification_message': "emilyluxa added you to emilyluxa, haydensmith"
    }]
    
def test_notifications_tagged_channel():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()   
    
    channel1_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "channel1",
        'is_public': True
        }
    )
    assert  channel1_details.status_code == 200
    channel1_details =  channel1_details.json()
    
    requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': h_smith_details['token'],
        'channel_id': channel1_details['channel_id']
    })
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == []
    
    #### user 1 tags user 2 #####
    send_request_details_details = requests.post(f"{BASE_URL}/message/send/v1", json={
        'token': e_luxa_details['token'],
        'channel_id': channel1_details['channel_id'],
        'message': "Hi there, your handle name should be @haydensmith"
    })
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [{
        'channel_id': channel1_details['channel_id'],
        'dm_id': -1,
        'notification_message': "emilyluxa tagged you in channel1: Hi there, your handl"
    }]
    
    #### message/edit
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": e_luxa_details['token'],
        "message_id": m_id['message_id'],
        "message": "edited @haydensmith"
    })
    assert edit_request.status_code == 200
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [
        {
            'channel_id': channel1_details['channel_id'],
            'dm_id': -1,
            'notification_message': "emilyluxa tagged you in channel1: edited @haydensmith"    
        },
        {
            'channel_id': channel1_details['channel_id'],
            'dm_id': -1,
            'notification_message': "emilyluxa tagged you in channel1: Hi there, your handl"
        }
    ]
    
    
    
def test_notifications_tagged_dm():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()   
    
    dm1_details = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": e_luxa_details['token'],
        "u_ids": [h_smith_details['auth_user_id']]
    })
    assert dm1_details.status_code == 200
    dm1_details = dm1_details.json()
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [{
        'channel_id': -1,
        'dm_id': dm1_details['dm_id'],
        'notification_message': "emilyluxa added you to emilyluxa, haydensmith"
    }]
    
    #### user 1 tags user 2 #####
    send_request_details_details = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        'token': e_luxa_details['token'],
        'dm_id': dm1_details['dm_id'],
        'message': "Hi there, your handle name should be @haydensmith"
    })
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [
        {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa tagged you in emilyluxa, haydensmith: Hi there, your handl"
        },
        {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa added you to emilyluxa, haydensmith"
        }
    ]
    
    #### message/edit
    edit_request = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": e_luxa_details['token'],
        "message_id": m_id['message_id'],
        "message": "edited @haydensmith"
    })
    assert edit_request.status_code == 200
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [
        {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa tagged you in emilyluxa, haydensmith: edited @haydensmith"
        },
        {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa tagged you in emilyluxa, haydensmith: Hi there, your handl"
        },
        {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa added you to emilyluxa, haydensmith"
        }
    ]
    

def test_notifications_reacted_message_channel():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()   
    
    channel1_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "channel1",
        'is_public': True
        }
    )
    assert  channel1_details.status_code == 200
    channel1_details =  channel1_details.json()
    
    requests.post(f"{BASE_URL}/channel/join/v2", json = {
        'token': h_smith_details['token'],
        'channel_id': channel1_details['channel_id']
    })
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == []
    
    #### user 2 send message ###
    send_request_details_details = requests.post(f"{BASE_URL}/message/send/v1", json={
        'token': h_smith_details['token'],
        'channel_id': channel1_details['channel_id'],
        'message': "I made a message here, hi"
    })
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    #### user 1 react to it ###
    message_react = requests.post(f"{BASE_URL}/message/react/v1", json={
        "token": e_luxa_details['token'],
        "message_id": m_id['message_id'],
        "react_id": 1
    })
    assert message_react.status_code == 200
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [{
        'channel_id': channel1_details['channel_id'],
        'dm_id': -1,
        'notification_message': "emilyluxa reacted to your message in channel1"
    }]

def test_notifications_reacted_message_dm():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()   
    
    dm1_details = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": e_luxa_details['token'],
        "u_ids": [h_smith_details['auth_user_id']]
    })
    assert dm1_details.status_code == 200
    dm1_details = dm1_details.json()
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [{
        'channel_id': -1,
        'dm_id': dm1_details['dm_id'],
        'notification_message': "emilyluxa added you to emilyluxa, haydensmith"
    }]
    
    #### user 2 send message ###
    send_request_details_details = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        'token': h_smith_details['token'],
        'dm_id': dm1_details['dm_id'],
        'message': "I made a message here, hi"
    })
    assert send_request_details_details.status_code == 200
    m_id = send_request_details_details.json()
    
    #### user 1 react to it ###
    message_react = requests.post(f"{BASE_URL}/message/react/v1", json={
        "token": e_luxa_details['token'],
        "message_id": m_id['message_id'],
        "react_id": 1
    })
    assert message_react.status_code == 200
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [
        {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa reacted to your message in emilyluxa, haydensmith"
        },
        {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa added you to emilyluxa, haydensmith"
        }
    ]
    
def test_21_notifications():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()   
    
    channel1_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "channel1",
        'is_public': True
        }
    )
    assert  channel1_details.status_code == 200
    channel1_details =  channel1_details.json()

    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == []

    requests.post(f"{BASE_URL}/channel/invite/v2", json={
        'token': e_luxa_details['token'],
        'channel_id': channel1_details["channel_id"],
        'u_id': h_smith_details['auth_user_id']
    })
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [{
        'channel_id': channel1_details['channel_id'],
        'dm_id': -1,
        'notification_message': "emilyluxa added you to channel1"
    }]
    
    #### Alternate between reacts and taggs for 10 messages
    notif_list = []
    for count in range(5):
        #### user 2 send message ###
        send_request_details_details = requests.post(f"{BASE_URL}/message/send/v1", json={
            'token': h_smith_details['token'],
            'channel_id': channel1_details['channel_id'],
            'message': f"I made a message {count}"
        })
        assert send_request_details_details.status_code == 200
        m_id = send_request_details_details.json()
        
        #### user 1 react to it ###
        message_react = requests.post(f"{BASE_URL}/message/react/v1", json={
            "token": e_luxa_details['token'],
            "message_id": m_id['message_id'],
            "react_id": 1
        })
        assert message_react.status_code == 200
        notif_list.insert(0, {
            'channel_id': channel1_details['channel_id'],
            'dm_id': -1,
            'notification_message': 'emilyluxa reacted to your message in channel1'
        })
        
        tagged = requests.post(f"{BASE_URL}/message/send/v1", json={
            'token': e_luxa_details['token'],
            'channel_id': channel1_details['channel_id'],
            'message': "Hi there, your handle name should be @haydensmith"
        })
        assert tagged.status_code == 200
        m_id = tagged.json()
        
        notif_list.insert(0, {
            'channel_id': channel1_details['channel_id'],
            'dm_id': -1,
            'notification_message': 'emilyluxa tagged you in channel1: Hi there, your handl'
        })
        
    #### user 1 tags user 2 in 10 messages.
    for count in range(10):
        #### user 2 send message ###
        send_request_details_details = requests.post(f"{BASE_URL}/message/send/v1", json={
            'token': h_smith_details['token'],
            'channel_id': channel1_details['channel_id'],
            'message': f"I made a message {count}"
        })
        assert send_request_details_details.status_code == 200
        m_id = send_request_details_details.json()
        
        #### user 1 react to it ###
        message_react = requests.post(f"{BASE_URL}/message/react/v1", json={
            "token": e_luxa_details['token'],
            "message_id": m_id['message_id'],
            "react_id": 1
        })
        assert message_react.status_code == 200
        notif_list.insert(0, {
            'channel_id': channel1_details['channel_id'],
            'dm_id': -1,
            'notification_message': 'emilyluxa reacted to your message in channel1'
        })

    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == notif_list
    
    requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": h_smith_details['token'],
        "channel_id": channel1_details["channel_id"],
    })
    
    ### user leaves channel, should become empty.
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == notif_list





def test_notifications_channels_and_dm():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    e_luxa_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'e.luxa@student.unsw.edu.au',
        'password': 'password1',
        'name_first': 'emily',
        'name_last': 'luxa',
    })
    assert e_luxa_details.status_code == 200
    e_luxa_details = e_luxa_details.json()
    
    h_smith_details = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'hayden.smith@unsw.edu.au',
        'password': 'password',
        'name_first': 'hayden',
        'name_last': 'smith',
    })
    assert h_smith_details.status_code == 200
    h_smith_details = h_smith_details.json()   
    
    channel1_details = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': e_luxa_details['token'], 
        'name': "channel1",
        'is_public': True
        }
    )
    assert  channel1_details.status_code == 200
    channel1_details =  channel1_details.json()
    
    dm1_details = requests.post(f'{BASE_URL}/dm/create/v1', json={
        "token": e_luxa_details['token'],
        "u_ids": [h_smith_details['auth_user_id']]
    })
    assert dm1_details.status_code == 200
    dm1_details = dm1_details.json()
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [{
        'channel_id': -1,
        'dm_id': dm1_details['dm_id'],
        'notification_message': "emilyluxa added you to emilyluxa, haydensmith"
    }]
    
    requests.post(f"{BASE_URL}/channel/invite/v2", json={
        'token': e_luxa_details['token'],
        'channel_id': channel1_details["channel_id"],
        'u_id': h_smith_details['auth_user_id']
    })
    
    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": h_smith_details['token'],
    })
    assert notif.status_code == 200
    notif = notif.json()
    assert notif['notifications'] == [
        {
            'channel_id': channel1_details['channel_id'],
            'dm_id': -1,
            'notification_message': "emilyluxa added you to channel1"
        },
        {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa added you to emilyluxa, haydensmith"
        }
    ]
    
    notif_list = [
        {
            'channel_id': channel1_details['channel_id'],
            'dm_id': -1,
            'notification_message': "emilyluxa added you to channel1"
        },
        {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa added you to emilyluxa, haydensmith"
        }
    ]
    
    for count in range(9):
        dm_tag = requests.post(f"{BASE_URL}/message/senddm/v1", json={
            'token': e_luxa_details['token'],
            'dm_id': dm1_details['dm_id'],
            'message': f"I made @haydensmith {count}"
        })
        assert dm_tag.status_code == 200
        # m_id = dm_tag.json()
        notif_list.insert(0, {
            'channel_id': -1,
            'dm_id': dm1_details['dm_id'],
            'notification_message': "emilyluxa tagged you in emilyluxa, haydensmith: I made @haydensmith "
        })
        channel_tag = requests.post(f"{BASE_URL}/message/send/v1", json={
            'token': e_luxa_details['token'],
            'channel_id': channel1_details['channel_id'],
            'message': "I here made @haydensmith"
        })
        
        assert channel_tag.status_code == 200
        #m_id = channel_tag.json()
        notif_list.insert(0, {
            'channel_id': channel1_details['channel_id'],
            'dm_id': -1,
            'notification_message': "emilyluxa tagged you in channel1: I here made @haydens"
        })

    notif = requests.get(f"{BASE_URL}/notifications/get/v1", params={
            "token": h_smith_details['token'],
        })
    assert notif.status_code == 200
    assert notif.json()['notifications'] == notif_list
    