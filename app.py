#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from views import *
from config import DEBUG
from chat import XmppHandler

application = webapp.WSGIApplication(
    [
        ('/',Index),
        ('/help/',Help),
        ('/user/',Tool),
        ('/user/mardict\.xml', XMLExport),
        ('/user/import/', XMLImport),
        ('/_ah/xmpp/message/chat/', XmppHandler),
    ],
    debug=DEBUG,
)

def run():
    run_wsgi_app(application)

if "__main__" == __name__:
    run()
