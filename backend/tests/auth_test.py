"""'''
auth_test.py
4/3/22
Amy Pham z5359018 - W11B CAMEL
Tests to ensure correct output and errors are
given by the functions created in auth.py
'''

import pytest
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import InputError

#########################  AUTH_REGISTER  ##########################

# emails must be in valid format
def test_register_invalid_no_symbols():
    '''
    email is in invalid format with no symbols '@','.'
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("invalidemail", "password", "first", "last")

def test_register_invalid_email_with_symbols():
    '''
    email is in invalid format with symbols '@','.'
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("invalid@email.", "password", "first", "last")

def test_register_invalid_email_empty():
    '''
    email is an empty string
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("", "password", "first", "last")

def test_register_duplicate_email():
    '''
    email cannot be registered if already used by another user
    '''
    clear_v1()
    auth_register_v1("duplicate@email.used", "password", "first", "last")
    with pytest.raises(InputError):
        auth_register_v1("duplicate@email.used", "password", "first", "last")

def test_register_invalid_password_length():
    '''
    password passed to auth_register is less than 6 chars
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("valid@email.used", "no", "first", "last")


def test_register_invalid_first_over_50_chars():
    '''
    name_first passed to auth_register is over 50 chars
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("vaild@email.used", "password",
                         "very_______________________long_____________________first", "last")

def test_register_invalid_first_empty():
    '''
    name_first passed to auth_register is empty
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("vaild@email.used", "password", "", "last")

# last name must be between 1-50 characters inclusive
def test_register_invalid_last_over_50_chars():
    '''
    name_last passed to auth_register is over 50 chars
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("valid@email.used", "password", "first",
                         "very______________________long_______________________last")

def test_register_invalid_last_empty():
    '''
    name_last passed to auth_register is empty
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("valid@email.used", "password", "first", "")

def test_register_correct_output_single():
    '''
    single use of auth_register should return auth_user_id = 1
    '''
    clear_v1()
    auth_id = auth_register_v1("valid@email.used", "password", "first", "last")
    assert (auth_id['auth_user_id']) == 1

def test_register_correct_output_multiple():
    '''
    mulitple use of auth_register 3x
    should return auth_user_id = = 1st auth_user_id + 2
    for most recently registered user
    '''
    clear_v1()
    auth_id1 = auth_register_v1("valid1@email.used", "password1", "first1", "last1")
    auth_register_v1("valid2@email.used", "password2", "first2", "last2")
    auth_id3 = auth_register_v1("valid3@email.used", "password3", "first3", "last3")
    assert (auth_id3['auth_user_id']) == auth_id1['auth_user_id'] + 2

#########################  AUTH_LOGIN  ##############################

def test_login_incorrect_email():
    '''
    auth_login is passed an unregistered email
    '''
    clear_v1()
    auth_register_v1("valid@email.used", "password", "first", "last")
    with pytest.raises(InputError):
        auth_login_v1("wrong@email.used", "password")

def test_login_incorrect_email_no_registered_users():
    '''
    auth_login is used when there are no registered users
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_login_v1("valid@email.used", "password")

def test_login_incorrect_password():
    '''
    auth_login is passed a password that doesn't
    match up with its registered email
    '''
    clear_v1()
    auth_register_v1("valid@email.used", "password", "first", "last")
    with pytest.raises(InputError):
        auth_login_v1("valid@email.used", "invalid_pass")

def test_login_correct_output_single():
    '''
    checking auth_login after a single user was registered
    should return the auth_user_id of logged in user
    '''
    clear_v1()
    auth_id_login = auth_register_v1("valid@email.used", "password", "first", "last")
    auth_id = auth_login_v1("valid@email.used", "password")
    assert (auth_id['auth_user_id']) == auth_id_login['auth_user_id']

def test_login_correct_output_multiple():
    '''
    checking auth_login after multiple users are registered
    should return the auth_user_id of logged in user
    '''
    clear_v1()
    auth_register_v1("valid1@email.used", "password1", "first1", "last1")
    auth_id_login = auth_register_v1("valid2@email.used", "password2", "first2", "last2")
    auth_register_v1("valid3@email.used", "password3", "first3", "last3")
    auth_register_v1("valid4@email.used", "password4", "first4", "last4")

    auth_id = auth_login_v1("valid2@email.used", "password2")
    assert (auth_id['auth_user_id']) == auth_id_login['auth_user_id']
"""