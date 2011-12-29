import os
import re
import time
import glob
import cPickle as pickle

from django.db import models
from django.contrib.auth.models import User
import django.utils.simplejson as json

from ide.grep import Grep
from ide.templatetags.ntags import hashstr

THEMES = (
  ('textmate', 'TextMate'),
  ('eclipse', 'Eclipse'),
  ('dawn', 'Dawn'),
  ('idle_fingers', 'idleFingers'),
  ('pastel_on_dark', 'Pastel on dark'),
  ('twilight', 'Twilight'),
  ('clouds', 'Clouds'),
  ('clouds_midnight', 'Clouds Midnight'),
  ('crimson_editor', 'Crimson'),
  ('kr_theme', 'krTheme'),
  ('mono_industrial', 'Mono Industrial'),
  ('monokai', 'Monokai'),
  ('merbivore', 'Merbivore'),
  ('merbivore_soft', 'Merbivore Soft'),
  ('vibrant_ink', 'Vibrant Ink'),
  ('solarized_dark', 'Solarized Dark'),
  ('solarized_light', 'Solarized Light'),
)

UI_THEMES = (
  ('kendo', 'Kendo'),
  ('black', 'Black'),
  ('blueopal', 'Blue Opal'),
)

SIZES = (
  ('6px', '6px'),
  ('7px', '7px'),
  ('8px', '8px'),
  ('9px', '9px'),
  ('10px', '10px'),
  ('11px', '11px'),
  ('12px', '12px'),
  ('13px', '13px'),
  ('14px', '14px'),
  ('15px', '15px'),
  ('16px', '16px'),
  ('17px', '17px'),
  ('18px', '18px'),
  ('19px', '19px'),
  ('20px', '20px'),
  ('21px', '21px'),
  ('22px', '22px'),
  ('23px', '23px'),
  ('24px', '24px'),
)

KBINDS = (
  ('ace', 'Ace'),
  ('vim', 'Vim'),
  ('emacs', 'Emacs')
)

WRAPS = (
  ('off', 'Off'),
  ('40', '40 Chars'),
  ('80', '80 Chars'),
  ('free', 'Free')
)

class TempFile (models.Model):
  user = models.ForeignKey(User)
  file = models.FileField(upload_to='tmp')
  
class ExtFileRequest (models.Model):
  secret = models.CharField(max_length=255)
  path = models.TextField(max_length=255)
  created = models.DateTimeField(auto_now_add=True)
  
class Preferences (models.Model):
  user = models.OneToOneField(User)

  basedir = models.CharField('Base Directory', max_length=255)
  
  uitheme = models.CharField('UI Theme', choices=UI_THEMES, max_length=25, default='kendo')
  
  theme = models.CharField('Editor Theme', choices=THEMES, max_length=25, default='textmate')
  fontsize = models.CharField('Font Size', choices=SIZES, max_length=10, default='12px')
  keybind = models.CharField('Key Bindings', choices=KBINDS, max_length=10, default='ace')
  swrap = models.CharField('Soft Wrap', choices=WRAPS, max_length=10, default='off')
  
  tabsize = models.IntegerField('Tab Size', default=4)
  
  hactive = models.BooleanField('Highlight Active Line', default=True)
  hword = models.BooleanField('Highlight Selected Word', default=True)
  invisibles = models.BooleanField('Show Invisibles', default=False)
  gutter = models.BooleanField('Show Gutter', default=True)
  pmargin = models.BooleanField('Show Print Margin', default=True)
  softab = models.BooleanField('Use Soft Tab', default=True)
  behave = models.BooleanField('Enable Behaviors', default=True)
  
  save_session = models.BooleanField('Save Session', default=True)
  session = models.TextField(blank=True, null=True)
  
  def last_session (self):
    if self.session:
      return json.dumps(self.session.split("\n"))
      
    return '[]';
    
  def valid_path (self, path):
    path = os.path.normpath(path)
    if path.startswith(self.basedir):
      return True
      
    return False
    
class DirSearch (models.Model):
  user = models.ForeignKey(User)
  opts = models.TextField()
  
  state = models.CharField(max_length=25, default='created')
  replace_state = models.CharField(max_length=25, blank=True, null=True)
  
  results = models.TextField(blank=True, null=True)
  replace_results = models.TextField(blank=True, null=True)
  
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  
  class Meta:
    verbose_name = 'Directory Search Job'
    
  def make_needle (self):
    needle = ''
    opts = self.get_opts()
    
    regex = False
    flags = re.I
    
    if opts['caseSensitive'] == 'true':
      flags = 0
      
    if opts['regExp'] == 'true':
      regex = True
      
    if regex:
      if opts['wholeWord'] == 'true':
        needle = re.compile(r"\b" + opts['needle'] + r"\b", flags=flags)
        
      else:
        needle = re.compile(opts['needle'], flags=flags)
        
    else:
      if opts['wholeWord'] == 'true':
        needle = re.compile(r"\b" + re.escape(opts['needle'] + r"\b"), flags=flags)
        
      else:
        needle = re.compile(re.escape(opts['needle']), flags=flags)
        
    return needle
    
  def do_search (self):
    self.state = 'running'
    self.save()
    opts = self.get_opts()
    needle = self.make_needle()
    results = []
    
    for root, dirs, files in os.walk(opts['dir']):
      if opts['glob']:
        files = glob.glob(root + '/' + opts['glob'])
        
      if files:
        for file in files:
          fp = os.path.join(root, file)
          uid = hashstr(fp)
          
          if opts['needle']:
            grep = Grep(fp, needle)
            grep_results = grep.results()
            if grep_results:
              results.append((fp, uid, grep_results))
              
          else:
            results.append((fp, uid, []))
            
        self.set_results(results)
        
    self.state = 'complete'
    self.save()
    
  def do_replace (self):
    self.replace_state = 'running'
    self.save()
    
    for r in self.get_results():
      needle = self.make_needle()
      opts = self.get_opts()
      rlines = [x[0] for x in r[2]]
      
      grep = Grep(r[0], needle)
      grep.replace(opts['replace'], rlines)
      if self.replace_results:
        self.replace_results += '\n' + r[0]
        
      else:
        self.replace_results = r[0]
        
      self.save()
      
    self.replace_state = 'complete'
    self.save()
    
  def get_opts (self):
    return pickle.loads(str(self.opts))
    
  def get_results (self):
    return pickle.loads(str(self.results))
    
  def set_results (self, results):
    self.results = pickle.dumps(results)
    self.save()
    