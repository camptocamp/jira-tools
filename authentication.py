from jira import JIRA
from github3 import authorize
from github3 import login
from getpass import getpass, getuser
from subprocess import check_output
import sys
import json
import os


# By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK
# (see https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK for details).
# Override this with the options parameter.

def jira_connection():
    """ Connect to Jira
        Using this method, authentication happens during the initialization
         of the object. If the authentication is successful, the retrieved
         session cookie will be used in future requests. Upon cookie
         expiration, authentication will happen again transparently.
    """
    with open('config.json') as conf:
        options = json.load(conf)

    username = os.environ.get('USER')
    password = getpass(prompt='Your Jira password: ')
    auth = (username, password)

    return JIRA(options=options, auth=auth)


def github_connection():
    """ Connect to GitHub API with token creation if needed
    """
    try:
        import readline
    except ImportError:
        pass

    if not os.path.isfile('CREDENTIALS_FILE'):
        # Part to create CREDENTIALS_FILE with github token
        try:
            user = check_output(['git', 'config', 'user.name'])[:-1].decode()
        except KeyboardInterrupt:
            user = getuser()

        password = getpass('GitHub password for {0}: '.format(user))

        # Obviously you could also prompt for an OAuth token
        if not (user and password):
            print("Refuses to login without username and password.")
            sys.exit(1)

        note = 'Camptocamp Jira tools'
        note_url = ''
        scopes = ['user', 'repo']

        auth = authorize(user, password, scopes, note, note_url)

        with open('CREDENTIALS_FILE', 'w') as fd:
            fd.write(auth.token + '\n')
            fd.write(str(auth.id))

    # Use token already created
    token = ''
    with open('CREDENTIALS_FILE', 'r') as fd:
        token = fd.readline().strip()  # Can't hurt to be paranoid

    return login(token=token)
