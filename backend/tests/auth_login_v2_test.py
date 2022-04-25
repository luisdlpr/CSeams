'''
auth_login_v2_test.py
21/3/22
Amy Pham z5359018 - W11B CAMEL
Tests to ensure correct output and errors are
given by auth/login/v2
'''

import pytest
import requests
import json
from src import config
import src.server
import jwt
from src.error import InputError, AccessError

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"

def test_auth_login_correct_output():   
    '''
    tests for correct output for auth/login/v2
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    print(response.json())

    # login user
    response1 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "valid@email.com",
    "password": "password"
    })
    print(response1.json())
    
    #assert response1.status_code == 200

    assert response1.json() == {
        "token": jwt.encode({"auth_user_id": 1, "session_id": 2}, 'placeholder', algorithm='HS256'),
        "auth_user_id": 1,
    }

def test_login_multi_session():   
    '''
    tests for correct output for auth/logout/v1 if user is registered and logged in
    in multiple sessions
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})


     # login user
    response1 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "valid@email.com",
    "password": "password"
    } )

    response2 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "valid@email.com",
    "password": "password"
    } )


    assert response.json() == {
        "token": jwt.encode({"auth_user_id": 1, "session_id": 1}, 'placeholder', algorithm='HS256'),
        "auth_user_id": 1,
    }
    assert response1.json() == {
        "token": jwt.encode({"auth_user_id": 1, "session_id": 2}, 'placeholder', algorithm='HS256'),
        "auth_user_id": 1,
    }
    assert response2.json() == {
        "token": jwt.encode({"auth_user_id": 1, "session_id": 3}, 'placeholder', algorithm='HS256'),
        "auth_user_id": 1,
    }

def test_login__after_logout():   
    '''
    tests for correct output for auth/logout/v1 if user is registered and logged in
    in multiple sessions
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    tok = response.json()['token']

     # logout user
    response0 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": tok })
    assert response0.status_code == 200
    assert response0.json() == {}

     # login user
    response1 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "valid@email.com",
    "password": "password"
    } )
    assert response1.json() == {
        "token": jwt.encode({"auth_user_id": 1, "session_id": 2}, 'placeholder', algorithm='HS256'),
        "auth_user_id": 1,
    }
    assert response1.status_code == 200

def test_login_incorrect_email():
    '''
    auth_login is passed an unregistered email
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    auth_id1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert auth_id1.status_code == 200
    faliure = requests.post(f"{BASE_URL}/auth/login/v2", json={
        'email': "wrong@email.used",
        'password': 'password'
    })
    assert faliure.status_code == InputError.code

def test_login_incorrect_email_no_registered_users():
    '''
    auth_login is used when there are no registered users
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    faliure = requests.post(f"{BASE_URL}/auth/login/v2", json={
        'email': "valid@email.used",
        'password': 'password'
    })
    assert faliure.status_code == InputError.code

def test_login_incorrect_password():
    '''
    auth_login is passed a password that doesn't
    match up with its registered email
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    auth_id1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    auth_id1.status_code == 200
    faliure = requests.post(f"{BASE_URL}/auth/login/v2", json={
        'email': "valid@email.used",
        'password': 'wrong_password'
    })
    assert faliure.status_code == InputError.code

def test_login_correct_output_single():
    '''
    checking auth_login after a single user was registered
    should return the auth_user_id of logged in user
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    auth_id_login = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.used",
    "password": "password",
    "name_first": "firstfirstfirst",
    "name_last": "lastlastlastlast"})
    auth_id = requests.post(f"{BASE_URL}/auth/login/v2", json={
        'email': "valid@email.used",
        'password': 'password'
    })
    assert auth_id.status_code == auth_id_login.status_code == 200
    auth_id_login = auth_id_login.json()
    auth_id = auth_id.json()
    assert auth_id['auth_user_id'] == auth_id_login['auth_user_id']

def test_login_correct_output_multiple():
    '''
    checking auth_login after multiple users are registered
    should return the auth_user_id of logged in user
    '''
    requests.delete(f"{BASE_URL}/clear/v1")

    requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid1@email.used",
    "password": "password1",
    "name_first": "first",
    "name_last": "last"})
    auth_id_login2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid2@email.used",
    "password": "password2",
    "name_first": "first",
    "name_last": "last"})
    requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid3@email.used",
    "password": "password3",
    "name_first": "first",
    "name_last": "last"})
    requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid4@email.used",
    "password": "password4",
    "name_first": "first",
    "name_last": "last"})
    auth_id = requests.post(f"{BASE_URL}/auth/login/v2", json={
        'email': "valid2@email.used",
        'password': 'password2'
    })
    assert auth_id.status_code == auth_id.status_code == 200
    auth_id = auth_id.json()
    auth_id_login2 = auth_id_login2.json()
    
    assert (auth_id['auth_user_id']) == auth_id_login2['auth_user_id']
