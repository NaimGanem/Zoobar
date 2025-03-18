#!/usr/bin/env python2
#
# Insert bank server code here.
#
#!/usr/bin/env python3

import rpclib
import os
import sys
import time
from debug import *
from zoodb import *
import random
import loger_client


class BankRpcServer(rpclib.RpcServer):
    def rpc_transfer(self, sender, recipient, zoobars):
        """Handle the transfer RPC call."""
        bankdb = bank_setup()
        senderp = bankdb.get(Bank, sender)
        recipientp = bankdb.get(Bank, recipient)

        if zoobars <= 0 :
            loger_client.log("bank-service","transfer",sender,"WARNING",f"User {sender} tried to transfer 0 or negative zoobars.")
            return {"error": "Cannot transfer negative or zero zoobars."}

        if recipientp is None:
            loger_client.log("bank-service","transfer",sender,"ERROR",f"User {sender} tried to transfer {zoobars} to user {recipient} , User {recipient} not exist.")
            return {"error": "User not exist."}

        sender_balance = senderp.zoobars - zoobars
        recipient_balance = recipientp.zoobars + zoobars
        
        if sender_balance < 0 or recipient_balance < 0:
            loger_client.log("bank-service","transfer",sender,"ERROR",f"User {sender} or user {recipient} will have negative zoobars after the transfer.")
            return {"error": "Insufficient funds."}

        if sender != recipient:
            senderp.zoobars = sender_balance
            recipientp.zoobars = recipient_balance
            bankdb.commit()

        transfer = Transfer()
        transfer.sender = sender
        transfer.recipient = recipient
        transfer.amount = zoobars
        transfer.time = time.asctime()

        transferdb = transfer_setup()
        transferdb.add(transfer)
        transferdb.commit()
        loger_client.log("bank-service","transfer",sender,"INFO",f"User {sender} have transfered {zoobars} zoobars to {recipient}")

    def rpc_balance(self, username):
        """Handle the balance RPC call."""
        bankdb = bank_setup()
        person = bankdb.get(Bank, username)
        loger_client.log("bank-service","balance",username,"INFO",f"User {username} request balance and have {person.zoobars} zoobars")
        return person.zoobars

    def rpc_add_user_to_bank(self, username):
        """Handle adding new user register RPC call."""
        db_bank = bank_setup()
        person_bank = db_bank.get(Bank, username)
        if person_bank:
            loger_client.log("bank-service","add user to bank",username,"ERROR",f"User {username} allredy exist in bank db")
            return None  # User already exists
        newbank = Bank(username=username)
        db_bank.add(newbank)
        db_bank.commit()
        loger_client.log("bank-service","add user to bank",username,"INFO",f"User {username} have been added to bank db")

    def rpc_get_log(self, username):
        """Validate the get_log for the user."""
        db = transfer_setup()
        loger_client.log("bank-service","get log",username,"INFO",f"User {username} requesed transfer logs")
        l = db.query(Transfer).filter(or_(Transfer.sender==username,
                                        Transfer.recipient==username))
        r = []
        for t in l:
            r.append({'time': t.time,
                        'sender': t.sender ,
                        'recipient': t.recipient,
                        'amount': t.amount })
        return r 

    @staticmethod
    def ensure_directory_exists(sockpath):
        """Ensure the directory for the socket file exists."""
        directory = os.path.dirname(sockpath)
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o777) 

# Ensure the script has valid arguments
if len(sys.argv) < 3:
    print("Usage: script.py dummy_zookld_fd sockpath")
    sys.exit(1)

_, dummy_zookld_fd, sockpath = sys.argv

# Ensure the socket directory exists
BankRpcServer.ensure_directory_exists(sockpath)

# Run the server
server = BankRpcServer()
print(f"📡 Service is listening on {sockpath}")
server.run_sockpath_fork(sockpath)
