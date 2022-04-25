'''
Created: 12.3.22
Last Updated: 15.3.22

Contains tests for channel join v2.
Cannot be currently tested until at least auth register.

Luis Vicente De La Paz Reyes (z5206766)
'''

import pytest
import requests
import json
from src import config
from src import channel

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"

# def test_details_input_error_invalid_channel():
#     '''tests for status code 400 (input error) - invalid channel.'''
    
#     # dummy user
#     response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
#         'email': 'dummy@hotmail.com',
#         'password': 'pass123',
#         'name_first': 'test',
#         'name_last': 'dummy'})

#     token = response.json()['token']
    
#     # dummy invalid channel id.
#     channel_id = {'channel_id' : 10000}
    
#     # request to post channel join using details
#     response = requests.post(f"{BASE_URL}/channel/details/v2", json = {
#         "token": token,
#         channel_id})
    
#     assert response.status_code == 400

# def test_details_access_error():
#     ''' Tests for AccessError (channel id is valid but user is not channel member or global owner)'''

#     response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
#       'email': 'dummy@hotmail.com',
#       'password': 'pass123',
#       'name_first': 'test',
#       'name_last': 'dummy'})
#     token = response.json()['token']

#     response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
#       'token': token,
#       'name': 'channel 1',
#       'is_public': False})
#     channel_id = response.json()['channel_id']

#     response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
#       'email': 'dummy2@hotmail.com',
#       'password': 'pass123',
#       'name_first': 'test2',
#       'name_last': 'dummy2'})
#     token = response.json()['token']

#     response = requests.post(f"{BASE_URL}/channel/details/v2", json = {token, channel_id})

#     assert response.status_code == 403    