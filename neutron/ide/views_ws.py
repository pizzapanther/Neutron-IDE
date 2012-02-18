import sys
import os
import re
import json
import time
import subprocess
import traceback
import logging
import base64
import datetime
import threading

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
import ide.settings

SCREEN_COMMAND = False
if os.path.exists(ide.settings.TERMINAL_SCREEN):
  SCREEN_COMMAND = ide.settings.TERMINAL_SCREEN
  
class TerminalWebSocket (WebSocketHandler):
  def open (self):
    logging.info('Opening Terminal Web Socket')
    self.last_sent = None
    self.terminals = {}
    self.current_tsid = None
    self.cols = None
    self.lines = None
    
    self.io_loop = ioloop.IOLoop.instance()
    #self.io_loop.set_blocking_signal_threshold(3)
    self.scheduler = ioloop.PeriodicCallback(self.refresh_loop, 100, io_loop=self.io_loop)
    self.scheduler.start()
    self.lock = threading.Lock()
    
    if SCREEN_COMMAND:
      old = []
      old = os.listdir(settings.TERM_DIR)
      
      if old:
        self.write_message(json.dumps({'action': 'oldterms', 'data': old}))
        
  def refresh_loop (self):
    try:
      if self.current_tsid is not None:
        self.term_refresh()
        
    except:
      import traceback
      traceback.print_exc()
      
  def create_terminal (self, tsid, user, width, height, restart=False):
    self.terminals[tsid] = ide.terminal.Terminal()
    
    cmd = ide.settings.TERMINAL_SHELL
    if SCREEN_COMMAND:
      cmd = SCREEN_COMMAND + ' -A ' + os.path.join(settings.TERM_DIR, str(tsid)) + ' -E -z -r none ' + ide.settings.TERMINAL_SHELL
      
    self.terminals[tsid].start(cmd, user.preferences.basedir, width, height, tsid=tsid, onclose=self.remove_terminal)
    
  def process_line (self, num, line):
    html = ''
    last_class = None
    count = 0
    
    #pline = ''
    #for ch in line:
    #  pline += ch[0]
    #  
    #print num, pline
    
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
      
    return html
    
  def term_refresh (self, tsid=None, full=False):
    self.lock.acquire()
    
    if tsid is None:
      if self.current_tsid is not None:
        tsid = self.current_tsid
        
      else:
        return None
        
    if full:
      data = self.terminals[tsid]._proc.history()
      
    else:
      data = self.terminals[tsid]._proc.read()
      
    if full or self.terminals[tsid]._proc.updated != self.last_sent:
      send_data = {'cursor': data['cursor'], 'cx': data['cx'], 'cy': data['cy'] , 'lines': {}}
      
      if full:
        self.last_sent = self.terminals[tsid]._proc.updated = None
        for num in range(0, len(data['lines'])):
          send_data['lines'][num] = self.process_line(num, data['lines'][num])
          
      else:
        for num, line in data['lines'].items():
          send_data['lines'][num] = self.process_line(num, line)
          
      #print '------------------------------------------------------------------'
      dump = json.dumps({'action': 'update', 'data': send_data})
      self.write_message(dump)
      self.last_sent = self.terminals[tsid]._proc.updated
      
    self.lock.release()
    
  def write_message (self, message):
    dump = message.encode('zlib')[2:-4]
    dump = unicode(base64.b64encode(dump))
    super(TerminalWebSocket, self).write_message(dump)
    
  def on_message (self, message):
    data = json.loads(message)
    
    if hasattr(data, 'has_key') and data.has_key('action'):
      tsid = data['tsid']
      self.current_tsid = tsid
      
      if data['action'] == 'start':
        session = ENGINE.SessionStore(data['session'])
        if session.has_key('_auth_user_id') and session['_auth_user_id']:
          try:
            user = User.objects.get(id=session['_auth_user_id'])
            
          except:
            user = None
            
          if user and user.is_active:
            restart = False
            if data.has_key('restart') and data['restart']:
              restart = True
              
            self.create_terminal(tsid, user, data['cols'], data['lines'], restart)
            self.cols = data['cols']
            self.lines = data['lines']
            self.term_refresh(tsid, True)
            
            if restart:
              self.write_message(unicode(json.dumps({'action': 'doreset', 'data': True})))
              
            return None
            
        self.write_message(unicode(json.dumps({'action': 'message', 'data': 'Invalid User Credentials'})))
        self.close()
        
      elif data['action'] == 'reset':
        self.terminals[tsid].write(u'\x0c') # ctrl-l
        self.term_refresh(tsid, True)
        
      elif data['action'] == 'prev':
        self.terminals[tsid]._proc.term.prev_page()
        self.term_refresh(tsid, True)
        
      elif data['action'] == 'next':
        self.terminals[tsid]._proc.term.next_page()
        self.term_refresh(tsid, True)
        
      elif data['action'] == 'write':
        self.terminals[tsid].write(data['write'])
        self.term_refresh(tsid)
        
      elif data['action'] == 'resize':
        self.terminals[tsid].resize(data['lines'], data['cols'])
        self.cols = data['cols']
        self.lines = data['lines']
        self.term_refresh(tsid, True)
        
      elif data['action'] == 'full':
        if data.has_key('lines') and data.has_key('cols'):
          self.cols = data['cols']
          self.lines = data['lines']
          if self.cols != self.terminals[tsid].cols or self.lines != self.terminals[tsid].lines:
            self.terminals[tsid].resize(data['lines'], data['cols'])
            
        self.term_refresh(tsid, True)
        
      elif data['action'] == 'solong':
        self.so_long(tsid)
        
  def remove_terminal (self, tsid):
    self.terminals[tsid].kill()
    
  def so_long (self, tsid):
    del self.terminals[tsid]
    self.current_tsid = None
    self.write_message(unicode(json.dumps({'action': 'killed', 'data': tsid})))
    
  def on_close(self):
    logging.info('Closing Terminal Web Socket')
    self.scheduler.stop()
    if len(self.terminals.keys()) > 0:
      for t, term in self.terminals.items():
        term.kill()
        
      
