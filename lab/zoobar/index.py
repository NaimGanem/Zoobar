from flask import g, render_template, request
from login import requirelogin
from debug import *
from zoodb import *
import auth_client

@catch_err
@requirelogin
def index():
    if 'profile_update' in request.form:
        profile = request.form['profile_update']
        username = g.user.person.username
        auth_client.update_profile(username, profile)
        g.user.person.profile = profile
    return render_template('index.html')
