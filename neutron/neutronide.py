#!/usr/bin/env python

import sys
import os
import argparse
import subprocess
import logging
import logging.handlers
import socket
import time
import functools
import signal
import traceback
from cStringIO import StringIO
import cPickle as pickle

import django.core.handlers.wsgi

import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import tornado.web
import tornado.options
import tornado.autoreload

import daemon

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
  
def exc_hook (t, v, trace):
  logging.exception('Error Information')
  logging.exception('Type: ' + str(t))
  logging.exception('Value: ' + str(v))
  
  fh = StringIO()
  traceback.print_exception(t, v, trace, file=fh)
  logging.exception(fh.getvalue())
  fh.close()
  
def start_loop (args):
  os.umask(022)
  os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'
  
  from django.conf import settings
  
  import ide.settings
  from ide.views_ws import TerminalWebSocket
  
  ld = os.path.dirname(settings.PKLPATH)
  if not os.path.exists(ld):
    os.makedirs(ld)
    
  p = {'pid': os.getpid(), 'args': args}
  output = open(settings.PKLPATH, 'wb')
  pickle.dump(p, output)
  output.close()
  
  ld = os.path.dirname(settings.LOGPATH)
  if not os.path.exists(ld):
    os.makedirs(ld)
    
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  
  if args.logging:
    tornado.options.enable_pretty_logging()
    
  else:
    fileLogger = logging.handlers.RotatingFileHandler(filename=settings.LOGPATH, maxBytes=1024*1024, backupCount=9)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fileLogger.setFormatter(formatter)
    logger.addHandler(fileLogger)
    logger.propagate = 0
    sys.excepthook = exc_hook
    
  wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
  
  if ide.settings.TERMINAL_ON:
    application = tornado.web.Application([
      (r"/websocket", TerminalWebSocket),
      (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': settings.STATIC_ROOT}),
      (r"/uploads/(.*)", tornado.web.StaticFileHandler, {'path': settings.MEDIA_ROOT}),
      (r".*", tornado.web.FallbackHandler, {'fallback': wsgi_app}),
    ], debug=settings.DEBUG, gzip=True)
    
  else:
    application = tornado.web.Application([
      (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': settings.STATIC_ROOT}),
      (r"/uploads/(.*)", tornado.web.StaticFileHandler, {'path': settings.MEDIA_ROOT}),
      (r".*", tornado.web.FallbackHandler, {'fallback': wsgi_app}),
    ], debug=settings.DEBUG, gzip=True)
    
  if args.nossl:
    ssl_options = None
    
  else:
    ssl_options = {
      'certfile': settings.SERVER_CERT,
      'keyfile': settings.SERVER_KEY,
    }
    
  http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_options)
  http_server.listen(settings.HTTP_PORT)
  if ssl_options:
    http_server2 = tornado.httpserver.HTTPServer(application)
    http_server2.listen(settings.IMG_EDITOR_PORT)
    
  io = tornado.ioloop.IOLoop.instance()
  #tornado.autoreload.add_reload_hook(functools.partial(cleanup_tornado_sockets, io))
  io.start()
  
def stop_loop ():
  os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'
  
  from django.conf import settings
  
  pkl = open(settings.PKLPATH, 'rb')
  p = pickle.load(pkl)
  pkl.close()
  
  os.kill(p['pid'], signal.SIGKILL)
  return p['args']
  
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
  parser = argparse.ArgumentParser(description='Neutron IDE built in Web Server')
  parser.add_argument('-l', '--logging', action='store_true', dest='logging', help='Log to screen instead of file logging.')
  parser.add_argument('-f', '--foreground', action='store_true', dest='foreground', help='Run in foreground instead of as a daemon.')
  parser.add_argument('-n', '--nossl', action='store_true', dest='nossl', help='turn off ssl.')
  parser.add_argument('action', nargs=1, help='start|stop|restart')
  
  args = parser.parse_args()
  
  if 'stop' in args.action or 'restart' in args.action:
    print "Stopping Web Server ...",
    oldargs = stop_loop()
    if 'restart' in args.action:
      args = oldargs
      
    print "Done"
    
  if 'start' in args.action or 'restart' in args.action:
    os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'
    from django.conf import settings
    
    if args.nossl:
      pass
    
    else:
      if not os.path.exists(settings.SERVER_CERT) or not os.path.exists(settings.SERVER_KEY):
        generate_cert(settings.SERVER_KEY, settings.SERVER_CSR, settings.SERVER_CERT)
        print "Certificate Generation Complete"
        
    if args.foreground:
      start_loop(args)
      
    else:
      print "Starting Web Server ...",
      with daemon.DaemonContext():
        start_loop(args)
        