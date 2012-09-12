from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
  url(r'^admin/', include(admin.site.urls)),
  url(r'', include('neutron.ide.urls')),
)

if settings.DJANGO_SERVE_STATIC_MEDIA:
  urlpatterns += patterns('',
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:-1], 'django.views.static.serve',  {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
  )
  
if settings.DJANGO_SERVE_STATIC_MEDIA or settings.DEBUG:
  urlpatterns += patterns('',
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:-1], 'django.views.static.serve',  {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
  )
  