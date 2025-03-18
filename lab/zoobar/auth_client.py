import rpclib

SOCKET_PATH = "/tmp/authsvc.sock"  

class Person_replasment:
    def __init__(self, username="", profile=""):
        self.username = username
        self.profile = profile

def login(username, password):
    """Call the login RPC method."""
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('login', username=username, password=password)

def register(username, password, pepper):
    """Call the register RPC method."""
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('register', username=username, password=password, pepper=pepper)

def check_token(username, token):
    """Call the check_token RPC method."""
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('check_token', username=username, token=token)

def get_person_and_profile(username):
    """Call the get_person_and_profile RPC method."""
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('get_person_and_profile', username=username)

def update_profile(username, profile):
    """Call the update_profile RPC method."""
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('update_profile', username=username, profile=profile)

def get_pepper(username):
    """Call the get_pepper RPC method."""
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('get_pepper', username=username)

