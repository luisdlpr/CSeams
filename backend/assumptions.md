1. The functions in channel.py won't be used/invoked unless there's a user in data_store.
2. Since users and channels have no current implementation for deletion, it is assumed that channel_id and user_id remain ordered from smallest to largest in the data_store.
3. auth_register creates users with auth_user_id starting from 1
4. channels_create creates channels with channel_id starting from 1
5. channel_details uses the key called 'channel_name' to store the name of the channel in data_store but returns the channel name in the key 'name' as an output
6. the user with u_id of 1 has global owner permissions (because there's no way for them to leave yet.)

7. You can't have more than 10 million messages in any of the channels or dms.