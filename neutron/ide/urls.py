from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import redirect_to

urlpatterns = patterns('ide.views',
  url('^filetree/$', 'filetree', name='ide-filetree'),
  url('^fileget/$', 'fileget', name='ide-fileget'),
  url('^filesave/$', 'filesave', name='ide-filesave'),
  url('^accounts/login/$', 'login', name='ide-login'),
  url('^favicon.ico$', redirect_to, {'url': settings.STATIC_URL + 'ide/img/favicon.ico'}, name='ide-favicon.ico'),
  url('^new/$', 'new', name='ide-new'),
  url('^delete/$', 'remove', name='ide-delete'),
  url('^temp_file/$', 'temp_file', name='ide-temp-file'),
  url('^view_file/$', 'view_file', name='ide-view-file'),
  url('^$', 'home', name='ide-home'),
)
