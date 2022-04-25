"""import pytest
import jwt
from src.other import clear_v1
from src.auth import auth_register_v1
from src.auth import auth_login_v1
from src.channels import channels_create_v1
from src.channels import channels_listall_v1
from src.error import InputError

## clear_v1 tests ##
## Test clear_v1() empties this. ##
def test_clear_basic():
    '''
    Tests clear using auth_register_v1, auth_login_v1 and channels_create_v1
    '''
    clear_v1()
    user1_data = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy1')
    user2_data = auth_register_v1('testemail2@hotmail.com', 'pass123', 'Test', 'Dummy2')
    channel1_id = channels_create_v1(user1_data['auth_user_id'], 'Channel 1', True)
    channel2_id = channels_create_v1(user2_data['auth_user_id'], 'Channel 2', True)
    ## check database not empty ##
    channel1_id['name'] = 'Channel 1'
    channel2_id['name'] = 'Channel 2'
    assert channels_listall_v1(user1_data['auth_user_id']) == {
        'channels': [
            channel1_id,
            channel2_id
        ]
    }
    login_user1 = auth_login_v1('testemail1@hotmail.com', 'pass123')
    login_user2 = auth_login_v1('testemail2@hotmail.com', 'pass123')
   
    assert login_user1['auth_user_id'] == user1_data['auth_user_id']
    assert login_user2['auth_user_id'] == user2_data['auth_user_id']
    assert login_user1['token'] == jwt.encode({"auth_user_id": 1, "session_id": 3}, 'placeholder', algorithm='HS256')
    assert login_user2['token'] == jwt.encode({"auth_user_id": 2, "session_id": 4}, 'placeholder', algorithm='HS256')
   
    clear_v1()
    with pytest.raises(InputError):
        assert auth_login_v1('testemail1@hotmail.com', 'pass123')
        assert auth_login_v1('testemail2@hotmail.com', 'pass123')
    user1_newid = auth_register_v1('testemail1@hotmail.com', 'pass123', 'Test', 'Dummy')
    assert channels_listall_v1(user1_newid['auth_user_id']) == {
        'channels': []
    }
"""