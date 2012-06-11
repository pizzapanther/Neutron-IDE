import os
import time
import shutil
import codecs
import urllib
import datetime
import cPickle as pickle
import traceback
import pprint

from django.contrib.auth.signals import user_logged_in
from django import http
from django.conf import settings
from django.template.response import TemplateResponse
import django.utils.simplejson as json
from django.contrib.auth.decorators import login_required
import django.contrib.auth.views as auth_views
from django.template.loader import render_to_string
from django.core.files.uploadedfile import SimpleUploadedFile
from django.views.static import serve
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

import ide.utils
import ide.settings
import ide.models
import ide.forms
import ide.tasks
from ide.templatetags.ntags import hashstr

GOOD_CSTATES = ("SUCCESS", "STARTED", "RECEIVED")

def user_folder_check (sender, user, request, **kwargs):
  theFolder = settings.USERDIR + "/" + user.username
  prefs = ide.models.Preferences.objects.get(user=user)
  if not prefs == None:
    if not prefs.basedir == theFolder :
      prefs.basedir = theFolder
      prefs.save()
      if not os.path.exists(theFolder):
        os.mkdir(theFolder)
  
user_logged_in.connect(user_folder_check)

def login (request):
  return auth_views.login(request)
  
@login_required
def home (request):
  try:
    base_dir = request.user.preferences.basedir
    
  except:
    return TemplateResponse(request, 'ide/message.html', {'message': 'Please fill out a user preference.'})
    
  C_ON = False
  if ide.settings.SKIP_CELERY_CHECK:
    C_ON = ide.settings.CELERY_ON
    
  else:
    result = ide.tasks.ctest.delay(4, 5)
    for i in range(0, 10):
      if result.ready() or result.state in GOOD_CSTATES:
        C_ON = True
        break
        
      else:
        print result.ready(), result.state
        time.sleep(1)
        
  c = {
    'MODES': ide.settings.MODES,
    'THEMES': ide.settings.THEMES,
    'dir': base_dir,
    'did': 'file_browser',
    'd': base_dir,
    'CELERY_ON': C_ON,
    'TERMINAL_ON': ide.settings.TERMINAL_ON
  }
  
  return TemplateResponse(request, 'ide/home.html', c)
  
@login_required
def temp_file (request):
  fn = request.GET.get('name')
  
  mt = ide.utils.mimetype(fn)
  f = SimpleUploadedFile(fn, request.raw_post_data, mt)
  
  t = ide.models.TempFile(file=f, user=request.user)
  t.save()
  
  return ide.utils.good_json(t.id)
  
@login_required
@ide.utils.valid_dir
def new (request):
  d = request.REQUEST.get('dir', '')
  new_type = request.REQUEST.get('new_type', '')
  name = request.REQUEST.get('name', '')
  
  fp = os.path.join(d, name)
  
  if new_type == 'file':
    if os.path.exists(fp):
      return ide.utils.bad_json('File Exists Already')
      
    fh = open(fp, 'w')
    fh.close()
    
  elif new_type == 'dir':
    if os.path.exists(fp):
      return ide.utils.bad_json('Directory Exists Already')
      
    os.mkdir(fp)
    
  elif new_type == 'url':
    uh = urllib.urlopen(name)
    
    if uh.info().has_key('Content-Disposition'):
      if 'filename' in uh.info()['Content-Disposition']:
        fn = uh.info()['Content-Disposition'].split('filename=')[1]
        
      else:
        fn = uh.info()['Content-Disposition']
        
      if fn[0] == '"' or fn[0] == "'":
        fn = fn[1:-1]
        
    else:
      fn = name.split('/')[-1]
      if fn == '':
        fn = time.strftime("%Y%m%d_%H%M%S.file", time.gmtime())
        
    fp = os.path.join(d, fn)
    if os.path.exists(fp):
      return ide.utils.bad_json('File Exists Already')
      
    fh = open(fp, 'wb')
    while 1:
      data = uh.read()
      fh.write(data)
      
      if not data:
        break
        
    fh.close()
    uh.close()
    
  else:
    tf = request.REQUEST.get('temp_file')
    tf = ide.models.TempFile.objects.get(id=tf, user=request.user)
    
    name = os.path.basename(tf.file.path)
    
    fp = os.path.join(d, name)
    if os.path.exists(fp):
      tf.file.delete()
      tf.delete()
      return ide.utils.bad_json('File Exists Already')
      
    shutil.move(tf.file.path, fp)
    tf.delete()
    
  return ide.utils.good_json()
  
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
        fh = codecs.open(path, encoding='utf-8', mode='w')
        fh.write(contents)
        
      except:
        error = 'Error writing file to disk.'
        
      else:
        fh.close()
        ret = 'good'
        
    else:
      error = 'File Access Denied'
      
  return http.HttpResponse(json.dumps({'result': ret, 'error': error, 'uid': hashstr(path)}), mimetype=settings.JSON_MIME)
    
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
        'mode': mode,
        'uid': hashstr(f)
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
      did = hashstr(d[0])
      rm = render_to_string('ide/right_menu_dir.html', {'dir': d[0], 'did': did, 'd': os.path.basename(d[0])})
      r.append('<li class="directory collapsed" id="%s" title="%s">%s<a href="#" rel="%s/">%s</a></li>' % (did, d[0], rm, d[0], d[1]))
      
    for f in files:
      fid = hashstr(f[1])
      rm = render_to_string('ide/right_menu_file.html', {'f': f[2], 'fid': fid, 'file': f[1]})
      r.append('<li class="file ext_%s" id="%s">%s<a href="#" rel="%s">%s</a></li>' % (f[0], fid, rm, f[1], f[2]))
        
    r.append('</ul>')
    
  except Exception,e:
    r.append('Could not load directory: %s' % str(e))
    
  r.append('</ul>')
  return http.HttpResponse(''.join(r))
  
@login_required
def dirchooser (request):
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
      short = urllib.quote(d[0].replace(base_dir + '/', ''))
      r.append('<li class="directory collapsed" title="%s"><a href="#" rel="%s/" onclick="choose_me(\'%s\')">%s</a></li>' % (d[0], d[0], short, d[1]))
      
    r.append('</ul>')
    
  except Exception,e:
    r.append('Could not load directory: %s' % str(e))
    
  r.append('</ul>')
  return http.HttpResponse(''.join(r))

  
@login_required
def view_file (request, fp=None):
  if ide.utils.valid_path(request, fp):
    fn = os.path.basename(fp)
    ret = serve(request, fp, document_root="/")
    ret['Content-Disposition'] = 'filename=%s' % fn
    return ret
    
  raise http.Http404
  
@login_required
def external_open (request, fp=None):
  if ide.utils.valid_path(request, fp):
    return ide.utils.external_service(request, fp)
    
  raise http.Http404
  
@csrf_exempt
@login_required
def save_image (request, fp=None):
  if ide.utils.valid_path(request, fp):
    fw = open(fp, 'wb')
    url = request.REQUEST.get(ide.settings.IMG_EDITOR_READ)
    fr = urllib.urlopen(url)
    fw.write(fr.read())
    fw.close()
    fr.close()
    
    return TemplateResponse(request, 'ide/close.html', {})
    
  raise http.Http404
  
def external_request (request, key=None, fp=None):
  efr = get_object_or_404(ide.models.ExtFileRequest, secret=key, path=fp)
  if settings.DEBUG:
    old = datetime.datetime.now() - datetime.timedelta(seconds=300)
    
  else:
    old = datetime.datetime.now() - datetime.timedelta(seconds=30)
    
  if efr.created > old:
    ret = serve(request, fp, document_root="/")
    
    return ret
    
  if not setting.DEBUG:
    efr.delete()
    
  raise http.Http404
  
@login_required
@ide.utils.valid_dir
def remove (request):
  path = request.REQUEST.get('dir')
  if os.path.isdir(path):
    shutil.rmtree(path)
    
  else:
    os.remove(path)
  
  d = os.path.dirname(path)
  if d == request.user.preferences.basedir:
    did = 'file_browser'
    
  else:
    did = hashstr(d)
    
  return ide.utils.good_json(did)
  
@login_required
@ide.utils.valid_dir
def rename (request):
  path = request.REQUEST.get('dir')
  name = request.REQUEST.get('name')
  
  d = os.path.dirname(path)
  newpath = os.path.join(d, name)
  
  if os.path.exists(newpath):
    return ide.utils.bad_json('Destination Exists Already')
    
  os.rename(path, newpath)
  if d == request.user.preferences.basedir:
    did = 'file_browser'
    
  else:
    did = hashstr(d)
    
  return ide.utils.good_json(did)
  
@login_required
def save_session (request):
  if request.user.preferences.save_session:
    files = request.POST.get('files', '')
    request.user.preferences.session = files
    
  else:
    request.user.preferences.session = ''
    
  request.user.preferences.save()
  
  return ide.utils.good_json()
  
@login_required
def editor_pref (request):
  form = ide.forms.EditorPref(request.POST or None, instance=request.user.preferences)
  
  if request.method == 'POST' and form.is_valid():
    form.save()
    
    p = request.user.preferences
    new_prefs = {
      'uitheme': p.uitheme,
      
      'theme': p.theme,
      'fontsize': p.fontsize,
      'keybind': p.keybind,
      'swrap': p.swrap,
      'tabsize': p.tabsize,
      
      'hactive': p.hactive,
      'hword': p.hword,
      'invisibles': p.invisibles,
      'gutter': p.gutter,
      'pmargin': p.pmargin,
      'softab': p.softab,
      'behave': p.behave,
      
      'save_session': p.save_session,
    }
    return TemplateResponse(request, 'ide/editor_pref_success.html', {'new_prefs': json.dumps(new_prefs)})
    
  return TemplateResponse(request, 'ide/editor_pref.html', {'form': form})
  
@login_required
def term_pref (request):
  form = ide.forms.TermPref(None, instance=request.user.preferences)
  
  if request.method == 'POST':
    form = ide.forms.TermPref(request.POST, request.FILES, instance=request.user.preferences)
    
    if form.is_valid():
      form.save()
      
      p = request.user.preferences
      
      if p.bg:
        bgurl = p.bg.url
        
      else:
        bgurl = settings.STATIC_URL + ide.settings.BG_IMG
        
      new_prefs = {
        'bg': bgurl,
        'font': p.font,
        'fontsize': p.tfontsize,
      }
      return TemplateResponse(request, 'ide/term_pref_success.html', {'new_prefs': json.dumps(new_prefs)})
      
  return TemplateResponse(request, 'ide/term_pref.html', {'form': form})
  
@login_required
@ide.utils.valid_dir
def submit_search (request):
  try:
    opts = {
      'wholeWord': request.POST.get('wholeWord', 'false'),
      'glob': request.POST.get('glob', ''),
      'needle': request.POST.get('needle', ''),
      'caseSensitive': request.POST.get('caseSensitive', 'false'),
      'regExp': request.POST.get('regExp', 'false'),
      'dir': request.POST.get('dir', request.user.preferences.basedir),
      'replace': request.POST.get('replace', ''),
    }
    
    opts_str = pickle.dumps(opts)
    
    ds = ide.models.DirSearch(user=request.user, opts=opts_str)
    ds.save()
    
    result = ide.tasks.dir_search.delay(ds.id)
    
    return http.HttpResponse(json.dumps({'result': 1, 'task_id': result.task_id, 'dsid': ds.id}), mimetype=settings.JSON_MIME)
    
  except:
    traceback.print_exc()
    raise
    
@login_required
def check_search (request):
  dsid = request.REQUEST.get('ds', '')
  task = request.REQUEST.get('task', '')
  
  try:
    ds = get_object_or_404(ide.models.DirSearch, id=dsid, user=request.user)
    if ds.results:
      dumpme = {'task_id': task, 'dsid': dsid, 'state': ds.state, 'results': ds.get_results()}
      
    else:
      dumpme = {'task_id': task, 'dsid': dsid, 'state': ds.state, 'results': []}
      
    return http.HttpResponse(json.dumps(dumpme), mimetype=settings.JSON_MIME)
    
  except:
    traceback.print_exc()
    raise
    
@login_required
def check_replace (request):
  dsid = request.REQUEST.get('ds', '')
  task = request.REQUEST.get('task', '')
  
  ds = get_object_or_404(ide.models.DirSearch, id=dsid, user=request.user)
  if ds.replace_results:
    dumpme = {'task_id': task, 'dsid': dsid, 'state': ds.replace_state, 'last_file': ds.replace_results.split('\n')[-1]}
    
  else:
    dumpme = {'task_id': task, 'dsid': dsid, 'state': ds.replace_state, 'last_file': 'Waiting to start'}
    
  return http.HttpResponse(json.dumps(dumpme), mimetype=settings.JSON_MIME)
  
@login_required
def cancel_job (request):
  dsid = request.REQUEST.get('ds', '')
  task = request.REQUEST.get('task', '')
  jtype = request.REQUEST.get('jtype', 'search')
  
  ds = get_object_or_404(ide.models.DirSearch, id=dsid, user=request.user)
  
  jk = ide.models.JobKill(ds=ds)
  jk.save()
  
  while 1:
    print 'checking', datetime.datetime.now()
    ds = ide.models.DirSearch.objects.get(id=dsid, user=request.user)
    if ds.killed:
      return http.HttpResponse(json.dumps({'result': True}), mimetype=settings.JSON_MIME)
      
    if jtype == 'search' and ds.state == 'complete':
      return http.HttpResponse(json.dumps({'result': False}), mimetype=settings.JSON_MIME)
      
    if jtype == 'replace' and ds.replace_state == 'complete':
      return http.HttpResponse(json.dumps({'result': False}), mimetype=settings.JSON_MIME)
      
    time.sleep(1)
    
@login_required
def submit_replace (request):
  dsid = request.REQUEST.get('ds', '')
  ds = get_object_or_404(ide.models.DirSearch, id=dsid, user=request.user)
  result = ide.tasks.dir_replace.delay(ds.id)
  
  return http.HttpResponse(json.dumps({'result': 1, 'task_id': result.task_id, 'dsid': ds.id}), mimetype=settings.JSON_MIME)
  
@login_required
def terminal (request):
  if ide.settings.TERMINAL_ON:
    split_term = request.GET.get('split', '')
    if request.user.preferences.bg:
      bg = request.user.preferences.bg.url
      
    else:
      bg = settings.STATIC_URL + ide.settings.BG_IMG
      
    c = {
      'cookie': settings.SESSION_COOKIE_NAME,
      'bg': bg,
      'font': request.user.preferences.font,
      'fontsize': request.user.preferences.tfontsize
    }
    
    if split_term == '1':
      return TemplateResponse(request, 'ide/terminal_split.html', c)
      
    return TemplateResponse(request, 'ide/terminal.html', c)
    
  else:
    raise http.Http404
    
