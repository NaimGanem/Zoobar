from flask import g, render_template, request

from login import requirelogin
from zoodb import *
from debug import *
import bank
import traceback

@catch_err
@requirelogin
def transfer():
    warning = None
    try:
        if 'recipient' in request.form:
            zoobars = int(request.form['zoobars'])
            res = bank.transfer(g.user.person.username,
                          request.form['recipient'], zoobars)
            if 'error' in res:
                warning = res['error']
            else:
                warning = "Sent %d zoobars" % zoobars
    except (KeyError, ValueError, AttributeError) as e:
        traceback.print_exc()
        warning = "Transfer to %s failed" % request.form['recipient']

    return render_template('transfer.html', warning=warning)
