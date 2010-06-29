#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db

class DictLog(db.Model):
    im = db.IMProperty(required=True)
    word = db.StringProperty(required=True)
    define = db.StringProperty()
    pron = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def add_record(cls, user_im, user_word, user_define, user_pron):
        m = DictLog(
            im = user_im,
            word = user_word,
            define = user_define,
            pron= user_pron
        )
        m.put()

    @classmethod
    def get_record(cls, user_im):
        q = db.GqlQuery("SELECT * FROM DictLog WHERE im = :1 ORDER BY date DESC", user_im)
        return q.fetch(1)
    @classmethod
    def list_record(cls, user_im, count=10):
        q = db.GqlQuery("SELECT * FROM DictLog WHERE im = :1 ORDER BY date DESC", user_im)
        if int(count) > 50 or int(count) < 0:
            count = 10
        return q.fetch(int(count))

    @classmethod
    def destroy(cls, user_im):
        ''' clear one's history '''
        q = db.GqlQuery("SELECT * FROM DictLog WHERE im = :1", user_im)
        results = q.fetch(100)
        db.delete(results)


class MBook(db.Model):
    ''' for user storing their unfamiliar words '''
    im = db.IMProperty(required=True)
    rating = db.IntegerProperty(default=0)
    word = db.StringProperty(required=True)
    define = db.StringProperty()
    pron = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_record(cls, user_im, user_word):
        q = db.GqlQuery("SELECT * FROM MBook WHERE im = :1 AND word = :2",user_im, user_word)
        return q.fetch(1)
    
    @classmethod
    def add_record(cls, user_im, user_word, user_define, user_pron=None):
        if user_pron:
            m = MBook(im = user_im,
                      word = user_word,
                      define = user_define,
                      pron= user_pron)
            m.put()
        else:
            m = MBook(im = user_im,
                      word = user_word,
                      define = user_define)
            m.put()
    
    @classmethod
    def list_record(cls, user_im, count):
        q = db.GqlQuery("SELECT * FROM MBook WHERE im = :1 ORDER BY date DESC", user_im)
        if int(count) > 50 or int(count) < 0:
            count = 10
        return q.fetch(int(count))

    @classmethod
    def list_old_record(cls, user_im, count):
        q = db.GqlQuery("SELECT * FROM MBook WHERE im = :1", user_im)
        if int(count) > 50 or int(count) < 0:
            count = 10
        return q.fetch(int(count))

    @classmethod
    def rating_record(cls, user_im, user_rating, count):
        q = db.GqlQuery("SELECT * FROM MBook WHERE im = :1 AND rating = :2 ORDER BY date DESC", user_im, user_rating)
        if int(count) > 50 or int(count) < 0:
            count = 10
        return q.fetch(int(count))

    @classmethod
    def rating_old_record(cls, user_im, user_rating, count):
        q = db.GqlQuery("SELECT * FROM MBook WHERE im = :1 AND rating = :2", user_im, user_rating)
        if int(count) > 50 or int(count) < 0:
            count = 10
        return q.fetch(int(count))
