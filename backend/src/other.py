'''
File contains functions that do not fit the classifications of any other files in src.
'''

from src.data_store import data_store
from src.helpers import reset_sessions
import os, re, os.path

def clear_v1():
    '''
    < clear_v1() clears all data from the datastore and reinitialises it. >

    Arguments: None

    Exceptions: None

    Return Value: None
    '''
    reset_sessions()
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    store['workspace_stats'] = {}
    directory = "images"
    for filename in os.listdir(directory):
        if filename != "default.jpg":
            os.remove(os.path.join(directory, filename))
    data_store.set(store)
