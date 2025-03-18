from flask import g, render_template, request
from markupsafe import Markup

from login import requirelogin
from zoodb import *
from debug import *
import bank
import auth_client

@catch_err
@requirelogin
def users():
    args = {}
    args['req_user'] = Markup.escape(request.args.get('user', ''))
    if 'user' in request.values:
        temp = auth_client.get_person_and_profile(request.values['user'])
        if temp:
            user = auth_client.Person_replasment(temp['username'], temp['profile'])
        else : 
            user = None 
            
        if user: 
            p = user.profile

            p_markup = Markup.escape("%s" % p)
            args['profile'] = p_markup

            args['user'] = user
            args['user_zoobars'] = bank.balance(user.username)
            args['transfers'] = bank.get_log(user.username)
        else:
            args['warning'] = "Cannot find that user."
    return render_template('users.html', **args)
