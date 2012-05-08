from django import forms

import ide.models

class EditorPref (forms.ModelForm):
  class Meta:
    model = ide.models.Preferences
    exclude = ('user', 'basedir', 'session', 'bg', 'font', 'tfontsize')
    
class TermPref (forms.ModelForm):
  class Meta:
    model = ide.models.Preferences
    exclude = ('user', 'basedir', 'session', 'uitheme', 'theme', 'fontsize', \
               'keybind', 'swrap', 'tabsize', 'hactive', 'hword', 'invisibles', \
               'gutter', 'pmargin', 'softab', 'behave', 'save_session', 'splitterm')
               
    