#!/usr/bin/env python

import sys
import os
import argparse
import subprocess
import logging
import socket
import time
import functools

import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import tornado.web
import tornado.options
import tornado.autoreload

MYPATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, MYPATH)
sys.path.insert(0, os.path.abspath(os.path.join(MYPATH, '..')))
sys.path.insert(0, os.path.normpath(os.path.join(MYPATH, "depends")))

def systemcmd (cmd):
  p = subprocess.Popen(cmd, shell=True)
  sts = os.waitpid(p.pid, 0)[1]
  
def generate_cert (key, csr, crt):
  raw_input('Welcome to Neutron IDE!\nWe are going to create an SSL certificate for you so everything is super secure.\nPress ENTER to continue.\n')
  
  systemcmd('openssl req -nodes -newkey rsa:2048 -keyout "%s" -out "%s"' % (key, csr))
  systemcmd('openssl x509 -req -days 999 -in "%s" -signkey "%s" -out "%s"' % (csr, key, crt))
  
#def cleanup_tornado_sockets (io_loop):
#  for fd in io_loop._handlers.keys()[:]:
#    print fd
#    try:
#      os.close(fd)
#      
#    except Exception:
#      import traceback
#      traceback.print_exc()
#      
if __name__ == "__main__":
  os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'
  
  from django.conf import settings
  
  import ide.settings
  from ide.views_ws import TerminalWebSocket
  
  parser = argparse.ArgumentParser(description='Neutron IDE built in Web Server')
  parser.add_argument('-l', '--logging', action='store_true', dest='logging', help='turn on request logging.')
  parser.add_argument('-n', '--nossl', action='store_true', dest='nossl', help='turn off ssl.')
  
  args = parser.parse_args()
  
  if args.logging:
    logging.getLogger().setLevel(logging.INFO)
    tornado.options.enable_pretty_logging()
    
  wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
  
  if ide.settings.TERMINAL_ON:
    application = tornado.web.Application([
      (r"/websocket", TerminalWebSocket),
      (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': settings.STATIC_ROOT}),
      (r".*", tornado.web.FallbackHandler, {'fallback': wsgi_app}),
    ], debug=settings.DEBUG)
    
  else:
    application = tornado.web.Application([
      (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': settings.STATIC_ROOT}),
      (r".*", tornado.web.FallbackHandler, {'fallback': wsgi_app}),
    ], debug=settings.DEBUG)
    
  if args.nossl:
    ssl_options = None
    
  else:
    if not os.path.exists(settings.SERVER_CERT) or not os.path.exists(settings.SERVER_KEY):
      generate_cert(settings.SERVER_KEY, settings.SERVER_CSR, settings.SERVER_CERT)
      print "Certificate Generation Complete"
      
    ssl_options = {
      'certfile': settings.SERVER_CERT,
      'keyfile': settings.SERVER_KEY,
    }
    
  http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_options)
  http_server.listen(settings.HTTP_PORT)
  if ssl_options:
    http_server2 = tornado.httpserver.HTTPServer(application)
    http_server2.listen(settings.IMG_EDITOR_PORT)
    
  print "Web Server Started"
  
  io = tornado.ioloop.IOLoop.instance()
  #tornado.autoreload.add_reload_hook(functools.partial(cleanup_tornado_sockets, io))
  io.start()
  
  