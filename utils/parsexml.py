#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
import data from a mardict xml file
"""

__version__ = '1.0'
__author__ = 'Marvour Young < marvour@gmail.com >'
__license__ = 'BSD'

from xml.dom import minidom
import datetime

def todate(s):
    date = datetime.datetime.strptime(s,'%Y-%m-%d %H:%M:%S.%f')
    return date


class MarXML:
    def __init__(self, content):
        self.content = content

    def get_data(self, node):
        child = node.firstChild
        if child:
            if child.nodeType == node.TEXT_NODE or \
               child.nodeType == node.CDATA_SECTION_NODE:
                return child.data
        return None

    def get_item(self, nodelist):
        text = self.get_data
        mardata = []
        for node in nodelist:
            word = text(node.getElementsByTagName('word')[0])
            pron = text(node.getElementsByTagName('pron')[0])
            define = text(node.getElementsByTagName('define')[0])
            rate = int(text(node.getElementsByTagName('rate')[0]))
            date = todate(text(node.getElementsByTagName('date')[0]))
            mardata.append(dict(
                word = word,
                pron = pron,
                define = define,
                rate = rate,
                date = date,
            ))
        return mardata

    def parse_data(self):
        content = self.content
        try:
            dom = minidom.parseString(content)
        except:
            return False
        itemlist = dom.getElementsByTagName('item')
        data = self.get_item(itemlist)
        return data


if "__main__" == __name__:
    f = open('mardict.xml')
    p = f.read()
    m = MarXML(p)
    print m.parse_data()
