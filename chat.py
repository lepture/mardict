#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.ext.webapp import xmpp_handlers

from mardict import DictCN, GoogleDict

from models import *

class Message:
    def __init__(self, message):
        self.__message = message

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
            message = self.__message
            sender = db.IM("xmpp", message.sender.split('/')[0])
            data = self.__add(sender, content)
            return data
        elif 'del' == cmd:
            message = self.__message
            sender = db.IM("xmpp", message.sender.split('/')[0])
            data = self.__del(sender, content)
            return data
        elif 'list' == cmd:
            message = self.__message
            sender = db.IM("xmpp", message.sender.split('/')[0])
            data = self.__list(sender, content)
            return data
        elif 'rating' == cmd:
            message = self.__message
            sender = db.IM("xmpp", message.sender.split('/')[0])
            data = self.__rating(sender, content)
            return data
        elif 'help' == cmd:
            data = self.__help()
            return data
        else:
            return 'Undefined command'

    def __dict(self,content):
        d = DictCN(content)
        response = d.get_response()
        if response:
            data = response
            reply = '%s [%s]\nfrom: dict.cn\n%s' % \
                    (data['key'], data['pron'], data['define'])
        else:
            reply = 'Not Found'
        return reply

    def __google(self,content):
        g = GoogleDict(content)
        response = g.get_response()
        if response:
            data = response
            reply = '%s\nfrom: google\n%s' % \
                    (data['key'], data['define'])
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
                    (data['key'], data['define'])
        else:
            reply = 'Not Found'
        return reply

    def __nocmd(self, content):
        response = DictCN(content).get_response()
        if response:
            data = response
            reply = '%s [%s]\nfrom: dict.cn\n%s' % \
                    (data['key'], data['pron'], data['define'])
        else:
            g = GoogleDict(content)
            lan = g.detect_language()
            if ('zh-CN' or 'zh-TW') == lan:
                lan1 = lan
                lan2 = 'en'
            else:
                lan1 = lan
                lan2 = 'zh'
            g = GoogleDict(content,lan1,lan2)
            response = g.get_response()
            if response:
                data = response
                reply = '%s\nfrom: google\n%s' % \
                        (data['key'], data['define'])
            else:
                reply = 'Not Found'
        return reply

    def __add(self, sender, content):
        if content:
            mb = MBook.get_record(sender, content)
            if 0 == len(mb):
                trans = DictCN(content).get_response()
                if trans:
                    MBook.add_record(sender, trans['key'], trans['define'], trans['pron'])
                    reply = '"%s" has added to your libarary\n\n%s [%s]\n%s' % \
                            (trans['key'], trans['key'], trans['pron'], trans['define'])
                else:
                    reply = 'Something Wrong Happened. Cannot find the word'
            else:
                m = mb[0]
                if m.rating < 5:
                    m.rating += 1
                    m.put()
                    reply = 'You had added it before'
                else:
                    reply = 'You have added 5 times'
        else:
            reply = 'Usage:\n:add word'
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
        try:
            count = int(content)
        except ValueError:
            count = 10
        lib = MBook.list_record(sender, count)
        reply = 'list:\n'
        for m in lib:
            reply += '%s [%s]\n%s\n\n' % (m.word, m.pron or 'google', m.define)
        return reply

    def __rating(self, sender, content):
        if content:
            cmd = content.split()
            try:
                rate = int(cmd[0])
            except:
                rate = 0
            try:
                count = int(cmd[1])
            except:
                count = 10
        else:
            rate = 0
            count = 10
        lib = MBook.rating_record(sender, rate, count)
        reply = 'rating: %s\n' % rate
        for m in lib:
            reply += '%s [%s]\n%s\n\n' % (m.word, m.pron or 'google', m.define)
        return reply

    def __help(self):
        reply = ':help, this help menu\n'
        reply += ':xx2xx, eg: en2zh, zh2ja, en2ja\n'
        reply += ':dict, only find translation on dict.cn\n'
        reply += ':google, only find translation on google\n'
        reply += ':add, add new word to your library\n'
        reply += ':del, delete word from your library\n'
        reply += ':list, list words in your library\n'
        reply += ':rating, list  words in your library\n'
        return reply



class XmppHandler(xmpp_handlers.CommandHandler):
    def text_message(self, message=None):
        if message:
            m = Message(message)
            reply = m.parse_cmd()
            message.reply(reply)
        else:
            message.reply('You Asked Nothing')

    def add_command(self, message=None):
        sender = message.sender.split('/')[0]
        im_from = db.IM("xmpp", sender)
        if message.arg:
            mb = MBook.get_record(im_from, message.arg)
            if 0 == len(mb):
                trans = parse_message(message.arg)
                if trans:
                    MBook.add_record(im_from, trans['key'], trans['define'], trans['pron'])
                    reply = '"%s" has added to your libarary' % trans['key']
                    message.reply(reply)
                else:
                    message.reply('Something Wrong Happened. Cannot find the word')
            else:
                m = mb[0]
                if m.rating < 6:
                    m.rating += 1
                    m.put()
                    message.reply('You had added it before')
                else:
                    message.reply('You have added 6 times')
        else:
            message.reply('usage:\n/add yourword')

    def del_command(self, message=None):
        sender = message.sender.split('/')[0]
        im_from = db.IM("xmpp", sender)
        if message.arg:
            mb = MBook.get_record(im_from, message.arg)
            if 0 == len(mb):
                message.reply('"%s" not in your libarary' % message.arg)
            else:
                m = mb[0]
                m.delete()
                message.reply('"%s" has been deleted' % message.arg)
        else:
            message.reply('usage:\n/del yourword')

    def list_command(self, message=None):
        sender = message.sender.split('/')[0]
        im_from = db.IM("xmpp", sender)
        if message.arg:
            try:
                count = int(message.arg)
            except ValueError:
                count = 10
        else:
            count = 10
        lib = MBook.list_record(im_from, count)
        reply = 'list:\n'
        for m in lib:
            reply += '%s [%s]\n%s\n\n' % (m.word, m.pron or 'google', m.define)
        message.reply(reply)

    def rating_command(self, message=None):
        sender = message.sender.split('/')[0]
        im_from = db.IM("xmpp", sender)
        if message.arg:
            cmd = message.arg.split()
            try:
                rate = int(cmd[0])
            except ValueError:
                rate = 0
            try:
                count = int(cmd[1])
            except:
                count = 10
        else:
            rate = 0
            count = 10
        lib = MBook.rating_record(im_from, rate, count)
        reply = 'rating:%s\n' % rate
        for m in lib:
            reply += '%s [%s]\n%s\n\n' % (m.word, m.pron or 'google', m.define)
        message.reply(reply)
    
    def help_command(self, message=None):
        help_info = '/help, this help menu\n'
        help_info += '/dict (word), translation\n'
        help_info += '/add (word), add word to your libarary\n'
        help_info += '/del (word), del word from your libarary\n'
        help_info += '/list (number), list your recent 10 words from libarary\n'
        help_info += '/rating (number) (number), list your rating words\n'
        if message:
            cmd = message.arg or ''
            if cmd:
                reply = 'No info for %s now' % cmd
                message.reply(reply)
            else:
                message.reply(help_info)
        else:
            message.reply('You Asked Nothing')

    def unhandled_command(self, message=None):
        message.reply('type /help to get more info')
