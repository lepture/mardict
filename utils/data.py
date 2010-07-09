#!/usr/bin/env python
# -*- coding: utf-8 -*-

help_txt = """
:help, show this help menu. :help [command] for detail
:dict [word], only find translation on dict.cn
:google [sentence], only find translation on google api
:lan2lan [sentence], translate from one language to another language
:add [word], add new word to your library
:del [word], delete word from your library
:list [number], list words in your library
:rating [number], lsit words in your library with a certain rate
:history [number], show your search history
:clear, clear your oldest 100 history

for more information, browser http://mardict.appspot.com
"""

help_dict = """
help on dict:
[usage] :dict word
[intro] translate your word only use dict.cn api
[eg] :dict hello

more on http://mardict.appspot.com/help/#2
"""

help_google = """
help on google:
[usage] :google word
[intro] translate your word only use google api
[eg] :google google is a bitch

more on http://mardict.appspot.com/help/#3
"""

help_lan2lan = """
help on lan2lan:
[usage] :lan2lan word
[intro] translate from one language to another language by google translation api
[eg] :en2zh hello

more on http://mardict.appspot.com/help/#4
"""

help_history = """
help on history:
[usage] :history (number)
[intro] list your search history
[eg] :history 9

more on http://mardict.appspot.com/help/#5
"""

help_clear = """
help on clear:
[usage] :clear
[intro] clear your search history

more on http://mardict.appspot.com/help/#6
"""

help_add = """
help on add:
[usage] :add (word)
[intro] add the new word to your library(storing your unfamiliar word)
[eg] :add hello

more on http://mardict.appspot.com/help/#7
"""

help_del = """
help on del:
[usage] :del word
[intro] delete the word from your library
[eg] :del hello

more on http://mardict.appspot.com/help/#8
"""

help_list = """
help on list:
[usage] :list (number)
[intro] list a certain number of words from your library.
[eg] :list 9

this function is very complex, browser the website.

more on http://mardict.appspot.com/help/#9
"""

help_rating = """
help on rating:
[usage] :rating (number)
[intro] list a certain number of words from your library with a certain rate.
[eg] :rating 0 9

this function is very complex, browser the website.

more on http://mardict.appspot.com/help/#10
"""
