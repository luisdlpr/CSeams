'''
Check for multiple sessions occuring concurrently
'''

import requests
from src import config

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"  

def test_sessions_user_with_multi_sessions(): 
    '''
    tests for correct output for if the user has multiple sessions
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
    })
    token2 = response1.json()['token']

    # login user again
    response2 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "valid@email.com",
    "password": "password"
    })
    token3 = response2.json()['token']

    # logout once using token1
    response1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token1 })
    assert response1.status_code == 200
    assert response1.json() == {}

    # check token2 and token3 are still valid
    all_users = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': token2
    })
    assert response1.status_code == 200
    
    all_users_check = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': token3
    })
    assert response1.status_code == 200
    assert all_users.json() == all_users_check.json()

    # check token1 is invalid
     # logout once using token1
    response1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token1 })
    assert response1.status_code == 403

def test_sessions_multi_users_with_multi_sessions(): 
    '''
    tests for correct output for if there are 
    multiple users who have multiple sessions
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    ###### USER 1 #####
    # registers 1 user
    tok1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid@email.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    token1 = tok1.json()['token']

    # login user
    tok2 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "valid@email.com",
    "password": "password"
    })
    token2 = tok2.json()['token']

    ###### USER 2 #####
    # registers 1 user
    tok3 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "valid1@email.com",
    "password": "password1",
    "name_first": "first1",
    "name_last": "last1"})
    token3 = tok3.json()['token']

    # login user
    tok4 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "valid1@email.com",
    "password": "password1"
    })
    token4 = tok4.json()['token']

    # check users beforehand
    users_before1 = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': token1
    })

    # logout user1 once using token1
    response1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token1 })
    assert response1.status_code == 200
    assert response1.json() == {}

    # check other user1 still has a valid token and token1 is invalid
    users_after1 = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': token2
    })
    assert users_after1.status_code == 200
    assert users_before1.json() == users_after1.json()

    invalid1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token1 })
    assert invalid1.status_code == 403

    # logout user2 using token3
    response2 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token3 })
    assert response2.status_code == 200
    assert response2.json() == {}

    # check user2 still has valid token and token 3 is invalid
    users_after2 = requests.get(f"{BASE_URL}/users/all/v1", params={
        'token': token4
    })
    assert users_after1.status_code == 200
    assert users_before1.json() == users_after2.json()

    response3 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token3 })
    assert response3.status_code == 403
