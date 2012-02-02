import sys
import os
import json
import traceback
import logging
import base64
import datetime

MYPATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(MYPATH, '..')))
sys.path.insert(0, os.path.abspath(os.path.join(MYPATH, '..', '..')))
sys.path.insert(0, os.path.normpath(os.path.join(MYPATH, "depends")))

os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'

from django.utils.html import escape
from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.auth.models import User
ENGINE = import_module(settings.SESSION_ENGINE)

from tornado.websocket import WebSocketHandler
from tornado import ioloop

import ide.terminal

class TerminalWebSocket (WebSocketHandler):
  def open (self):
    logging.info('Opening Terminal Web Socket')
    self.last_sent = None
    self.terminal = None
    
  def create_terminal (self, user, width, height):
    self.terminal = ide.terminal.Terminal()
    self.terminal.start('/bin/bash', user.preferences.basedir, width, height, self.close)
    
  def term_refresh (self, full=False):
    #print self.terminal._proc.popen.poll()
    #if full:
    #  data = self.terminal._proc.history()
    #  
    data = self.terminal._proc.read()
      
    if data != self.last_sent:
      send_data = {'cursor': data['cursor'], 'cx': data['cx'], 'cy': data['cy'] , 'lines': {}}
      for num, line in data['lines'].items():
        html = ''
        last_class = None
        count = 0
        for ch in line:
          classes = ''
          
          if ch[1]  != 'default':
            classes += 'fg' + ch[1] + ' '
            
          if ch[2]  != 'default':
            classes += 'bg' + ch[2] + ' '
            
          if ch[3]:
            classes += 'b '
            
          if ch[4]:
            classes += 'i '
            
          if ch[5]:
            classes += 'u '
            
          if ch[6]:
            classes += 's '
            
          if ch[7]:
            classes += 'r '
            
          if classes != '':
            classes = classes[:-1]
            
          if classes != last_class:
            if count != 0 and last_class != '':
              html += '</span>';
              
            if classes != '':
              html += '<span class="' + classes + '">'
              
          html += escape(ch[0])
          
          last_class = classes;
          count += 1
          
        if last_class != '':
          html += '</span>';
          
        #print html
        send_data['lines'][num] = html
        
      dump = json.dumps({'action': 'update', 'data': send_data})
      dump = dump.encode('zlib')[2:-4]
      dump = unicode(base64.b64encode(dump))
      self.write_message(dump)
      self.last_sent = data
      
  def on_message (self, message):
    data = json.loads(message)
    
    if hasattr(data, 'has_key') and data.has_key('action'):
      if data['action'] == 'start':
        session = ENGINE.SessionStore(data['session'])
        if session.has_key('_auth_user_id') and session['_auth_user_id']:
          try:
            user = User.objects.get(id=session['_auth_user_id'])
            
          except:
            user = None
            
          if user and user.is_active:
            self.create_terminal(user, data['cols'], data['lines'])
            
            self.term_refresh(True)
            self.io_loop = ioloop.IOLoop.instance()
            #self.io_loop.set_blocking_signal_threshold(3)
            self.scheduler = ioloop.PeriodicCallback(self.term_refresh, 100, io_loop=self.io_loop)
            self.scheduler.start()
            return None
            
        self.write_message(unicode(json.dumps({'action': 'message', 'data': 'Invalid User Credentials'})))
        self.close()
          
      elif data['action'] == 'write':
        self.terminal.write(data['write'])
        self.term_refresh()
        
  def on_close(self):
    logging.info('Closing Terminal Web Socket')
    if self.terminal:
      self.scheduler.stop()
      self.terminal._proc.kill()
      