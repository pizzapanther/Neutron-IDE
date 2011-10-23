from django.forms import ModelForm

import ide.models

class EditorPref (ModelForm):
  class Meta:
    model = ide.models.Preferences
    exclude = ('user', 'basedir', 'session')
    