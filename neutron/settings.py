# Django settings for neutron project.
import os
import sys

SFILE = __file__
SPATH = os.path.normpath(os.path.dirname(SFILE))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

MEDIA_URL = '/uploads/'

STATIC_ROOT = os.path.join(SPATH, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'zlm5+9n-=flbjb*4dr_g-bl52(r=mif)h)@6ax9=af_4=2c^o9'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'ide.middleware.Track',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'neutron.urls'

TEMPLATE_DIRS = ()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    #'django.contrib.admindocs',
    'south', #http://south.aeracode.org/
    'djcelery', #http://ask.github.com/django-celery/
    'djkombu', #https://github.com/ask/django-kombu/
    'ide',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
  "django.contrib.auth.context_processors.auth",
  "django.core.context_processors.debug",
  #"django.core.context_processors.i18n",
  "django.core.context_processors.media",
  "django.core.context_processors.static",
  "django.contrib.messages.context_processors.messages",
  'django.core.context_processors.request'
)

SESSION_COOKIE_AGE = 36 * 60 * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = 'neutronsession'
SESSION_COOKIE_HTTPONLY = False

JSON_MIME = 'application/json'

CERT_DIR = os.path.normpath(os.path.join(SPATH, '..', 'cert'))
SERVER_CSR = os.path.join(CERT_DIR, 'server.csr')
SERVER_CERT = os.path.join(CERT_DIR, 'server.crt')
SERVER_KEY = os.path.join(CERT_DIR, 'server.key')
SERVER_PIDFILE = os.path.normpath(os.path.join(SPATH, '..', 'server.pid'))

BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
CELERY_RESULT_BACKEND = "database"

HTTP_PORT = 8000
IMG_EDITOR_PORT = 8001

BG_IMG = 'ide/img/neutron.jpg'

import djcelery
djcelery.setup_loader()

try:
  from neutron.settings_local import *
  
except:
  try:
    from settings_local import *
    
  except:
    pass
    
if not globals().has_key('WORKING_DIR'):
  WORKING_DIR = os.path.join(os.environ['HOME'], 'neutron')
  
if not globals().has_key('TERM_DIR'):
  TERM_DIR = os.path.join(WORKING_DIR, 'terms')
  
if not globals().has_key('LOG_DIR'):
  LOG_DIR = os.path.join(WORKING_DIR, 'logs')
  
if not globals().has_key('LOGPATH'):
  if DEBUG:
    LOGPATH = os.path.join(LOG_DIR, 'neutronide_debug.log')
    
  else:
    LOGPATH = os.path.join(LOG_DIR, 'neutronide.log')
  
if not globals().has_key('PKLPATH'):
  PKLPATH = os.path.join(WORKING_DIR, 'neutronide.pkl')
  
if not globals().has_key('MEDIA_ROOT'):
  MEDIA_ROOT = os.path.join(WORKING_DIR, 'uploads')

for d in (WORKING_DIR, LOG_DIR, TERM_DIR, MEDIA_ROOT):
  if not os.path.exists(d):
    os.makedirs(d)
    
if not globals().has_key('DATABASES'):
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
          'NAME': os.path.join(WORKING_DIR, 'neutron.sql3'),                      # Or path to database file if using sqlite3.
          'USER': '',                      # Not used with sqlite3.
          'PASSWORD': '',                  # Not used with sqlite3.
          'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
          'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
      }
  }
