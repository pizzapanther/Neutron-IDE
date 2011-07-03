import os
import time
import errno
import signal
import subprocess
import mimetypes
mimetypes.init()

from django.core.management.base import BaseCommand, CommandError
from django.core.handlers.wsgi import WSGIHandler
from django.conf import settings
from django.utils.daemonize import become_daemon

from cherrypy.wsgiserver import CherryPyWSGIServer as Server
from cherrypy.wsgiserver import WSGIPathInfoDispatcher
from cherrypy.lib.static import serve_file
import cherrypy

HELP = r"""
  Run IDE in a CherryPy webserver.

  runide [options] [stop]

Optional CherryPy server settings: (setting=value)
  host=HOSTNAME         hostname to listen on
                        Defaults to localhost
  port=PORTNUM          port to listen on
                        Defaults to 8000
  server_name=STRING    CherryPy's SERVER_NAME environ entry
                        Defaults to localhost
  daemonize=BOOL        whether to detach from terminal
                        Defaults to False
  pidfile=FILE          write the spawned process-id to this file
  workdir=DIRECTORY     change to this directory when daemonizing
  threads=NUMBER        Number of threads for server to use
  ssl_certificate=FILE  SSL certificate file
  ssl_private_key=FILE  SSL private key file
  server_user=STRING    user to run daemonized process
                        Defaults to www-data
  server_group=STRING   group to daemonized process
                        Defaults to www-data

Examples:
  Run a "standard" CherryPy server server
    $ manage.py runide

  Run a CherryPy server on port 80
    $ manage.py runide

  Run a CherryPy server as a daemon and write the spawned PID in a file
    $ manage.py runide daemonize=true pidfile=/var/run/django-cpserver.pid

"""

DEFAULT_OPTIONS = {
  'host': 'localhost',
  'port': 8000,
  'server_name': 'localhost',
  'threads': 10, 
  'daemonize': 0,
  'workdir': None,
  'pidfile': settings.SERVER_PIDFILE,
  'server_user': None,
  'server_group': None,
  'ssl_certificate': settings.SERVER_CERT,
  'ssl_private_key': settings.SERVER_KEY,
  'shutdown_timeout': 60,
  'request_queue_size': 5,
}

class Command (BaseCommand):
  def handle(self, *args, **options):
    opts = DEFAULT_OPTIONS.copy()
    
    for x in args:
      if "=" in x:
        k, v = x.split('=', 1)
        
      else:
        k, v = x, True
        
      opts[k.lower()] = v
  
    if "help" in opts:
      print HELP
      return
      
    if "stop" in opts:
      stop_server(opts['pidfile'])
      return True
      
    start_server(opts)
    
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
    
def poll_process(pid):
  for n in range(10):
    time.sleep(0.25)
    try:
      os.kill(pid, 0)
      
    except OSError, e:
      if e[0] == errno.ESRCH:
        return False
        
      else:
        raise Exception
        
  return True
  
def change_uid_gid(uid, gid=None):
  if not os.geteuid() == 0:
    return
    
  (uid, gid) = get_uid_gid(uid, gid)
  os.setgid(gid)
  os.setuid(uid)

def get_uid_gid(uid, gid=None):
  import pwd, grp
  uid, default_grp = pwd.getpwnam(uid)[2:4]
  if gid is None:
    gid = default_grp
    
  else:
    try:
      gid = grp.getgrnam(gid)[2]
      
    except KeyError:
      gid = default_grp
      
  return (uid, gid)
  
def stop_server (pidfile):
  if os.path.exists(pidfile):
    pid = int(open(pidfile).read())
    try:
      os.kill(pid, signal.SIGTERM)
      
    except OSError:
      os.remove(pidfile)
      return
      
    if poll_process(pid):
      os.kill(pid, signal.SIGKILL)
      if poll_process(pid):
        raise OSError, "Process %s did not stop."
        
    os.remove(pidfile)
    
def start_server (options):
  if options['daemonize']:
    if options['server_user'] and options['server_group']:
      change_uid_gid(options['server_user'], options['server_group'])
      
    if options['workdir']:
      become_daemon(our_home_dir=options['workdir'])
      
    else:
      become_daemon()
      
    fp = open(options['pidfile'], 'w')
    fp.write("%d\n" % os.getpid())
    fp.close()
    
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
    
  if options['ssl_certificate'].lower() == 'none' or options['ssl_private_key'].lower() == 'none':
    pass
    
  else:
    if not os.path.exists(options['ssl_certificate']) or not os.path.exists(options['ssl_private_key']):
      if options['ssl_certificate'] == settings.SERVER_CERT and options['ssl_private_key'] == settings.SERVER_KEY:
        generate_cert()
        
      else:
        raise Exception('Invalid Certificate or Key Path')
        
    SERVER.ssl_certificate = options['ssl_certificate']
    SERVER.ssl_private_key = options['ssl_private_key'] 
    
  try:
    SERVER.start()
    
  except KeyboardInterrupt:
    SERVER.stop()
    
def systemcmd (cmd):
  p = subprocess.Popen(cmd, shell=True)
  sts = os.waitpid(p.pid, 0)[1]
  
def generate_cert ():
  raw_input('Welcome to Neutron IDE!\nWe are going to create an SSL certificate for you so everything is super secure.\nPress ENTER to continue.\n')
  
  systemcmd('openssl req -nodes -newkey rsa:2048 -keyout "%s" -out "%s"' % (settings.SERVER_KEY, settings.SERVER_CSR))
  systemcmd('openssl x509 -req -days 999 -in "%s" -signkey "%s" -out "%s"' % (settings.SERVER_CSR, settings.SERVER_KEY, settings.SERVER_CERT))
  
