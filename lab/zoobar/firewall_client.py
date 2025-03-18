import rpclib

SOCKET_PATH = "/firewall/firewall_socket.sock" 

def check(ip):
    """Call the login RPC method."""
    with rpclib.client_connect(SOCKET_PATH) as c:
        return c.call('check', ip=ip)