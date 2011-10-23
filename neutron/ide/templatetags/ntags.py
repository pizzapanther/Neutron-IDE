import hashlib

from django import template

register = template.Library()

@register.filter
def hashstr (value):
  return hashlib.sha256(value).hexdigest()
  
@register.filter
def js_bool (value):
  if value:
    return 'true'
    
  return 'false'
  