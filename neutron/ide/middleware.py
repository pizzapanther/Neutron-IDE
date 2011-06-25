import time

class Logging (object):
  def process_response (self, request, response):
    if request.META.has_key('SERVER_SOFTWARE'):
      if 'CherryPy' in request.META['SERVER_SOFTWARE']:
        print "[%s] \"%s %s\" %d %d" % (time.strftime("%d/%b/%Y %H:%M:%S", time.localtime()), request.method, request.get_full_path(), response.status_code, len(response.content))
        
    return response
    
