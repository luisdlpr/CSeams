"""'''
This file contains all tests for dm_messages_v1
Written by Reuel Nkomo
z5367441 UNSW COMP1531 22T1
'''
import pytest
from src.error import AccessError, InputError
from src.other import clear_v1
from src.dm import dm_create_v1, dm_messages_v1
from src.auth import auth_register_v1

# 1. dm_id does not refer to a valid dm (InputError)
def test_dm_messages_v1_invalid_dm_id():
    '''
    Test that when an InputError is raised when dm_id does not
    refer to a valid dm
    '''
    clear_v1()
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')

    dm_id_invalid = 1
    token_valid = owner_details['token']
    start_valid = 0

    with pytest.raises(InputError):
        dm_messages_v1(token_valid, dm_id_invalid, start_valid)


# 2. start is greater than the total number of messages in the dm (InputError)
def test_dm_messages_v1_messages_invalid_start():
    '''
    Test that when start is greater than the total emount of messages in
    the given dm, an InputError is raised.
    '''
                                        #dms[ id = 0][messages[...]]
    '''
    max_start = len(data['dms'][0]['dm_messages']) - 1
    if max_start < 0:
        max_start = 0
    '''
    clear_v1()
    owner_details = auth_register_v1('johndoes@gmail.com', 'johndoespassword123', 'John', 'Doe')
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')

    dm_details = dm_create_v1(owner_details['auth_user_id'], [user1_details['auth_user_id']])
    
    start_invalid = 1
    with pytest.raises(InputError):
        dm_messages_v1(owner_details['auth_user_id'], dm_details['dm_id'], start_invalid)

def test_no_messages():
    clear_v1()

    user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')

    dm_details = dm_create_v1(user['auth_user_id'], [user1_details['auth_user_id']])
    
    start = 0
    assert dm_messages_v1(user['auth_user_id'], dm_details['dm_id'], start) == {
        'messages': [],
        'start': 0,
        'end': -1
    }

def test_access_error_when_user_is_non_member():
    clear_v1()
    user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')

    dm_details = dm_create_v1(user['auth_user_id'], [user1_details['auth_user_id']])
    non_member_details = auth_register_v1('jakedoes@gmail.com', 'jakedoespassword123', 'Jake', 'Doe')
    
    start = 0
    with pytest.raises(AccessError):
        dm_messages_v1(non_member_details['auth_user_id'], dm_details['dm_id'], start)

def test_access_error_when_member_not_exist():
    clear_v1()
    user = auth_register_v1("sheriff.woody@andysroom.com", "password", "sheriff", "woody")
    user1_details = auth_register_v1('Janedoes@gmail.com','janedoespasswrod123', 'Jane', 'Doe')

    dm_details = dm_create_v1(user['auth_user_id'], [user1_details['auth_user_id']])
    not_user_details = {'token': 'steve', 'auth_user_id': -1}
    
    start = 0
    with pytest.raises(AccessError):
        dm_messages_v1(not_user_details['auth_user_id'], dm_details['dm_id'], start)
"""        