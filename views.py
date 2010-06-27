#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from config import DIR

class Index(webapp.RequestHandler):
    def get(self):
        values = {
            'hello': 'hello',
        }
        tp = os.path.join(DIR, 'index.html')
        self.response.out.write(template.render(tp,values))
