from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command (BaseCommand):
  args = '<username> <username> .... <username>'
  help = 'deletes users not in list'

  def handle(self, *args, **options):
    User.objects.exclude(username__in=args).delete()
    