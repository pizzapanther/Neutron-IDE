import os
import mimetypes
mimetypes.init()

from django.core.management.base import BaseCommand, CommandError
from django.core.handlers.wsgi import WSGIHandler
from django.conf import settings

from cherrypy.wsgiserver import CherryPyWSGIServer as Server
from cherrypy.wsgiserver import WSGIPathInfoDispatcher
from cherrypy.lib.static import serve_file
import cherrypy

DEFAULT_OPTIONS = {
  'host': 'localhost',
  'port': 8000,
  'server_name': 'localhost',
  'threads': 10, 
  'daemonize': 0,
  'workdir': None,
  'pidfile': None,
  #'server_user': 'www-data',
  #'server_group': 'www-data',
  'ssl_certificate': settings.SERVER_CERT,
  'ssl_private_key': settings.SERVER_KEY,
  'shutdown_timeout': 60,
  'request_queue_size': 5,
}

class Command (BaseCommand):
  def handle(self, *args, **options):
    start_server()
    
def static (environ, start_response):
  path = os.path.join(settings.STATIC_ROOT, environ['PATH_INFO'][1:])
  t, e = mimetypes.guess_type(path)
  
  if not t:
    t = 'application/octet-stream'
    
  if os.path.exists(path):
    start_response('200 OK', [('Content-type', t)])
    return serve_file(path)
    
  else:
    start_response('404 Not Found', [('Content-type', 'text/plain')])
    return ['404 Not Found']
    
def start_server (options=DEFAULT_OPTIONS):
  d = WSGIPathInfoDispatcher({'/static': static, '/': WSGIHandler()})
  SERVER = Server(
      (options['host'], int(options['port'])),
      d, 
      numthreads=int(options['threads']),
      max=int(options['threads']), 
      server_name=options['server_name'],
      shutdown_timeout = int(options['shutdown_timeout']),
      request_queue_size = int(options['request_queue_size'])
    )
    
    server.ssl_certificate = options['ssl_certificate']
    server.ssl_private_key = options['ssl_private_key'] 
  
  try:
    SERVER.start()
    
  except KeyboardInterrupt:
    SERVER.stop()
    
