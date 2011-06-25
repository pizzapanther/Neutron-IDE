import os
import urllib

from django import http
from django.conf import settings
from django.template.response import TemplateResponse
import django.utils.simplejson as json
from django.contrib.auth.decorators import login_required
import django.contrib.auth.views as auth_views

import ide.utils
import ide.settings

def login (request):
  return auth_views.login(request)
  
@login_required
def home (request):
  try:
    base_dir = request.user.preferences.basedir
    
  except:
    return TemplateResponse(request, 'ide/message.html', {'message': 'Please fill out a user preference.'})
    
  return TemplateResponse(request, 'ide/home.html', {'MODES': ide.settings.MODES})
  
@login_required
def filesave (request):
  ret = 'bad'
  error = None
  
  path = request.POST.get('path', '')
  contents = request.POST.get('contents', '')
    
  if path == '':
    error = 'Bad Request'
    
  else:
    if request.user.preferences.valid_path(path):
      try:
        fh = open(path, 'w')
        fh.write(contents)
        
      except:
        error = 'Error writing file to disk.'
        
      else:
        fh.close()
        ret = 'good'
        
    else:
      error = 'File Access Denied'
      
  return http.HttpResponse(json.dumps({'result': ret, 'error': error}), mimetype=settings.JSON_MIME)
    
@login_required
def fileget (request):
  try:
    base_dir = request.user.preferences.basedir
    
    f = request.POST.get('f', '')
    f = os.path.normpath(f)
    if not f.startswith(base_dir):
      raise http.Http404
      
    fh = open(f, 'rb')
    mode = None
    
    if ide.utils.istext(fh.read(512)):
      fh.seek(0)
      
      root, ext = os.path.splitext(f)
      if ext[1:].lower() in ide.settings.TEXT_EXTENSIONS.keys():
        mode = ide.settings.TEXT_EXTENSIONS[ext[1:].lower()]
        
      ret = {
        'fileType': 'text',
        'data': fh.read(),
        'path': f,
        'filename': os.path.basename(f),
        'mode': mode
      }
      
    else:
      ret = {'fileType': 'binary', }
      
    return http.HttpResponse(json.dumps(ret), mimetype=settings.JSON_MIME)
    
  except:
    import traceback
    traceback.print_exc()
    
@login_required
def filetree (request):
  r = ['<ul class="jqueryFileTree" style="display: none;">']
  show_hidden = False
  base_dir = request.user.preferences.basedir
  
  try:
    r = ['<ul class="jqueryFileTree" style="display: none;">']
    d = urllib.unquote(request.POST.get('dir', ''))
    
    if not d.startswith(base_dir):
      d = os.path.join(base_dir, d)
      
    d = os.path.normpath(d)
    if not d.startswith(base_dir):
      r.append('Invalid directory: %s' % str(d))
      
    fdlist = os.listdir(d)
    fdlist.sort()
    
    files = []
    dirs = []
    
    for f in fdlist:
      go = False
      if f.startswith('.'):
        if show_hidden:
          go = True
          
      else:
        go = True
        
      if go:
        ff = os.path.join(d,f)
        if os.path.isdir(ff):
          dirs.append((ff,f))
          
        else:
          e = os.path.splitext(f)[1][1:] # get .ext and remove dot
          files.append((e,ff,f))
          
    for d in dirs:
      r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (d[0], d[1]))
      
    for f in files:
      r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (f[0], f[1], f[2]))
      
    r.append('</ul>')
    
  except Exception,e:
    r.append('Could not load directory: %s' % str(e))
    
  r.append('</ul>')
  
  return http.HttpResponse(''.join(r))
