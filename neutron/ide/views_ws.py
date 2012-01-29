from tornado.websocket import WebSocketHandler
from tornado import ioloop

import ide.terminal

import json
import traceback
import logging

class TerminalWebSocket (WebSocketHandler):
  def open (self):
    logging.info('Opening Terminal Web Socket')
    self.last_sent = None
    
  def create_terminal (self, width, height):
    self.terminal = ide.terminal.Terminal()
    self.terminal.start('/bin/bash', width, height)
    
  def term_refresh (self, full=False):
    if full:
      data = self.terminal._proc.history()
      
    else:
      data = self.terminal._proc.read()
      
    if data != self.last_sent:
      dump = unicode(json.dumps({'action': 'update', 'data': data}))
      self.write_message(dump)
      self.last_sent = data
      
  def on_message (self, message):
    data = json.loads(message)
    
    if hasattr(data, 'has_key') and data.has_key('action'):
      if data['action'] == 'start':
        self.create_terminal(data['cols'], data['lines'])
        
        self.term_refresh(True)
        self.io_loop = ioloop.IOLoop.instance()
        #self.io_loop.set_blocking_signal_threshold(3)
        self.scheduler = ioloop.PeriodicCallback(self.term_refresh, 100, io_loop=self.io_loop)
        self.scheduler.start()
        
      elif data['action'] == 'write':
        self.terminal.write(data['write'])
        self.term_refresh()
        
  def on_close(self):
    logging.info('Closing Terminal Web Socket')
    self.scheduler.stop()
    self.terminal._proc.kill()
    