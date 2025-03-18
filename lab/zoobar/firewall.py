import rpclib
import socket
import sys
import os
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
import loger_client

SOCKET_PATH = "/firewall/firewall_socket.sock"


class FireWallRpcServer(rpclib.RpcServer):
    def rpc_check(self, ip):
        """Handle the check RPC call."""
        dbssesion = firewallDBsetup()
        result = dbssesion.query(ClientIP).filter_by(ip=ip).first()
        if not result:
            loger_client.log("firewall-service","check ip",ip,
                            "INFO",f"Ip {ip} have connection")
            return '1' 
        else:
            loger_client.log("firewall-service","check ip",ip,
                            "CRITICAL",f"Ip {ip} is blacklist and trying to connect")
            return '0'

    @staticmethod
    def ensure_directory_exists(sockpath):
        """Ensure the directory for the socket file exists."""
        directory = os.path.dirname(sockpath)
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o770)

ClientIPBase = declarative_base()

class ClientIP(ClientIPBase):
    __tablename__ = "client_ips"
    ip = Column(String, primary_key=True)
    
def firewallDBsetup():
    thisdir = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(thisdir, "firewallDB")
    # "firewallDB"
    DB_FILE = os.path.join(DB_DIR, "firewall.db")
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)
    ClientIPBase.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()



FireWallRpcServer.ensure_directory_exists(SOCKET_PATH)

# Run the server
server = FireWallRpcServer()
print(f"📡 Service is listening on {SOCKET_PATH}")
server.run_sockpath_fork(SOCKET_PATH)
