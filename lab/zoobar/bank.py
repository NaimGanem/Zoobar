import rpclib

SOCKET_PATH = "/tmp/banksvc.sock"  

def transfer(sender, recipient, zoobars):
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('transfer', sender=sender, recipient=recipient, zoobars=zoobars)



def balance(username):
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('balance', username=username)

def get_log(username):
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('get_log', username=username)

def add_user_to_bank(username):
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('add_user_to_bank', username=username)