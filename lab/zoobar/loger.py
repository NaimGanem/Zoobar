import rpclib
import socket
import sys
import os
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta, timezone



SOCKET_PATH = "/loger/loger_socket.sock"

class logerRpcServer(rpclib.RpcServer):
    def rpc_log(self,service_name, action, username, log_level, message):
        """Handle the log RPC call."""
        dbsession = logDBsetup()
        new_log = Log(
            service_name=service_name,
            action=action,
            username=username,
            log_level=log_level,
            message=message
        )
        dbsession.add(new_log)
        try:
            dbsession.commit()  
            return {"status": "success", "message": "Log entry added successfully"}
        except Exception as e:
            dbsession.rollback()  
            return {"status": "error", "message": str(e)}
        finally:
            dbsession.close() 

    def rpc_check_failed_logins(self, username):
        """Check if the user has failed to log in 3 times in the last minute."""
        dbsession = logDBsetup()
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

        failed_attempts = dbsession.query(Log).filter(
            Log.service_name == "auth-service",
            Log.action == "login",
            Log.username == username,
            Log.log_level == "ERROR",
            Log.message.like(f"%Wrong password%"),  
            Log.timestamp >= one_minute_ago
        ).count()

        dbsession.close()

        return failed_attempts >= 3
    @staticmethod
    def ensure_directory_exists(sockpath):
        """Ensure the directory for the socket file exists."""
        directory = os.path.dirname(sockpath)
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o777)

LogBase = declarative_base()

class Log(LogBase):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(100))
    action = Column(String(50))
    username = Column(String(50))
    log_level = Column(String(10))
    message = Column(Text)
    timestamp = Column(DateTime, default=func.now())

def logDBsetup():
    thisdir = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(thisdir, "log")
    DB_FILE = os.path.join(DB_DIR, "log.db")
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)
    LogBase.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()

logerRpcServer.ensure_directory_exists(SOCKET_PATH)

# Run the server
server = logerRpcServer()
print(f"📡 Service is listening on {SOCKET_PATH}")
server.run_sockpath_fork(SOCKET_PATH)


