from flask import g, redirect, render_template, request, url_for
from markupsafe import Markup
from functools import wraps
import os
from debug import *
from zoodb import *
import html  
import auth_client
import bank
import random
import json
import secrets
import hashlib


class User(object):
    def __init__(self):
        self.person = None

    def checkLogin(self, username, password):
        pepper = auth_client.get_pepper(username)
        if pepper is None: 
            return None
        hashed_password = self.hash_with_pepper(password, pepper)
        token = auth_client.login(username, hashed_password)
        if token is not None:
            return self.loginCookie(username, token)
        else:
            return None

    def loginCookie(self, username, token):
        self.setPerson(username, token)
        return "%s#%s" % (username, token)

    def logout(self):
        self.person = None

    def addRegistration(self, username, password):
        pepper = self.generate_pepper()
        hashed_password = self.hash_with_pepper(password, pepper)
        token = auth_client.register(username, hashed_password, pepper)
        if token is not None:
            return self.loginCookie(username, token)
        else:
            return None

    def checkCookie(self, cookie):
        if cookie is None:
            return
        if "#" not in cookie:
            return
        (username, token) = cookie.rsplit("#", 1)
        if auth_client.check_token(username, token):
            self.setPerson(username, token)

    def setPerson(self, username, token):
        temp = auth_client.get_person_and_profile(username)
        if temp:
            self.person = auth_client.Person_replasment(temp['username'], temp['profile'])
            self.token = token
            self.zoobars = bank.balance(username)

    def generate_pepper(self):
        """Generate a secure random pepper for a new user."""
        return secrets.token_hex(16)
        
    def hash_with_pepper(self, password, pepper):
        """Hashes the password with a prefix and a per-user pepper before sending to the server."""
        p = "b2f63adb9d54e625"
        combined_value = (p + password + pepper).encode('utf-8')
        return hashlib.pbkdf2_hmac('sha256', combined_value, b'', 100000).hex()



def logged_in():
    g.user = User()
    g.user.checkCookie(request.cookies.get("PyZoobarLogin"))
    if g.user.person:
        return True
    else:
        return False

def requirelogin(page):
    @wraps(page)
    def loginhelper(*args, **kwargs):
        if not logged_in():
            return redirect(url_for('login') + "?nexturl=" + request.url)
        else:
            return page(*args, **kwargs)
    return loginhelper

@catch_err
def login():
    cookie = None
    login_error = ""
    user = User()

    if request.method == 'POST':
        username = html.escape(request.form.get('login_username', ''))
        password = html.escape(request.form.get('login_password', ''))

        if 'submit_registration' in request.form:
            if not username:
                login_error = "You must supply a username to register."
            elif not password:
                login_error = "You must supply a password to register."
            else:
                cookie = user.addRegistration(username, password)
                if not cookie:
                    login_error = "Registration failed."
        elif 'submit_login' in request.form:
            if not username:
                login_error = "You must supply a username to log in."
            elif not password:
                login_error = "You must supply a password to log in."
            else:
                cookie = user.checkLogin(username, password)
                if not cookie:
                    login_error = "Invalid username or password."

    nexturl = request.values.get('nexturl', url_for('index'))
    if cookie:
        response = redirect(nexturl)
        ## Be careful not to include semicolons in cookie value; see
        ## https://github.com/mitsuhiko/werkzeug/issues/226 for more
        ## details.
        response.set_cookie('PyZoobarLogin', cookie)
        return response

    return render_template('login.html',
                       nexturl=nexturl,
                       login_error=login_error,
                       login_username=html.escape(request.form.get('login_username', '')))

@catch_err
def logout():
    if logged_in():
        g.user.logout()
    response = redirect(url_for('login'))
    response.set_cookie('PyZoobarLogin', '')
    return response
