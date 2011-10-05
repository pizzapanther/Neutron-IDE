import os
import string
import urllib
import mimetypes
import base64
import random
import hashlib
mimetypes.init()

from django import http
from django.conf import settings
import django.utils.simplejson as json
from django.core.urlresolvers import reverse

import ide.settings
import ide.models

text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
_null_trans = string.maketrans("", "")

DEFAULT_MT = 'application/octet-stream'

def external_service (request, fp):
  url = None
  
  if is_image(fp):
    pdict = {}
    
    save_url = 'http://'
    temp_url = 'http://'
    if request.is_secure():
      save_url = 'https://'
      temp_url = 'https://'
      
    key = api_key()
    save_url += request.get_host() + reverse('ide-save-image', args=[fp])
    temp_url += request.get_host() + reverse('ide-ext-req', args=[key, fp])
    
    efr = ide.models.ExtFileRequest(secret=key, path=fp)
    efr.save()
    
    values = {
      'service_name': 'Neutron IDE',
      'image_url': temp_url,
      'filename': os.path.basename(fp),
      'method': 'GET',
      'save_url': save_url
    }
    
    for key, value in values.items():
      if ide.settings.IMG_PARAMS.has_key(key):
        pdict[ide.settings.IMG_PARAMS[key]] = value
        
    params = urllib.urlencode(pdict)
    url = ide.settings.IMG_EDITOR_URL + '?' + params
    
  if url:
    return http.HttpResponseRedirect(url)
    
  raise http.Http404
  
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
  
def is_image (path):
  root, ext = os.path.splitext(path)
  if ext.lower() in ide.settings.IMG_EXTENSIONS:
    return True
    
  return False
  
def mimetype (fp):
  mt, enc = mimetypes.guess_type(fp)
  if mt is None:
    mt = DEFAULT_MT
    
  return mt
  
def valid_path (request, d):
  base_dir = request.user.preferences.basedir
  d = os.path.normpath(d)
  
  if d.startswith(base_dir):
    return True
    
  return False
  
def valid_dir (target):
  def wrapper (*args, **kwargs):
    d = args[0].REQUEST.get('dir', '')
    
    if valid_path(args[0], d):
      return target(*args, **kwargs)
      
    raise http.Http404
    
  return wrapper
  
def valid_file (target):
  def wrapper (*args, **kwargs):
    f = args[0].REQUEST.get('file', '')
    
    if valid_path(args[0], f):
      return target(*args, **kwargs)
      
    raise http.Http404
    
  return wrapper
  
def good_json (msg=None):
  return http.HttpResponse(json.dumps({'result': True, 'message': msg}), mimetype=settings.JSON_MIME)
  
def bad_json (msg):
  return http.HttpResponse(json.dumps({'result': False, 'message': msg}), mimetype=settings.JSON_MIME)
  
def api_key ():
  return base64.b64encode(hashlib.sha256( str(random.getrandbits(256)) ).digest(), random.choice(['rA','aZ','gQ','hH','hG','aR','DD'])).rstrip('==')
  