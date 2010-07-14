#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.ext.webapp import xmpp_handlers

from utils.mardict import DictCN, GoogleDict
from utils.helper import *

from models import *

def star_rate(num):
    ''' 0 <= num <= 5'''
    num = str(num)
    d = {
        '0':u'☆☆☆☆☆',
        '1':u'☆☆☆☆★',
        '2':u'☆☆☆★★',
        '3':u'☆☆★★★',
        '4':u'☆★★★★',
        '5':u'★★★★★',
    }
    return d[num]

class Message:
    def __init__(self, message):
        self.__message = message
        self.sender = db.IM("xmpp", message.sender.split('/')[0].lower())

    def parse_cmd(self):
        content = self.__message.body
        sp = content.split()
        cmd = sp[0]
        if ':' == cmd[0]:
            cmd = cmd[1:]
            content = ' '.join(sp[1:])
        else:
            data = self.__nocmd(content)
            return data
        if '2' in cmd:
            data = self.__trans2(cmd,content)
            return data
        elif 'dict' == cmd:
            data = self.__dict(content)
            return data
        elif 'google' == cmd:
            data = self.__google(content)
            return data
        elif 'add' == cmd:
            sender = self.sender
            data = self.__add(sender, content)
            return data
        elif 'del' == cmd:
            sender = self.sender
            data = self.__del(sender, content)
            return data
        elif 'list' == cmd:
            sender = self.sender
            data = self.__list(sender, content)
            return data
        elif 'rating' == cmd:
            sender = self.sender
            data = self.__rating(sender, content)
            return data
        elif 'history' == cmd:
            sender = self.sender
            data = self.__history(sender, content)
            return data
        elif 'clear' == cmd:
            sender = self.sender
            data = self.__clear(sender)
            return data
        elif 'help' == cmd:
            data = self.__help(content)
            return data
        else:
            return 'Undefined command'

    def __dict(self,content):
        if not content:
            reply = 'You asked nothing'
            return reply
        d = DictCN(content)
        response = d.get_response()
        if response:
            data = response
            reply = '%s [%s]\nfrom: dict.cn\n%s' % \
                    (data['word'], data['pron'], data['define'])

            sender = self.sender
            DictLog.add_record(sender, data['word'], data['define'], data['pron'])
        else:
            reply = 'Not Found'
        return reply

    def __google(self,content):
        if not content:
            return 'You asked nothing'
        g = GoogleDict(content)
        response = g.get_response()
        if response:
            data = response
            reply = '%s\nfrom: google\n%s' % \
                    (data['word'], data['define'])
        else:
            reply = 'Not Found'
        return reply

    def __trans2(self,cmd,content):
        lan = cmd.split('2')
        lan1 = lan[0]
        lan2 = lan[1]
        g  = GoogleDict(content,lan1,lan2)
        response = g.get_response()
        if response:
            data = response
            reply = '%s\nfrom: google\n%s' % \
                    (data['word'], data['define'])
        else:
            reply = 'Not Found'
        return reply

    def __nocmd(self, content):
        if 1 == len(content.split()):
            response = DictCN(content).get_response()
            if response:
                data = response
                reply = '%s [%s]\nfrom: dict.cn\n%s' % \
                        (data['word'], data['pron'], data['define'])
                sender = self.sender
                if 'help' == content:
                    reply += '\nNeed help? Type ":help" for more infomation.'
                else:
                    DictLog.add_record(sender, data['word'], data['define'], data['pron'])
                return reply
        g = GoogleDict(content)
        lan = g.detect_language()
        lan1 = lan
        lan2 = 'zh'
        if ('zh-CN' or 'zh-TW') == lan:
            lan2 = 'en'
        g = GoogleDict(content,lan1,lan2)
        response = g.get_response()
        reply = 'Not Found'
        if response:
            data = response
            reply = '%s\nfrom: google\n%s' % \
                    (data['word'], data['define'])
        return reply

    def __add(self, sender, content):
        if content:
            mb = MBook.get_record(sender, content)
            if 0 == len(mb):
                trans = DictCN(content).get_response()
                if trans:
                    MBook.add_record(sender, trans['word'], trans['define'], trans['pron'])
                    reply = '"%s" has added to your libarary\n\n%s [%s]\n%s' % \
                            (trans['word'], trans['word'], trans['pron'], trans['define'])
                else:
                    reply = 'Something Wrong Happened. Cannot find the word'
            else:
                m = mb[0]
                if m.rating < 5:
                    m.rating += 1
                    m.put()
                    reply = u'You added "%s" before\n\n%s\n%s [%s]\n%s' % \
                            (star_rate(m.rating), m.word, m.word, m.pron, m.define)
                else:
                    reply = u'You added "%s" more than 5 times\n\n%s\n%s [%s]\n%s' % \
                            (star_rate(m.rating), m.word, m.word, m.pron, m.define)
        else:
            log = DictLog.get_record(sender)
            if 0 == len(log):
                reply = 'You add nothing'
            else:
                data = log[0]
                MBook.add_record(sender, data.word, data.define, data.pron)
                reply = '"%s" has added to your libarary\n\n%s [%s]\n%s' %\
                        (data.word, data.word, data.pron, data.define)
        return reply

    def __del(self, sender, content):
        if content:
            mb = MBook.get_record(sender, content)
            if 0 == len(mb):
                reply = '"%s" not in your libarary' % content
            else:
                m = mb[0]
                m.delete()
                reply = '"%s" has been deleted' % content
        else:
            reply = 'Usage:\n:del word'
        return reply

    def __list(self, sender, content):
        old = False
        offset = 0
        count = 10
        if content:
            c1 = content.split()
            if "-" == c1[-1]:
                old = True
            if (len(c1) >= 1) and ('-' != c1[0]) :
                c2 = c1[0].split('-')
                if len(c2) > 1:
                    try:
                        offset = int(c2[0])
                        count = int(c2[1]) - offset
                    except ValueError:
                        offset = 0
                        count = 10
                else:
                    try:
                        count = int(c2[0])
                    except ValueError:
                        count = 10
        if old:
            lib = MBook.list_old_record(sender, offset, count)
            reply = 'list by oldest: (from: %s)\n\n' % offset
        else:
            lib = MBook.list_record(sender, offset, count)
            reply = 'list by newest: (from :%s)\n\n' % offset
        for m in lib:
            reply += u'%s\n%s [%s]\n%s\n\n' %\
                    (star_rate(m.rating), m.word, m.pron, m.define)
        return reply

    def __rating(self, sender, content):
        old = False
        rate = 0
        offset = 0
        count = 10
        if content:
            c1 = content.split()
            if '-' == c1[-1]:
                old = True
            try:
                rate = int(c1[0])
            except ValueError:
                rate = 0
            if len(c1) > 1 and '-' != c1[1]:
                c2 = c1[1].split('-')
                if len(c2) > 1:
                    try:
                        offset = int(c2[0])
                        count = int(c2[1]) - offset
                    except ValueError:
                        offset = 0
                        count = 10
                else:
                    try:
                        count = int(c2[0])
                    except ValueError:
                        count = 10
        if old:
            lib = MBook.rating_old_record(sender, rate, offset, count)
            reply = u'rating by oldest: (from:%s)\n%s \n\n' % (offset,star_rate(rate))
        else:
            lib = MBook.rating_record(sender, rate, offset, count)
            reply = u'rating by newest: (from:%s)\n%s \n\n' % (offset,star_rate(rate))
        for m in lib:
            reply += '%s [%s]\n%s\n\n' % (m.word, m.pron, m.define)
        return reply

    def __history(self, sender, content):
        try:
            count = int(content)
        except ValueError:
            count = 10
        logs = DictLog.list_record(sender, count)
        reply = 'history:\n'
        for m in logs:
            reply += '%s [%s]\n%s\n\n' % (m.word, m.pron, m.define)
        return reply

    def __clear(self, sender):
        DictLog.destroy(sender)
        reply = 'History cleared'
        return reply

    def __help(self, content):
        if not content:
            reply = help_txt
        elif 'lan2lan' == content:
            reply = help_lan2lan
        elif 'dict' == content:
            reply = help_dict
        elif 'google' == content:
            reply = help_google
        elif 'add' == content:
            reply = help_add
        elif 'del' == content:
            reply = help_del
        elif 'list' == content:
            reply = help_list
        elif 'rating' == content:
            reply = help_rating
        elif 'history' == content:
            reply = help_history
        elif 'clear' == content:
            reply = help_clear
        return reply

class XmppHandler(xmpp_handlers.CommandHandler):
    def text_message(self, message=None):
        if message:
            m = Message(message)
            reply = m.parse_cmd()
            message.reply(reply)
        else:
            message.reply('You Asked Nothing')

    def unhandled_command(self, message=None):
        message.reply('type :help to get more info')
