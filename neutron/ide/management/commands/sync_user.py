from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from ide.models import Preferences

class Command (BaseCommand):
  args = '<username> <project_dir> <password_hash>'
  help = 'creates user or just syncs password'

  def handle(self, *args, **options):
    if len(args) == 3:
      username = args[0]
      bdir = args[1]
      pwd = args[2]
      
      user, created = User.objects.get_or_create(username=username, defaults={'is_staff': True, 'is_superuser': True})
      user.password = pwd
      user.save()
        
      if created:
        pref = Preferences(user=user, basedir=bdir)
        pref.save()
        
    else:
      raise CommandError('Invalid arguments.')
      