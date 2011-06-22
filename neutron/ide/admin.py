from django.contrib import admin
from django.contrib.auth.models import User
import django.contrib.auth.admin

import ide.models

class PrefInline (admin.StackedInline):
  model = ide.models.Preferences
  
class UserAdmin (django.contrib.auth.admin.UserAdmin):
  inlines = [PrefInline,]
  
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
