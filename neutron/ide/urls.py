from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('ide.views',
  url('^$', 'home', name='ide-home'),
)
