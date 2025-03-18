#!/usr/bin/env python3

import rpclib
import os
import sys
from debug import *
from zoodb import *
import hashlib
import random
import bank
import json
import loger_client
import secrets

class AuthRpcServer(rpclib.RpcServer):
    def rpc_login(self, username, password):
        """Handle the login RPC call."""
        db = Cred_setup()
        user = db.get(Cred, username)
        if not user:
            loger_client.log("auth-service","login",username,"ERROR",f"User {username} not exist")
            return None
        res = loger_client.check_failed_logins(username)
        if res :
            loger_client.log("auth-service","login",username,"CRITICAL",f"User {username} is temporarily blocked due to multiple failed login attempts.")
            return None
        username_and_password = (password + username + user.salt).encode('utf-8')
        hash_pass = hashlib.pbkdf2_hmac('sha256', username_and_password, b'', 100000).hex()
        if user.password == hash_pass:
            loger_client.log("auth-service","login",username,"INFO",f"User {username} logged in successfully")
            return self.newtoken(db, user)
        else:
            loger_client.log("auth-service","login",username,"ERROR",f"Wrong password for {username}")
            return None

    def rpc_register(self, username, password, pepper):
        """Handle the register RPC call."""
        db_person = person_setup()
        person = db_person.get(Person, username)
        if person:
            loger_client.log("auth-service","register",username,"ERROR",f"User {username} already exists")
            return None  # User already exists
        newperson = Person(username=username)
        db_person.add(newperson)
        db_person.commit()
        # bank handling:
        bank.add_user_to_bank(username)
        salt = secrets.token_hex(16)
        username_and_password = (password + username + salt).encode('utf-8')
        hash_pass = hashlib.pbkdf2_hmac('sha256', username_and_password, b'', 100000).hex()
        db = Cred_setup()
        new_cred = Cred(username=username, password=hash_pass, salt=salt, pepper=pepper)
        db.add(new_cred)
        db.commit()
        loger_client.log("auth-service","register",username,"INFO",f"User {username} have registered")
        return self.newtoken(db, new_cred)

    def rpc_check_token(self, username, token):
        """Validate the token for the user."""
        db = Cred_setup()
        person = db.get(Cred, username)
        if person and person.token == token:
            return True
        else:
            return False

    def newtoken(self, db, cred):
        """Generate a new token for the user."""
        hashinput = "%s%.10f" % (cred.password, random.random())
        cred.token = hashlib.sha256(hashinput.encode('utf-8')).hexdigest()
        db.commit()
        return cred.token
    
    def rpc_get_person_and_profile(self, username):
        """Get person form cred db."""
        db_person = person_setup()
        person = db_person.get(Person, username)
        if person:
            temp = {"username": person.username, "profile": person.profile}
        else:
            temp = None
        return temp

    def rpc_get_pepper(self, username):
        """Get pepper from cred db."""
        db_cred = Cred_setup()
        person = db_cred.get(Cred, username)
        if not person:
            return None
        return person.pepper
    
    


    def rpc_update_profile(self, username, profile):
        """Update profile for person form person db."""
        db_person = person_setup()
        person = db_person.get(Person, username)
        if person:
            person.profile = profile
            db_person.commit()  
            loger_client.log("auth-service","update profile",username,"INFO",f"User {username} have updated the profile")


    @staticmethod
    def ensure_directory_exists(sockpath):
        """Ensure the directory for the socket file exists."""
        directory = os.path.dirname(sockpath)
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o777)  # Create with permissions for user and group

# Ensure the script has valid arguments
if len(sys.argv) < 3:
    print("Usage: script.py dummy_zookld_fd sockpath")
    sys.exit(1)

_, dummy_zookld_fd, sockpath = sys.argv

# Ensure the socket directory exists
AuthRpcServer.ensure_directory_exists(sockpath)

# Run the server
server = AuthRpcServer()
print(f"📡 Service is listening on {sockpath}")
server.run_sockpath_fork(sockpath)
