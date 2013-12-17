'''
Python module for automating box.com 

You should have this page handy for documentation
http://developers.box.com/docs

The process for starting box is to go to this website:
https://gilgamesh.cheme.cmu.edu/cgi-bin/jkitchin-box

put in your box username and password, and save the file that pops up as token.json at the place pointed to by BOX_TOKEN. The token is good for 1 hour, but it can be refreshed for up to 2 weeks. After that, you need to reauthorize at the website.

The api is not 100% covered, and even within a function not all of the options may be covered. In general, I return the json data directly from box, which is buried in the request.

It is not obvious what the most consistent return data is. Not all calls return 200, even when successful.

This module could be the foundation for box-cli. That command might look like this:

box-cli info file
box-cli collaborate --add/--remove/--edit login role
box-cli task --add/--remove/--edit login message
box-cli comment file message

or it could be built into a right-click context menu in windows.
'''
import json, os, time

import requests

# We need to know where the BOX_TOKEN is. There are two options.  You
# can store an environment variable that reads it or it can be stored
# in box_course_config.py. The environment variable lets you use box
# outside of the course.

from box_course import *

if 'BOX_TOKEN' in os.environ:
    BOX_TOKEN = os.environ.get('BOX_TOKEN')


##### From here down should be totally general
API_URI = 'https://api.box.com/2.0'

def authorize():
    '''open a webbrowser to authenticate box and get new tokens'''
    import webbrowser
    webbrowser.open(AUTH_URL, new=0, autoraise=True)


def refresh_tokens():
    '''refresh auth tokens, and save new tokens

    a 401 error means unauthorized access'''
    with open(BOX_TOKEN, 'r') as f:
        d1 = json.loads(f.read())    
        client_id = d1['client_id']
        client_secret = d1['client_secret']
        refresh_token = d1['refresh_token']

    payload = {'refresh_token': refresh_token,
               'client_id':client_id,
               'client_secret':client_secret,
               'grant_type':'refresh_token'}

    r = requests.post('https://www.box.com/api/oauth2/token', 
                      data=payload)
    d2 = json.loads(r.text)
    
    d1.update(d2)
    d1.update({'time_acquired':time.time()})

    with open(BOX_TOKEN, 'w') as f:
        f.write(json.dumps(d1))

    return d1


def get_access_token():
    'convenience function to get access_token'
    with open(BOX_TOKEN, 'r') as f:
        d1 = json.loads(f.read())    

    # the refresh token is expired or new
    twoweeks = 60*60*24*7*2 # sec/min * min/hour * hour/day * day/week * 2 weeks
    if (('time_acquired' not in d1) 
        or (time.time() > (d1['time_acquired'] + twoweeks))):
        authorize()  
        print('seems refresh token is expired')
        d1 = refresh_tokens()

    # tokens are invalid, but can be refreshed
    if (('time_acquired' not in d1) 
        or (time.time() > (d1['time_acquired'] + d1['expires_in']))):
        d1 = refresh_tokens()
        print('token is invalid, but refreshable')

    return d1['access_token']


def check_tokens():
    'Checks if tokens are valid' 
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    r = requests.get(API_URI + '/users/me', headers=headers)
    if r.status_code != 200:
        print 'tokens are not valid'
    return r

##------------------------------------------------------------------
## these are functions for doing things

## -----------------------FOLDERS---------------------------------    

def list_folder(parent_id=0):
    '''List contents of folder with parent_id

    if successful, returns the json data

    if not successful, returns None'''

    headers = {"Authorization": "Bearer %s" % get_access_token()}
    r = requests.get(API_URI + '/folders/{0}/items'.format(parent_id),
                     headers=headers)
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        return None

    
def get_item(name, parent_id=0):
    '''returns json representation of item with name in parent_id

    name may be a path'''
    id = parent_id
    if name.startswith('/'):
        name = name[1:]
    for item in name.split('/'):
        uri = '/folders/{0}/items'.format(id)
        headers = {"Authorization": "Bearer %s" % get_access_token()}
        r = requests.get(API_URI + uri,
                         headers=headers)

        if r.status_code == 401:
            raise Exception('expired tokens')

        if r.status_code == 200:
            j = json.loads(r.text)
            names = [entry['name'] for entry in j['entries']]
            if item in names:
                ind = names.index(item)
                entry = j['entries'][ind]
                id = entry['id'] # redefine id for loop
            else: # not found
                return None
    return entry # I think this is a dictionary from json


def create_a_folder(name, parent_id=0):
    '''Create a single folder in the folder with parent_id

    return the json data from the response 

    http://developers.box.com/docs/#folders-create-a-new-folder'''

    headers = {"Authorization": "Bearer %s" % get_access_token()}
    data = '{{"name":"{0}", "parent": {{"id": "{1}"}}}}'.format(name, parent_id)
    r = requests.post(API_URI + '/folders', headers=headers, data=data)
    
    if r.status_code == 409:  # the folder exists
        return get_item(name, parent_id)
    else:
        d = json.loads(r.text)
        return d


def create_folder(name, parent_id=0):
    '''Create a folder, possibly nested, e.g. level1/level2/level3

    returns list of newly created ids
    '''
    id = parent_id
    ids = []
    for folder in name.split('/'):
        if folder:
            d  = create_a_folder(folder, id)
            id = d['id']
            ids += [id]
    return d


def get_folder_information(folder_id):
    '''http://developers.box.com/docs/#folders-get-information-about-a-folder'''
    uri = '/folders/{0}'.format(folder_id)
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    r = requests.get(API_URI + uri, headers=headers)
    return json.loads(r.text)


def update_folder_information(folder_id, 
                              name=None, 
                              description=None, 
                              parent_id=None):
    '''http://developers.box.com/docs/#folders-update-information-about-a-folder'''
    uri = '/folders/{0}'.format(folder_id)

    headers = {"Authorization": "Bearer %s" % get_access_token()}
    data = {}
    if name: data['name'] = name
    if description: data['description'] = description
    if parent_id: data['parent_id'] = parent_id
    r = requests.put(API_URI + uri, 
                     headers=headers, 
                     data=json.dumps(data))
    return json.loads(r.text)

    
def delete_folder(parent_id, recursive=False):
    '''Delete a folder with parent_id

    set recursive to True if the folder is not empty.

    the response is 204 if successful, and 404 if not found.
    http://developers.box.com/docs/#folders-delete-a-folder
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}

    params = {'recursive':str(recursive).lower()}

    uri='/folders/{0}'.format(parent_id)

    r = requests.delete(API_URI + uri, headers=headers, params=params)
    if r.status_code == 204:
        return {}
    else:
        raise Exception('Could not delete {0}'.format(parent_id))


def copy_folder(id, destination_folder_id, new_name=None):
    '''Copy folder with id to the folder with parent_id, possibly with a new name

    http://developers.box.com/docs/#folders-copy-a-folder
    '''

    headers = {"Authorization": "Bearer %s" % get_access_token()}

    data = {"parent": {"id" : destination_folder_id}}
    if new_name:
        data['name'] = new_name

    uri = '/folders/{0}/copy'.format(id)
    r = requests.post(API_URI + uri, headers=headers, data=json.dumps(data))
    return json.loads(r.text)


## ------------------------------FILES-----------------------

def get_file_information(fileid):
    '''http://developers.box.com/docs/#files-get'''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/files/{0}'.format(fileid)
    r = requests.get(API_URI + uri, headers=headers)
    return json.loads(r.text)


def update_file_information(file_id):
    '''http://developers.box.com/docs/#files-update-a-files-information'''
    raise NotImplemented


def download(filename, newname=None):
    '''download filename, possibly renaming to newname

    filename is presumed to be a path on box

    http://developers.box.com/docs/#files-download-a-file'''
    import urllib

    item = get_item(filename)
    name = item['name']
    id = item['id']
    
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri="/files/{0}/content".format(id)

    r = requests.get(API_URI + uri, 
                     headers=headers,
                     allow_redirects=False)

    dlurl = r.headers['location']
    if newname:
        name = newname
    urllib.urlretrieve (dlurl, name)
    return r

        
def upload(filename, parent_id=0, new_version=False):
    '''upload filename to folder with parent_id, possibly as a new version

    http://developers.box.com/docs/#files-upload-a-file
    '''

    headers = {"Authorization": "Bearer %s" % get_access_token()}
    base, fname = os.path.split(filename)
    if not new_version:
        uri = '/files/content'
    else:
        # we need to get file id
        item = get_item(fname, parent_id)
        if item:
            id = item['id']
            uri = '/files/{0}/content'.format(id)
        else:
            # probably not found. we just upload in that case
            uri = '/files/content'

    data = {'filename': fname,
            'folder_id': parent_id}

    with open(filename, 'rb') as f:
        files = {'filename': f}
        
        r = requests.post(API_URI + uri,
                          headers=headers,
                          files=files,
                          data=data)
    return json.loads(r.text)


def copy(file_id, parent_id, newname=None):
    '''copy file with file_id to parent_id folder, possibly with a new name'''

    uri = '/files/{0}/copy'.format(file_id)
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    
    data = {'parent':{'id':parent_id}}
    if newname:
        data['name'] = newname

    r = requests.post(API_URI + uri,
                     headers=headers,
                     data=json.dumps(data))
    return json.loads(r.text)

## ------------------------COMMENTS----------------------------

def comment(id, message):
    '''Add a comment to file with id

    http://developers.box.com/docs/#comments-add-a-comment-to-an-item'''

    uri = '/comments'
    headers = {"Authorization": "Bearer %s" % get_access_token()}

    data = {'item': {'type': 'file', 'id': id}, 
            'message':message}

    r = requests.post(API_URI + uri,
                      headers=headers,
                      data=json.dumps(data))
    return json.loads(r.text)


def change_comment(comment_id, new_message):
    '''http://developers.box.com/docs/#comments-change-a-comments-message'''
    raise NotImplemented


def get_comment_information(comment_id):
    '''http://developers.box.com/docs/#comments-get-information-about-a-comment'''
    raise NotImplemented


def delete_comment(comment_id):
    '''http://developers.box.com/docs/#comments-delete-a-comment'''
    raise NotImplemented

##  ---------------------COLLABORATIONS------------------------

def add_collaboration(id, login, role):
    '''Add collaboration with login with role to id

    id should be a folder id
    login is the email address the person logs in with
    role is editor, viewer, etc...

    http://developers.box.com/docs/#collaborations-add-a-collaboration
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    data = {'item': {'id': id, 'type': 'folder'},
            'accessible_by':{'login':login},
            'role':role}

    uri = '/collaborations'

    r = requests.post(API_URI + uri,
                      headers=headers,
                      data=json.dumps(data))
    return json.loads(r.text)


def edit_collaboration(collab_id, role):
    '''
    I have not included the status option here.

    http://developers.box.com/docs/#collaborations-edit-a-collaboration
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/collaborations/{0}'.format(collab_id)
    data = {'role':role}

    r = requests.put(API_URI + uri,
                     headers=headers,
                     data=json.dumps(data))
    return json.loads(r.text)


def get_collaborations(folder_id):
    '''
    returns all collaborations on a folder

    http://developers.box.com/docs/#collaborations-retrieve-a-collaboration
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/folders/{0}/collaborations'.format(folder_id)
    r = requests.get(API_URI + uri,
                     headers=headers)
    return json.loads(r.text)


def get_collaboration(collab_id):
    '''
    get a specific collaboration by id.

    http://developers.box.com/docs/#collaborations-retrieve-a-collaboration
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/collaborations/{0}'.format(collab_id)
    r = requests.get(API_URI + uri,
                     headers=headers)
    return json.loads(r.text)    


def delete_collaboration(collab_id):
    '''http://developers.box.com/docs/#collaborations-remove-a-collaboration'''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/collaborations/{0}'.format(collab_id)
    r = requests.delete(API_URI + uri,
                        headers=headers)
    return json.loads(r.text)  


def get_pending_collaborations(status='pending'):
    '''http://developers.box.com/docs/#collaborations-get-pending-collaborations'''

    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/collaborations?status=pending'
    r = requests.get(API_URI + uri,
                     headers=headers)
    return json.loads(r.text)    



## -------------------------TASKS----------------------------

def create_task(id, message, due_at=None, action='review'):
    '''create a task on object with id, with message and
    with due_at

    due_at should be like '2013-04-17T09:12:36-00:00'
    http://developers.box.com/docs/#api-basics
    https://www.ietf.org/rfc/rfc3339.txt

    action should be 'review' it seems to be all the api supports. the
    web supports update and approve, but these values don't do
    anything here.

    http://developers.box.com/docs/#tasks-create-a-task
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/tasks'
    data = {'item':{'type':'file',
                    'id':id},
            'action':action,
            'message':message}
    if due_at:
        data['due_at'] = due_at

    # first create the task and get the id
    r = requests.post(API_URI + uri,
                      headers=headers,
                      data=json.dumps(data))

    return json.loads(r.text)


def update_task(id, message=None, due_at=None, action='review'):
    '''
    update the properties of a task

    http://developers.box.com/docs/#tasks-update-a-task
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/tasks/{0}'.format(id)
    data = {action:action}
    if message:
        data['message'] = message
    if due_at:
        data['due_at'] = due_at
    
    r = requests.put(API_URI + uri,
                     headers=headers,
                     data=json.dumps(data))
    return json.loads(r.text)    

def delete_task(id):
    '''
    delete a task by its id

    http://developers.box.com/docs/#tasks-delete-a-task
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/tasks/{0}'.format(id)
    r = requests.delete(API_URI + uri, headers=headers)
    if r.status_code == 204:
        return {}
    else:
        raise Exception('Could not delete {0}'.format(id))

def get_task_assignments(id):
    '''
    gets all the assignments for a task id

    http://developers.box.com/docs/#tasks-get-the-assignments-for-a-task
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/tasks/{0}/assignments'.format(id)
    r = requests.get(API_URI + uri, headers=headers)
    return json.loads(r.text)

def assign_task(task_id, login):
    '''
    assign a task to a login

    http://developers.box.com/docs/#tasks-create-a-task-assignment
    '''

    # now assign it
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    data = {'task':{'id':task_id,
                    'type':'task'},
            'assign_to':{'login':login}}
    
    uri = '/task_assignments'
    r = requests.post(API_URI + uri,
                      headers=headers,
                      data=json.dumps(data))
    
    return json.loads(r.text)

create_task_assignment = assign_task # an alias for consistency

   
def delete_task_assignment(id):
    '''
    http://developers.box.com/docs/#tasks-delete-a-task-assignment
    '''
    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/task_assignments/{0}'.format(id)
    r = requests.delete(API_URI + uri, headers=headers)
    if r.status_code == 204:
        return {}
    else:
        print r
        raise Exception('Could not delete {0}'.format(id))


def update_task_assignment(id, message, resolution_state=None):
    '''
    http://developers.box.com/docs/#tasks-update-a-task-assignment
    '''

    if resolution_state not in [None, 'completed','incomplete',
                                'approved','rejected']:
        raise Exception('invalid resolution state')

    headers = {"Authorization": "Bearer %s" % get_access_token()}
    uri = '/task_assignments/{0}'.format(id)
    data = {'message':message}
    if resolution_state:
        data['resolution_state'] = resolution_state

    r = requests.put(API_URI + uri,
                     headers=headers,
                     data=json.dumps(data))
    return json.loads(r.text)
