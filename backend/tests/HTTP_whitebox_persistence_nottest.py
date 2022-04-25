'''
25.3.22

Contains tests for http datastore persistence

Luis Vicente De La Paz Reyes (z5206766)
'''

import requests
from src import config
import pickle
from src.data_store import data_store
from src.helpers import hash

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"
SECRET = 'placeholder'

def test_admin_userpermissions_change_basic():
    '''
    Contains basic tests for channel_join_v1.  Tests for appropriate return type,
    ability to reuse email and handle, and removal from channels and dms list.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")

    data = pickle.load(open('datastore.p', 'rb'))
    data_store.set(data)
    assert data == {
        'users': [],
        'channels': [],
        'dms': []
    }

    response = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "testemail1@hotmail.com",
        "password": "pass123",
        "name_first": "Test",
        "name_last": "Dummy1"
    })
    token = response.json()['token']

    data = pickle.load(open('datastore.p', 'rb'))
    print(data)


    data = {
        'users': [],
        'channels': [],
        'dms': []
    }

    data = pickle.load(open('datastore.p', 'rb'))
    data_store.set(data)

    assert data == {
        'users': [
            {   
                'channels_joined': [],
                'dms_joined': [],
                'u_id': 1,
                'handle_str': 'testdummy1',
                'name_first': 'Test',
                'name_last': 'Dummy1',
                'email': 'testemail1@hotmail.com',
                'password': hash('pass123'),
                'permission_id': 1,
                'removed': False,
                'token': [token]
            }
        ],
        'channels': [],
        'dms': []
    }
