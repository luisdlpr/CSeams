import pytest
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1
from src.other import clear_v1
from src.error import InputError, AccessError
def test_logout_correct_output_register():
    clear_v1()
    user = auth_register_v1("valid1@email.used", "password1", "first1", "last1")
  
    assert auth_logout_v1(user['token']) == {}

def test_logout_correct_output_multiple_registered():
    '''
    checking auth_logout after multiple users are registered and one is logged in
    '''
    clear_v1()
    auth_register_v1("valid1@email.used", "password1", "first1", "last1")
    auth_register_v1("valid2@email.used", "password2", "first2", "last2")
    auth_register_v1("valid3@email.used", "password3", "first3", "last3")
    auth_register_v1("valid4@email.used", "password4", "first4", "last4")

    auth_id = auth_login_v1("valid2@email.used", "password2")
    assert auth_logout_v1(auth_id['token']) == {}

def test_logout_correct_output_single_login():
    '''
    checking auth_logout after a user is registered and logged in
    '''
    clear_v1()
    auth_register_v1("valid1@email.used", "password1", "first1", "last1")
    user = auth_login_v1("valid1@email.used", "password1")
  
    assert auth_logout_v1(user['token']) == {}

"""def test_logout_invalid_token_after_logout():
    clear_v1()
    user = auth_register_v1("valid1@email.used", "password1", "first1", "last1")
    assert auth_logout_v1(user['token']) == {}

    with pytest.raises(AccessError):
        auth_logout_v1(user['token'])"""

    

