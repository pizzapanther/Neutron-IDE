from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('ide.views',
  url('^filetree/$', 'filetree', name='ide-filetree'),
  url('^fileget/$', 'fileget', name='ide-fileget'),
  url('^filesave/$', 'filesave', name='ide-filesave'),
  url('^accounts/login/$', 'login', name='ide-login'),
  url('^$', 'home', name='ide-home'),
)
