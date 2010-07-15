#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from config import DIR, VERSION
from models import MBook, DictLog
from utils.parsexml import MarXML
from utils.paginator import pagi

def myvalues(request):
    user = users.get_current_user()
    if user:
        user.admin = users.is_current_user_admin()
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
        count = 15
        p = self.request.get('p',1)
        values = myvalues(self.request)
        xmppemail = values['user'].email().lower()
        sender = db.IM("xmpp", xmppemail)
        dictkey = xmppemail + '$dict'

        action = self.request.get('action')
        key = self.request.get('key')
        if key and 'delete' == action:
            memcache.delete(dictkey)
            m = db.get(key)
            if m and m.im == sender:
                db.delete(m)
            self.redirect('/user/')
        if 'refresh' == action:
            memcache.delete(dictkey)
            self.redirect('/user/')
        data = memcache.get(dictkey)
        if not data:
            query = MBook.all()
            query.filter('im =', sender).order('-date')
            data = []
            for item in query:
                data.append(dict(
                    key = item.key(),
                    word = item.word,
                    pron = item.pron,
                    define = item.define,
                    rating = item.rating,
                    date = item.date,
                ))
            memcache.set(dictkey, data, 86400)
        values['data'] = pagi(data, count, p)
        tp = os.path.join(DIR, 'user.html')
        self.response.out.write(template.render(tp,values))

class History(webapp.RequestHandler):
    def get(self):
        count = 15
        p = self.request.get('p',1)
        values = myvalues(self.request)
        xmppemail = values['user'].email().lower()
        sender = db.IM("xmpp", xmppemail)
        histkey = xmppemail + '$hist'

        action = self.request.get('action')
        key = self.request.get('key')
        if key and 'delete' == action:
            memcache.delete(histkey)
            m = db.get(key)
            if m and m.im == sender:
                db.delete(m)
            self.redirect('/user/history/')
        if 'refresh' == action:
            memcache.delete(histkey)
            self.redirect('/user/history/')
        data = memcache.get(histkey)
        if not data:
            query = DictLog.all()
            query.filter('im =', sender).order('-date')
            data = []
            for item in query:
                data.append(dict(
                    key = item.key(),
                    word = item.word,
                    pron = item.pron,
                    define = item.define,
                    date = item.date,
                ))
            memcache.set(histkey, data, 3600)
        values['data'] = pagi(data, count, p)
        tp = os.path.join(DIR, 'history.html')
        self.response.out.write(template.render(tp,values))


class God(webapp.RequestHandler):
    def get(self):
        action = self.request.get('action')
        if 'flush' == action:
            memcache.flush_all()
            self.redirect('/god/')
        values = myvalues(self.request)
        memstat = memcache.get_stats()
        age = int(memstat['oldest_item_age'])
        if age < 60:
            age = '%d s' % age
        elif age < 3600:
            age = '%d min' % (age/60)
        elif age < 86400:
            age = '%d hour' % (age/3600)
        else:
            age = '%d day' % (age/86400)
        memstat['age'] = age
        values['memstat'] = memstat
        tp = os.path.join(DIR, 'god.html')
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
