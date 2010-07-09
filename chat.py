#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.ext.webapp import xmpp_handlers

from mardict import DictCN, GoogleDict

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
        self.sender = db.IM("xmpp", message.sender.split('/')[0])

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
                    (data['key'], data['pron'], data['define'])

            sender = self.sender
            DictLog.add_record(sender, data['key'], data['define'], data['pron'])
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
            sender = self.sender
            if 'help' == content:
                reply += '\nNeed help? Type ":help" for more infomation.'
            else:
                DictLog.add_record(sender, data['key'], data['define'], data['pron'])
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
        if content:
            c1 = content.split()
            if len(c1) > 1:
                if '-' == c1[1]:
                    old = True
            c2 = c1[0].split('-')
            if len(c2) > 1:
                try:
                    offset = int(c2[0])
                except ValueError:
                    offset = 0
                try:
                    count = int(c2[1]) - offset
                except ValueError:
                    count = 10
            else:
                offset = 0
                try:
                    count = int(c2[0])
                except ValueError:
                    count = 10
        else:
            offset = 0
            count = 10
        if old:
            lib = MBook.list_old_record(sender, count)
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
            listcmd = content.split()
            if len(listcmd) > 2:
                if '-' == listcmd[2]:
                    old = True
            if len(listcmd) > 1:
                c1 = listcmd[1]
                c2 = c1.split('-')
                if len(c2) > 1:
                    try:
                        offset = int(c2[0])
                    except ValueError:
                        offset = 0
                    try:
                        count = int(c2[1]) - offset
                    except ValueError:
                        count = 10
                else:
                    try:
                        count = int(c2[0])
                    except ValueError:
                        count = 10
            try:
                rate = int(listcmd[0])
            except ValueError:
                rate = 0
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
            reply = ':help, this help menu, :help command for detail\n'
            reply += ':lan2lan, eg: en2zh, zh2ja, en2ja\n'
            reply += ':dict, only find translation on dict.cn\n'
            reply += ':google, only find translation on google\n'
            reply += ':add, add new word to your library\n'
            reply += ':del, delete word from your library\n'
            reply += ':list, list words in your library\n'
            reply += ':rating, list  words in your library\n'
            reply += ':history, your search history\n'
            reply += ':clear, clear your oldest 100 history\n'
            reply += 'more information on http://mardict.appspot.com\n'
        elif 'lan2lan' == content:
            reply = 'help on lan2lan:\n[usage] :lan2lan word\n'
            reply += '[intro] translate from one language to another language by google translation api.\n'
            reply += '[eg] :en2zh hello\n'
        elif 'dict' == content:
            reply = 'help on dict:\n[usage] :dict word\n'
            reply += '[intro] translate your word only use dict.cn api'
            reply += '[eg] :dict hello\n'
        elif 'google' == content:
            reply = 'help on google:\n[usage] :google word\n'
            reply += '[intro] translate your word only use google api'
            reply += '[eg] :google hello\n'
        elif 'add' == content:
            reply = 'help on add:\n[usage] :add (word)\n'
            reply += '[intro] add the word to your library(storing your unfamiliar word)\n'
            reply += '[eg] :add (without any word append, will add your last checking word)\n'
            reply += '     :add hello\n'
        elif 'del' == content:
            reply = 'help on del:\n[usage] :del word\n'
            reply += '[intro] delete the word from your library.\n'
            reply += '[eg] :del hello\n'
        elif 'list' == content:
            reply = 'help on list:\n[usage] :list (number)\n'
            reply += '[intro] list a certain number of words from your library.\n'
            reply += '[eg] :list (without any number append, the count will be 10)\n'
            reply += '     :list 20 (list the newest 20 words from your library)\n'
            reply += '     :list -20 (list the oldest 20 words from your library)\n'
        elif 'rating' == content:
            reply = 'help on rating:\n[usage] :rating (number) (number)\n'
            reply += '[intro] list a certain number of a certain rate of words from your library.\n'
            reply += '[eg] :rating (without any number append, the rate will be 0, the count will be 10)\n'
            reply += '     :list 1 (list the newest 10 words where rate is 1 from your library)\n'
            reply += '     :list 1 -10 (list the oldest 10 words where rate is 1 from your library)\n'
        elif 'history' == content:
            reply = 'help on history:\n[usage] :history (number)\n'
            reply += '[intro] list your checking history\n'
            reply += '[eg] :history (without any number append, the count will be 10)\n'
            reply += '     :list 20 (list your newest 20 checking history)\n'
        elif 'clear' == content:
            reply = 'help on clear:\n[usage] :clear\n'
            reply += '[intro] clear your oldest 100 checking history\n'
            reply += '[eg] :clear\n'
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
