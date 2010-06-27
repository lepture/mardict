#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import urllib2
from django.utils.simplejson import loads as parse_json
#from simplejson import loads as parse_json

class DictCN(object):
    def __init__(self, word='hello'):
        try:
            word = word.encode('utf-8')
        except:
            pass
        self.__url = 'http://dict.cn/ws.php?utf8=true&q=%s' % urllib2.quote(word)

    def __get_source(self):
        url = self.__url
        try:
            page = urllib2.urlopen(url)
            source = unicode(page.read(), 'utf-8')
            page.close()
        except:
            return None
        return source

    def __parse_source(self):
        source = self.__get_source()
        if source:
            regex = r'<key>(.*?)</key>.*?<pron>(.*?)</pron>.*?<def>(.*?)</def>'
            match = re.findall(regex, source, re.U|re.S)
            if match:
                return match[0]
        return None

    def __get_info(self):
        info = self.__parse_source()
        if not info:
            return None

        key = info[0]
        pron = info[1]
        define = info[2].replace('\n',', ')
        define = define.replace('&lt;','<').replace('&gt;','>')
        # fix pron
        regex = r'&#(\d{3});'
        match = re.findall(regex, pron, re.U)
        if match:
            for num in match:
                fix = '&#%s;' % num
                pron = pron.replace(fix,unichr(int(num)))
        data = {'from': 'dictcn','key': key, 'pron': pron, 'define': define}
        return data

    def get_response(self):
        data = self.__get_info()
        return data

class GoogleDict(object):
    base = 'http://ajax.googleapis.com/ajax/services/language/'

    def __init__(self, word='hello',lan1='en',lan2='zh-CN'):
        self.__from = lan1
        self.__to = lan2
        try:
            self.__word = word.encode('utf-8')
        except:
            self.__word = word

    def __get_source(self, url):
        try:
            page = urllib2.urlopen(url)
            source = map(parse_json, page)
            page.close()
        except:
            return None
        return source[0]['responseData']

    def detect_language(self):
        url = self.base + ('detect?v=1.0&q=%s' % urllib2.quote(self.__word))
        source = self.__get_source(url)
        if source:
            language = source['language']
        else:
            language = 'en'
        return language

    def trans_language(self):
        lan1 = self.__from
        lan2 = self.__to
        word = urllib2.quote(self.__word)
        url = self.base + ('translate?v=1.0&langpair=%s|%s&q=%s' % \
                           (lan1,lan2,word))
        source = self.__get_source(url)
        if source:
            try:
                key = unicode(self.__word, 'utf-8')
            except:
                key = self.__word
            define = source['translatedText']
            pron = 'none'
            data = {'from':'google','key':key, 'pron':pron,'define': define }
        else:
            data = None
        return data

    def get_response(self):
        data = self.trans_language()
        return data

if '__main__' == __name__:
    word = raw_input('Enter a word: ')
    d = DictCN(word)
    data = d.get_response()
    reply = '%s [%s]\nfrom: dict.cn\n%s' % \
            (data['key'], data['pron'], data['define'])
    print reply
    g = GoogleDict(word)
    data = g.get_response()
    reply = '%s\nfrom: google\n%s' % \
            (data['key'], data['define'])
    print reply
