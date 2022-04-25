'''
Created: 16.3.22
Last update:

Contains tests for auth/register/v2. 

Luis Vicente De La Paz Reyes (z5206766)

modified by Amy Pham(z5359018)
'''

import pytest
import requests
import json
from src import config, helpers, user
import src.server
import jwt
from src.error import AccessError, InputError
'''
BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"  
'''
BASE_URL = config.url
COPY_SESS_TRACKER = 0

def test_clear_status_code():
    '''
    Basic test to check auth/register/v2 return values.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testemail@gmail.com",
    "password": "pass123",
    "name_first": "test",
    "name_last": "dummy"})
    print("output:", response.json())
    assert response.status_code == 200

    assert response.json() == {
        "token": jwt.encode({"auth_user_id": 1, "session_id": 1}, 'placeholder', algorithm='HS256'),
        "auth_user_id": 1
    }

def test_mulitple_registers():
    '''
    Basic test to check auth/register/v2 return values for multiple consecutive registers
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testemail@gmail.com",
    "password": "pass123",
    "name_first": "test",
    "name_last": "dummy"})
    
    assert response.json() == {
        "token": jwt.encode({"auth_user_id": 1, "session_id": 1}, 'placeholder', algorithm='HS256'),
        "auth_user_id": 1
    }

    response1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testemail1@gmail.com",
    "password": "pass1231",
    "name_first": "test1",
    "name_last": "dummy1"})

    assert response1.json() == {
        "token": jwt.encode({"auth_user_id": 2, "session_id": 2}, 'placeholder', algorithm='HS256'),
        "auth_user_id": 2
    }

    response2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testemail2@gmail.com",
    "password": "pass1232",
    "name_first": "areallylongfirstname",
    "name_last": "areallylonglastname"})

    assert response2.json() == {
        "token": jwt.encode({"auth_user_id": 3, "session_id": 3}, 'placeholder', algorithm='HS256'),
        "auth_user_id": 3
    }

def test_duplicated_emails():
    requests.delete(f"{BASE_URL}/clear/v1")
    requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testemail@gmail.com",
    "password": "pass123",
    "name_first": "test",
    "name_last": "dummy"})
    
    duplicated = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testemail@gmail.com",
    "password": "pass123",
    "name_first": "test",
    "name_last": "dummy"})
    assert duplicated.status_code == InputError.code

def test_invalid_email():
    requests.delete(f"{BASE_URL}/clear/v1")
    no_symbols = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "invalidemail",
        "password": "pass123",
        "name_first": "test",
        "name_last": "dummy"
    })
    assert no_symbols.status_code == InputError.code
    
    with_symbols = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "invalidemail@email.",
        "password": "pass123",
        "name_first": "test",
        "name_last": "dummy"
    })
    assert with_symbols.status_code == InputError.code
    
def test_register_invalid_password_length():
    '''
    password passed to auth_register is less than 6 chars
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    faliure = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "no",
    "name_first": "test",
    "name_last": "dummy"})
    assert faliure.status_code == InputError.code

def test_register_invalid_first_over_50_chars():
    '''
    name_first passed to auth_register is over 50 chars
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    faliure = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "password",
    "name_first": "very_______________________long_____________________first",
    "name_last": "dummy"})
    assert faliure.status_code == InputError.code

def test_register_invalid_first_empty():
    '''
    name_first passed to auth_register is empty
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    faliure = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "no",
    "name_first": "",
    "name_last": "dummy"})
    assert faliure.status_code == InputError.code

# last name must be between 1-50 characters inclusive
def test_register_invalid_last_over_50_chars():
    '''
    name_last passed to auth_register is over 50 chars
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    faliure = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "password",
    "name_first": "first",
    "name_last": "very______________________long_______________________last"})
    assert faliure.status_code == InputError.code

def test_register_invalid_last_empty():
    '''
    name_last passed to auth_register is empty
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    faliure = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "password",
    "name_first": "first",
    "name_last": ""})
    assert faliure.status_code == InputError.code
    
def test_register_correct_output_single():
    '''
    single use of auth_register should return auth_user_id = 1
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert response.status_code == 200
    response = response.json()
    assert response['auth_user_id'] == 1

def test_register_correct_output_multiple():
    '''
    mulitple use of auth_register 3x
    should return auth_user_id = = 1st auth_user_id + 2
    for most recently registered user
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    auth_id1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert auth_id1.status_code == 200
    auth_id1 = auth_id1.json()
    
    auth_id2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid2@email.used",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert auth_id2.status_code == 200
    auth_id2 = auth_id2.json()
    
    auth_id3 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid3@email.used",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert auth_id3.status_code == 200
    auth_id3 = auth_id3.json()   

    assert (auth_id3['auth_user_id']) == auth_id1['auth_user_id'] + 2
    
    list_request = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': auth_id1['token']
    })
    assert list_request.json() == {
        'users': [
            {
                'u_id': auth_id1['auth_user_id'],
                'email': 'valid@email.used',
                'name_first': 'first',
                'name_last': 'last',
                'handle_str': 'firstlast',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': auth_id2['auth_user_id'],
                'email': 'valid2@email.used',
                'name_first': 'first',
                'name_last': 'last',
                'handle_str': 'firstlast0',
                'profile_img_url': f"{BASE_URL}/images/default.jpg" 
            },
            {
                'u_id': auth_id3['auth_user_id'],
                'email': 'valid3@email.used',
                'name_first': 'first',
                'name_last': 'last',
                'handle_str': 'firstlast1',
                'profile_img_url': f"{BASE_URL}/images/default.jpg"      
            }
        ]
    }


