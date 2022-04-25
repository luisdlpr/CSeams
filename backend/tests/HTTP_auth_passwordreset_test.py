'''
HTTP_auth_passwordreset_test.py
4/4/22
Amy Pham z5359018 - W11B CAMEL
Tests to ensure correct output and errors are
given by auth/passwordreset/request/v1 and auth/passwordreset/reset/v2
'''

import pytest
import requests
import json
from src import config
from src.helpers import hash
import src.server
import jwt
from src.error import InputError, AccessError

BASE_ADDRESS = 'http://127.0.0.1'
BASE_PORT = config.port
BASE_URL = f"{BASE_ADDRESS}:{BASE_PORT}"

######################## PASSWORDRESET/REQUEST ##########################
def test_request_correct_output_logged_in():
    '''
    tests for correct output for auth/passwordrest/request/v1 
    if user is logged in and requests a new password
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user - user is automatically logged in
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testrequestemail1@gmail.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert response.status_code == 200
    token = response.json()['token']

    # requests new pass
    response1 = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json={"email": "testrequestemail1@gmail.com"})
    assert response1.status_code == 200
    assert response1.json() == {}

    # cannot log out since already logged out when requesting new pass
    response2 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token })
    assert response2.status_code == 403

def test_request_correct_output_logged_out():
    '''
    tests for correct output for auth/passwordrest/request/v1 
    if user is not logged in and requests a new password
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user - user is automatically logged in
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testrequestemail1@gmail.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert response.status_code == 200
    token = response.json()['token']

    # logs out
    response1 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token })
    assert response1.status_code == 200

    # requests new pass
    response2 = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json={"email": "testrequestemail1@gmail.com"})
    assert response2.status_code == 200
    assert response2.json() == {}

    # cannot log out since already logged out
    response3 = requests.post(f"{BASE_URL}/auth/logout/v1", json = {"token": token })
    assert response3.status_code == 403

######################## PASSWORDRESET/RESET ##########################

def test_reset_single_request():
    '''
    tests for correct output for auth/passwordreset/reset/v1 
    if there is one request currently
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user 
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testrequestemail1@gmail.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert response.status_code == 200

    # requests new pass 
    response1 = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json={"email": "testrequestemail1@gmail.com"})
    assert response1.status_code == 200

    # resets new pass 
    reset_code = hash("testrequestemail1@gmail.com")
    response2 = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json={"reset_code": reset_code, "new_password": "new_pass"})
    assert response2.status_code == 200
    assert response2.json() == {}

    # user should be able to login using new pass
    response3 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "testrequestemail1@gmail.com",
    "password": "new_pass"
    } )
    assert response3.status_code == 200

def test_reset_mulitple_requests():
    '''
    tests for correct output for auth/passwordrest/reset/v1 
    if there are multiple request currently
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user 
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testrequestemail1@gmail.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert response.status_code == 200

    # registers 1 user 
    response1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testrequestemail2@gmail.com",
    "password": "password1",
    "name_first": "first1",
    "name_last": "last1"})
    assert response1.status_code == 200

    # requests new pass for 1st user
    response3 = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json={"email": "testrequestemail1@gmail.com"})
    assert response3.status_code == 200
    
    # requests new pass for 2nd user
    response4 = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json={"email": "testrequestemail2@gmail.com"})
    assert response4.status_code == 200

    # resets new pass for 2nd user
    reset_code = hash("testrequestemail2@gmail.com")
    response5 = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json={"reset_code": reset_code, "new_password": "new_pass"})
    assert response5.status_code == 200
    assert response5.json() == {}

    # 2nd user should be able to login using new pass
    response6 = requests.post(f"{BASE_URL}/auth/login/v2", json = {
    "email": "testrequestemail2@gmail.com",
    "password": "new_pass"
    } )
    assert response6.status_code == 200

def test_reset_invalid_reset_code_request_invalid_email():
    '''
    tests for InputError for auth/passwordreset/reset/v1 
    if an invalid email is passed to auth/passwordreset/request/v1
    '''
    requests.delete(f"{BASE_URL}/clear/v1")

    # requests new pass for unregistered email
    response1 = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json={"email": "invalid@email.com"})
    assert response1.status_code == 200
    assert response1.json() == {}

    # cannot reset password
    reset_code = hash("invalid@email.com")
    response2 = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json={"reset_code": reset_code, "new_password": "new_pass"})
    assert response2.status_code == 400

def test_reset_invalid_reset_code():
    '''
    tests for InputError for auth/passwordreset/reset/v1 
    if an invalid reset_code is passed
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user 
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testrequestemail1@gmail.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert response.status_code == 200

    # requests new pass 
    response1 = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json={"email": "testrequestemail1@gmail.com"})
    assert response1.status_code == 200

    # cannot reset password with wrong reset_code
    response2 = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json={"reset_code": "invalid_code", "new_password": "new_pass"})
    assert response2.status_code == 400

def test_reset_invalid_password():
    '''
    tests for InputError for auth/passwordreset/reset/v1 
    if an invalid password is passed (less than 6 chars long)
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    # registers 1 user 
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
    "email": "testrequestemail1@gmail.com",
    "password": "password",
    "name_first": "first",
    "name_last": "last"})
    assert response.status_code == 200

    # requests new pass 
    response1 = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json={"email": "testrequestemail1@gmail.com"})
    assert response1.status_code == 200

    # cannot reset password with invalid new_password length
    reset_code = hash("testrequestemail1@gmail.com")
    response2 = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json={"reset_code": reset_code, "new_password": "new"})
    assert response2.status_code == 400

