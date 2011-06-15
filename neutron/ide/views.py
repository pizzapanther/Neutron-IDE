from django import http
from django.template.response import TemplateResponse

def home (request):
  return TemplateResponse(request, 'ide/home.html', {})
  