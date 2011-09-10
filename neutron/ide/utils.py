import os
import string
import mimetypes
mimetypes.init()

from django import http
from django.conf import settings
import django.utils.simplejson as json

text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
_null_trans = string.maketrans("", "")

DEFAULT_MT = 'application/octet-stream'

def istext (s):
  if "\0" in s:
    return 0

  if not s:  # Empty files are considered text
    return 1

  # Get the non-text characters (maps a character to itself then
  # use the 'remove' option to get rid of the text characters.)
  t = s.translate(_null_trans, text_characters)

  # If more than 30% non-text characters, then
  # this is considered a binary file
  if len(t)/len(s) > 0.30:
    return 0
    
  return 1
  
  
def mimetype (fp):
  mt, enc = mimetypes.guess_type(fp)
  if mt is None:
    mt = DEFAULT_MT
    
  return mt
  
def valid_dir (target):
  def wrapper (*args, **kwargs):
    request = args[0]
    base_dir = request.user.preferences.basedir
    d = request.REQUEST.get('dir', '')
    d = os.path.normpath(d)
    
    if d.startswith(base_dir):
      return target(*args, **kwargs)
      
    raise http.Http404
    
  return wrapper
  
def valid_file (target):
  def wrapper (*args, **kwargs):
    request = args[0]
    base_dir = request.user.preferences.basedir
    f = request.REQUEST.get('file', '')
    f = os.path.normpath(f)
    
    if f.startswith(base_dir):
      return target(*args, **kwargs)
      
    raise http.Http404
    
  return wrapper
  
def good_json (msg=None):
  return http.HttpResponse(json.dumps({'result': True, 'message': msg}), mimetype=settings.JSON_MIME)
  
def bad_json (msg):
  return http.HttpResponse(json.dumps({'result': False, 'message': msg}), mimetype=settings.JSON_MIME)
  