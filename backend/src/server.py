import signal
from json import dumps, loads
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
from src.error import AccessError
from src import config, channels, channel, other, dm, auth, helpers, user,\
    admin, message, standup, search, notifications, stats
from src.data_store import data_store
import jwt, pickle

SECRET = 'placeholder'
def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path="/images/", static_folder="../images")
CORS(APP)
MAIL = Mail(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

#### TO USE FLASK MAIL:
APP.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_SSL= False,
    MAIL_USERNAME = 'testauthemail16@gmail.com',
    MAIL_PASSWORD = 'simplepass',
    MAIL_USE_TLS = True
)


MAIL = Mail(APP)
####

try:
    data = pickle.load(open('datastore.p', 'rb'))
    data_store.set(data)
except Exception:
    other.clear_v1()
    helpers.reset_sessions()
    
@APP.after_request
def save(response):
    with open('datastore.p', 'wb') as FILE:
        pickle.dump(data_store.get(), FILE)   
    return response
    

######### channels.py wrapper ##########

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    try:
        data = request.get_json()
        return channels.channels_create_v1(data['token'], data['name'], data['is_public'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/channels/list/v2", methods=['GET'])
def list_channels():
    try:
        token = request.args.get('token')
        return channels.channels_list_v1(token)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

    
@APP.route("/channels/listall/v2", methods=['GET'])
def list_all_channels():
    try:
        token = request.args.get('token')
        return channels.channels_listall_v1(token)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error
    
######### dm.py wrapper ##########

@APP.route("/dm/create/v1", methods=["POST"])
def create_dm():
    try:
        data = request.get_json()
        return dm.dm_create_v1(data['token'], data['u_ids'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/dm/list/v1", methods=["GET"])
def list_dm():
    try:
        token = request.args.get("token")
        return dm.dm_list_v1(token)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/dm/remove/v1", methods=["DELETE"])
def remove_dm():
    try:
        data = request.get_json()
        return dm.dm_remove_v1(data['token'], data['dm_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/dm/details/v1", methods=["GET"])
def dm_details():
    try:
        token = request.args.get('token')
        dm_id = int(request.args.get('dm_id'))
        return dm.dm_details_v1(token, dm_id)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/dm/leave/v1", methods=["POST"])
def leave_dm():
    try:
        data = request.get_json()
        return dm.dm_leave_v1(data['token'], data['dm_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/dm/messages/v1", methods = ['GET'])
def dm_messages_v1():
    try:
        token = request.args.get('token')
        dm_id = int(request.args.get('dm_id'))
        start = int(request.args.get('start'))
        return dm.dm_messages_v1(token, dm_id, start)
    # decode failed or content of decoded token is unexpected
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/clear/v1", methods=['DELETE'])
def clear_out():
    other.clear_v1()
    helpers.reset_sessions()
    return {}
    
# ## remove this when we are sure everything is working fine ########
'''@APP.route("/")
def print_data_store():
    return dumps(data_store.get())'''


###### auth.py wrappers #######

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2():
    try:
        data = request.get_json()
        return auth.auth_register_v1(data['email'], data['password'], data['name_first'], data['name_last'])
    except KeyError as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2():
    try:
        data = request.get_json()
        return auth.auth_login_v1(data['email'], data['password'])
    except KeyError as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 


@APP.route("/auth/logout/v1", methods = ['POST'])
def auth_logout_v1():
    try:
        data = request.get_json()
        return auth.auth_logout_v1(data['token'])
    except KeyError as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 

@APP.route("/auth/passwordreset/request/v1", methods = ['POST'])
def auth_passwordreset_request_v1():
    try:
        data = request.get_json()
        result = auth.auth_passwordreset_request_v1(data['email'])
        # send email with reset code
        if result == True:
            msg = Message('Reset password request', sender = 'testauthemail16@gmail.com', recipients = [data['email']])
            msg.body = f"Your reset code is: {helpers.hash(data['email'])}"
            MAIL.send(msg)
        return {}
    except KeyError as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

@APP.route("/auth/passwordreset/reset/v1", methods = ['POST'])
def auth_passwordreset_reset_v1():
    try:
        data = request.get_json()
        return auth.auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])
    except KeyError as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error
    
###### user.py wrapper ######

@APP.route("/users/all/v1", methods=['GET'])
def users_all_v1():
    try:
        token = request.args.get('token')
        return user.users_all_v1(token)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 


@APP.route("/user/profile/v1", methods=['GET'])
def user_profile_v1():
    try:
        token = request.args.get('token')
        u_id = int(request.args.get('u_id'))
        return user.user_profile_v1(token, u_id)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 


@APP.route("/user/profile/setname/v1", methods=['PUT'])
def users_profile_setname_v1():
    try:
        data = request.get_json()
        return user.profile_setname_v1(data['token'], data['name_first'], data['name_last'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 


@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def users_profile_setemail_v1():
    try:
        data = request.get_json()
        return user.profile_setemail_v1(data['token'], data['email'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 

 
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def users_profile_sethandle_v1():
    try:
        data = request.get_json()
        return user.profile_sethandle_v1(data['token'], data['handle_str'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 
###### channel.py wrapper #######


@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():
    try:
        data = request.get_json()
        return channel.channel_invite_v1(data['token'], data['channel_id'], data['u_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 


@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_v1_http_call():
    try:
        data = request.get_json()
        return channel.channel_leave_v1(data['token'], data['channel_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 

  
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2():
    try:
        data = request.get_json()
        return channel.channel_join_v1(data['token'], data['channel_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error   


@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    try:
        data = request.args.get('token')
        c_id = int(request.args.get('channel_id'))
        return channel.channel_details_v1(data, c_id)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error   


@APP.route("/channel/addowner/v1", methods=["POST"])
def add_owner():
    try:
        data = request.get_json()        
        return channel.channel_add_owner_v1(data['token'], data['channel_id'], data['u_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/channel/removeowner/v1", methods=["POST"])
def remove_owner():
    try:
        data = request.get_json()
        return channel.channel_remove_owner_v1(data['token'], data['channel_id'], data['u_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/channel/messages/v2", methods = ['GET'])
def channel_messages_v2():
    try:
        token = request.args.get('token')
        channel_id = int(request.args.get('channel_id'))
        start = int(request.args.get('start'))
        return channel.channel_messages_v1(token, channel_id, start)
    # decode failed or content of decoded token is unexpected
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

###### admin.py wrapper #######

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove_http():
    try:
        data = request.get_json()
        return admin.admin_user_remove_v1(data['token'], data['u_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermissions_change_http():
    try:
        data = request.get_json()
        return admin.admin_userpermission_change_v1(data['token'], data['u_id'], data['permission_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

###### messages.py wrapper #######

@APP.route("/message/send/v1", methods=["POST"])
def message_send_v1():
    try:
        data = request.get_json()
        return message.message_send_v1(data['token'], data['channel_id'], data['message'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/message/sendlater/v1", methods=["POST"])
def http_message_sendlater_v1():
    try:
        data = request.get_json()
        return message.message_sendlater_v1(data['token'], data['channel_id'], data['message'], data['time_sent'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

   
@APP.route("/message/senddm/v1", methods=["POST"])
def message_senddm_v1():
    try:
        data = request.get_json()
        return message.message_send_dm_v1(data['token'], data['dm_id'], data['message'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/message/sendlaterdm/v1", methods=["POST"])
def http_message_sendlater_dm_v1():
    try:
        data = request.get_json()
        return message.message_sendlater_dm_v1(data['token'], data['dm_id'], data['message'], data['time_sent'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit_v1():
    try:
        data = request.get_json()
        return message.message_edit_v1(data['token'], data['message_id'], data['message'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

   
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_v1():
    try:
        data = request.get_json()
        return message.message_remove_v1(data['token'], data['message_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

@APP.route("/message/share/v1", methods=['POST'])
def message_share_v1():
    try:
        data = request.get_json()
        return message.message_share_v1(data['token'], data['og_message_id'], data['channel_id'],
                                        data['dm_id'], data['message'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

@APP.route("/message/react/v1", methods=['POST'])
def message_react_v1():
    try:
        data = request.get_json()
        return message.message_react_v1(data['token'], data['message_id'], data['react_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact_v1():
    try:
        data = request.get_json()
        return message.message_unreact_v1(data['token'], data['message_id'], data['react_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

@APP.route("/message/pin/v1", methods = ['POST'])
def message_pin_v1():
    try:
        data = request.get_json()
        return message.message_pin_v1(data['token'], data['message_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

@APP.route("/message/unpin/v1", methods = ['POST'])
def message_unpin_v1():
    try:
        data = request.get_json()
        return message.message_unpin_v1(data['token'], data['message_id'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

###### notifications.py wrapper ########

@APP.route("/notifications/get/v1", methods=["GET"])
def notifications_get_v1():
    try:
        token = request.args.get('token')
        return notifications.get_notifications(token)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


###### stats.py wrapper #######
@APP.route("/users/stats/v1", methods=['GET'])
def users_stats_v1():
    try:
        token = request.args.get('token')
        return stats.workspace_stats(token)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

@APP.route("/user/stats/v1", methods=['GET'])
def user_stats_v1():
    try:
        token = request.args.get('token')
        return stats.user_stats(token)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


##### uploadphotos wrapper ######

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def upload_photo_v1():
    try:
        data = request.get_json()
        return user.profile_upload_photo_v1(data['token'], data['img_url'], data['x_start'], data['y_start'], data['x_end'], data['y_end'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error 


@APP.route('/images/<path:path>')
def send_js(path):
    return send_from_directory('', path)


@APP.route("/standup/active/v1", methods = ['GET'])
def standup_active_http():
    try:
        token = request.args.get('token')
        channel_id = int(request.args.get('channel_id'))
        return standup.standup_active_v1(token, channel_id)
    # decode failed or content of decoded token is unexpected
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


@APP.route("/standup/send/v1", methods=['POST'])
def standup_send_http():
    try:
        data = request.get_json()
        return standup.standup_send_v1(data['token'], data['channel_id'], data['message'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error

######### standup.py wrapper ##########

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start_http():
    try:
        data = request.get_json()
        return standup.standup_start_v1(data['token'], data['channel_id'], data['length'])
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error


###### search.py wrappers ######

@APP.route("/search/v1", methods=['GET'])
def search_v1():
    try:
        token = request.args.get('token')
        query_str = request.args.get('query_str')
        return search.search_v1(token, query_str)
    except (jwt.DecodeError, KeyError) as error:
        raise AccessError(description="Are you trying to hack the system or something?") from error   

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
