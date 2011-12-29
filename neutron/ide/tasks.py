from celery.task import task

import ide.models

@task
def ctest (x, y):
  ret = x + y
  print "TEST"
  print ret
  
  return ret
  
@task
def dir_search (search_id):
  print "Search: %d" % search_id
  ds = ide.models.DirSearch.objects.get(id=search_id)
  ds.do_search()
  print "Search Complete: %d" % search_id
  
@task
def dir_replace (search_id):
  print "Replace: %d" % search_id
  ds = ide.models.DirSearch.objects.get(id=search_id)
  ds.do_replace()
  print "Replace Complete: %d" % search_id
  