#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db

from config import DIR, VERSION
from models import MBook, DictLog
from utils.parsexml import MarXML
from utils.paginator import pagi

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

class User(webapp.RequestHandler):
    def get(self):
        count = 10
        p = self.request.get('p',1)
        values = myvalues(self.request)
        xmppemail = values['user'].email().lower()
        sender = db.IM("xmpp", xmppemail)

        action = self.request.get('action','none')
        key = self.request.get('key','none')
        if action != 'none' and key != 'none':
            m = db.get(key)
            if m.im == sender:
                db.delete(m)
            self.redirect('/user/')

        query = MBook.all()
        query.filter('im =', sender).order('-date')
        values['data'] = pagi(query, count, p)
        tp = os.path.join(DIR, 'user.html')
        self.response.out.write(template.render(tp,values))

class History(webapp.RequestHandler):
    def get(self):
        count = 15
        p = self.request.get('p',1)
        values = myvalues(self.request)
        xmppemail = values['user'].email().lower()
        sender = db.IM("xmpp", xmppemail)

        action = self.request.get('action','none')
        key = self.request.get('key','none')
        if action != 'none' and key != 'none':
            m = db.get(key)
            if m.im == sender:
                db.delete(m)
            self.redirect('/user/')

        query = DictLog.all()
        query.filter('im =', sender).order('-date')
        values['data'] = pagi(query, count, p)
        tp = os.path.join(DIR, 'history.html')
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

class XMLImport(webapp.RequestHandler):
    def get(self):
        values = myvalues(self.request)
        tp = os.path.join(DIR, 'import.html')
        self.response.out.write(template.render(tp,values))
    def post(self):
        values = myvalues(self.request)
        xmppemail = values['user'].email().lower()
        sender = db.IM("xmpp", xmppemail)
        marfile = self.request.get('marfile')
        mar = MarXML(marfile)
        content = mar.parse_data()
        for m in content:
            mdb = MBook.add_record(sender,m['word'], m['define'], m['pron'])
            mdb.date = m['date']
            mdb.put()
        #self.response.out.write(content)
        self.redirect('/user/')


class Error404(webapp.RequestHandler):
    def get(self):
        self.error(404)
        #self.response.out.write('Not Found')
