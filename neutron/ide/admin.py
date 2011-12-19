from django.contrib import admin
from django.contrib.auth.models import User
import django.contrib.auth.admin

import ide.models

class PrefInline (admin.StackedInline):
  model = ide.models.Preferences
  
class UserAdmin (django.contrib.auth.admin.UserAdmin):
  inlines = [PrefInline,]
  
class DSAdmin(admin.ModelAdmin):
  list_display = ('user', 'id', 'state', 'created', 'updated')
  
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ide.models.DirSearch, DSAdmin)
