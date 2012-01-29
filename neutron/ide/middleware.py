from django.conf import settings

import ide.settings

import time

class Track (object):
  def process_request (self, request):
    request.track = True
    request.track_code = ide.settings.IDE_TRACK_CODE
    
    if settings.DEBUG:
      request.track = False
      
    elif not ide.settings.IDE_TRACK:
      request.track = False
      
    return None
    