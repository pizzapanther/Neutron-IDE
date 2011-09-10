import hashlib

from django import template

register = template.Library()

@register.filter
def hashstr (value):
  return hashlib.sha256(value).hexdigest()
  