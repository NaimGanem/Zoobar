import rpclib

SOCKET_PATH = "/loger/loger_socket.sock"

def log(service_name, action, username, log_level, message):
    """Send a log entry via RPC"""
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call("log", service_name=service_name, action=action, username=username, log_level=log_level, message=message)

def check_failed_logins(username):
    """Send a log entry via RPC"""
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call("check_failed_logins", username=username)