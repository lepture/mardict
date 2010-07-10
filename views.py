#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db

from config import DIR, VERSION

from models import MBook

def myvalues(request):
    user = users.get_current_user()
    if user:
        st_url = users.create_logout_url(request.uri)
        st_text = 'Logout'
    else:
        st_url = users.create_login_url(request.uri)
        st_text = 'Login'
    values = {
        'user':user,
        'st_url':st_url,
        'st_text':st_text,
        'version': VERSION,
    }
    return values

class Index(webapp.RequestHandler):
    def get(self):
        values = myvalues(self.request)
        tp = os.path.join(DIR, 'index.html')
        self.response.out.write(template.render(tp,values))

class Help(webapp.RequestHandler):
    def get(self):
        values = myvalues(self.request)
        tp = os.path.join(DIR, 'help.html')
        self.response.out.write(template.render(tp,values))

class Tool(webapp.RequestHandler):
    def get(self):
        values = myvalues(self.request)
        xmppemail = values['user'].email().lower()
        sender = db.IM("xmpp", xmppemail)
        query = MBook.all()
        query.filter('im =', sender).order('-date')
        values['data'] = query
        tp = os.path.join(DIR, 'tool.html')
        self.response.out.write(template.render(tp,values))

class Log(webapp.RequestHandler):
    def get(self):
        values = myvalues(self.request)
        tp = os.path.join(DIR, 'tool.html')
        self.response.out.write(template.render(tp,values))

class XMLExport(webapp.RequestHandler):
    def get(self):
        values = myvalues(self.request)
        xmppemail = values['user'].email().lower()
        sender = db.IM("xmpp", xmppemail)
        query = MBook.all()
        query.filter('im =', sender).order('-date')
        values['data'] = query
        #self.response.headers['Content-Type'] = 'application/atom+xml'
        self.response.headers['Content-Type'] = 'binary/octet-stream'
        tp = os.path.join(DIR, 'mardict.xml')
        self.response.out.write(template.render(tp,values))
