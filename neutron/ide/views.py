import os
import urllib

from django import http
from django.template.response import TemplateResponse
import django.utils.simplejson as json
from django.contrib.auth.decorators import login_required
import django.contrib.auth.views as auth_views

import ide.utils

def login (request):
  return auth_views.login(request)
  
@login_required
def home (request):
  try:
    base_dir = request.user.preferences.basedir
    
  except:
    return TemplateResponse(request, 'ide/message.html', {'message': 'Please fill out a user preference.'})
    
  return TemplateResponse(request, 'ide/home.html', {})
  
@login_required
def fileget (request):
  try:
    base_dir = request.user.preferences.basedir
    
    f = request.POST.get('f', '')
    f = os.path.normpath(f)
    if not f.startswith(base_dir):
      raise http.Http404
      
    fh = open(f, 'rb')
    if ide.utils.istext(fh.read(512)):
      fh.seek(0)
      ret = {'fileType': 'text', 'data': fh.read(), 'path': f, 'filename': os.path.basename(f)}
      
    else:
      ret = {'fileType': 'binary', }
      
    return http.HttpResponse(json.dumps(ret), mimetype='application/json')
    
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
