from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import redirect_to

urlpatterns = patterns('ide.views',
  url('^filetree/$', 'filetree', name='ide-filetree'),
  url('^dirchooser/$', 'dirchooser', name='ide-dirchooser'),
  url('^fileget/$', 'fileget', name='ide-fileget'),
  url('^filesave/$', 'filesave', name='ide-filesave'),
  url('^accounts/login/$', 'login', name='ide-login'),
  url('^favicon.ico$', redirect_to, {'url': settings.STATIC_URL + 'ide/img/favicon.ico'}, name='ide-favicon.ico'),
  url('^new/$', 'new', name='ide-new'),
  url('^delete/$', 'remove', name='ide-delete'),
  url('^rename/$', 'rename', name='ide-rename'),
  url('^temp_file/$', 'temp_file', name='ide-temp-file'),
  url('^view_file(?P<fp>.+)$', 'view_file', name='ide-view-file'),
  url('^external_open(?P<fp>.+)$', 'external_open', name='ide-ext-open'),
  url('^save_image(?P<fp>.+)$', 'save_image', name='ide-save-image'),
  url('^external_request/(?P<key>.+)/fp(?P<fp>.+)$', 'external_request', name='ide-ext-req'),
  url('^save_session/$', 'save_session', name='ide-save-session'),
  url('^editor_pref/$', 'editor_pref', name='ide-editor-pref'),
  
  url('^dir_search/$', 'submit_search', name='ide-dir-search'),
  url('^check_search/$', 'check_search', name='ide-check-search'),
  
  url('^dir_replace/$', 'submit_replace', name='ide-dir-replace'),
  url('^check_replace/$', 'check_replace', name='ide-check-replace'),
  
  url('^$', 'home', name='ide-home'),
)
