'''
auth_logout_test.py
21/3/22
Amy Pham z5359018 - W11B CAMEL
Tests to ensure correct output and errors are
given by auth/logout/v1
'''

import requests
from src import config
import jwt

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"
def test_logout_register():   
    '''
    tests for correct output for auth/logout/v1
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})


    
    user1 = r.json()
    token1 = user1['token']
    print(user1)

    # logout user
    response1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token1 })
    assert response1.status_code == 200

    assert response1.json() == {}


def test_logout_login():   
    '''
    tests for correct output for auth/logout/v1 if user is registered and logged in
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user
    requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})

    # login user
    response = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "valid@email.com",
    "password": "password"
    } )
    
    user1 = response.json()
    token1 = user1['token']

    # logout user
    response1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token1 })
    assert response1.status_code == 200

    assert response1.json() == {}

def test_logout_invalid_token_2xlogout():   
    '''
    tests for correct error for auth/logout/v1 if user is registered and logs out
    but tries to logout again
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    
    user1 = response.json()
    token1 = user1['token']

    # logout user
    response1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token1 })
    assert response1.status_code == 200

    assert response1.json() == {}

    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token1 })
    assert response.status_code == 403

def test_logout_invalid_token_fake_token():   
    '''
    tests for correct error for auth/logout/v1 if a fake token is passed to logout
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user
    requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    
    fake = jwt.encode({"auth_user_id": 1, "session_id": 1}, 'fake', algorithm='HS256')

    # logout user
    response2 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": fake})
    assert response2.status_code == 403

def test_logout_multi_session():   
    '''
    tests for correct output for auth/logout/v1 if user is registered and logged in
    another session and tries to logout of both sessions
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})

    token1 = response.json()['token']

     # login user
    response1 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "valid@email.com",
    "password": "password"
    } )

    token2 = response1.json()['token']

    # logout user
    response1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token1 })
    assert response1.status_code == 200

    assert response1.json() == {}

     # logout user
    response1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token2 })
    assert response1.status_code == 200

    assert response1.json() == {}

