'''
12.3.22

Contains tests for channel join v2.

Luis Vicente De La Paz Reyes (z5206766)
'''

import pytest
import requests
import json
from src import config

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"


def test_channel_join_basic():
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    response = requests.post(config.url + 'auth/register/v2', json = {'email': 'dummy@hotmail.com', 'password': 'pass123', 'name_first': 'test', 'name_last': 'dummy'})
    token = response.json()['token']
    user = response.json()['auth_user_id']
    response = requests.post(config.url + 'channels/create/v2', json = {'token': token, 'name': 'channel 1', 'is_public': True})
    channel_id = response.json()['channel_id']

    response = requests.post(config.url + 'auth/register/v2', json = {'email': 'dummy2@hotmail.com', 'password': 'pass123', 'name_first': 'test2', 'name_last': 'dummy2'})
    token = response.json()['token']
    user = response.json()['auth_user_id']

    requests.post(config.url + 'channel/join/v2', json = {'token':token, 'channel_id': channel_id})

    details_resp = requests.get(config.url + 'channel/details/v2', params = {'token':token, 'channel_id': channel_id}).json()

    assert user in [user['u_id'] for user in details_resp['all_members']]

def test_join_input_error_invalid_channel():
    '''tests for status code 400 (input error) - invalid channel.'''
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    #dummy user
    response = requests.post(config.url + 'auth/register/v2', json = {
        'email': 'dummy@hotmail.com',
        'password': 'pass123',
        'name_first': 'test',
        'name_last': 'dummy'})
    token = response.json()['token']

    #dummy invalid channel id.
    channel_id = {'channel_id' : 10000}

    #request to post channel join using details
    response = requests.post(config.url + 'channel/join/v2', json = {'token':token, 'channel_id': channel_id})

    assert response.status_code == 400

def test_join_input_error_user():
    '''tests for status code 400 (input error) - user already a member.'''
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    #dummy user
    response = requests.post(config.url + 'auth/register/v2', json = {'email': 'dummy@hotmail.com', 'password': 'pass123', 'name_first': 'test', 'name_last': 'dummy'})
    token = response.json()['token']

    #dummy created channel (user should be member since they create it)
    response = requests.post(config.url + 'channels/create/v2', json = {'token': token, 'name': 'channel 1', 'is_public': True})
    channel_id = response.json()['channel_id']

    #request to post channel join using details
    response = requests.post(config.url + 'channel/join/v2', json = {'token':token, 'channel_id': channel_id})

    assert response.status_code == 400

def test_join_access_error():
    ''' Tests for AccessError (channel id is private and user is not channel member or global owner)'''
    clear_request = requests.delete(f'{BASE_URL}/clear/v1')
    assert clear_request.status_code == 200
    response = requests.post(config.url + 'auth/register/v2', json = {'email': 'dummy@hotmail.com', 'password': 'pass123', 'name_first': 'test', 'name_last': 'dummy'})
    token = response.json()['token']

    response = requests.post(config.url + 'channels/create/v2', json = {'token': token, 'name': 'channel 1', 'is_public': False})
    channel_id = response.json()['channel_id']

    response = requests.post(config.url + 'auth/register/v2', json = {'email': 'dummy2@hotmail.com', 'password': 'pass123', 'name_first': 'test2', 'name_last': 'dummy2'})
    token = response.json()['token']

    response = requests.post(config.url + 'channel/join/v2', json = {'token':token, 'channel_id': channel_id})

    assert response.status_code == 403
    pass