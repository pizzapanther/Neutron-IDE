from django.db import models
from django.contrib.auth.models import User

THEMES = (
  ('ace/theme/textmate', 'TextMate'),
  ('ace/theme/eclipse', 'Eclipse'),
  ('ace/theme/dawn', 'Dawn'),
  ('ace/theme/idle_fingers', 'idleFingers'),
  ('ace/theme/pastel_on_dark', 'Pastel on dark'),
  ('ace/theme/twilight', 'Twilight'),
  ('ace/theme/clouds', 'Clouds'),
  ('ace/theme/clouds_midnight', 'Clouds Midnight'),
  ('ace/theme/kr_theme', 'krTheme'),
  ('ace/theme/mono_industrial', 'Mono Industrial'),
  ('ace/theme/monokai', 'Monokai'),
  ('ace/theme/merbivore', 'Merbivore'),
  ('ace/theme/merbivore_soft', 'Merbivore Soft'),
  ('ace/theme/vibrant_ink', 'Vibrant Ink'),
  ('ace/theme/solarized_dark', 'Solarized Dark'),
  ('ace/theme/solarized_light', 'Solarized Light')
)

SIZES = (
  ('10px', '10px'),
  ('11px', '11px'),
  ('12px', '12px'),
  ('13px', '13px'),
  ('14px', '14px'),
  ('15px', '15px'),
  ('16px', '16px'),
  ('17px', '17px'),
  ('18px', '18px'),
  ('19px', '19px'),
  ('20px', '20px'),
  ('21px', '21px'),
  ('22px', '22px'),
  ('23px', '23px'),
  ('24px', '24px'),
)

KBINDS = (
  ('ace', 'Ace'),
  ('vim', 'Vim'),
  ('emacs', 'Emacs')
)

WRAPS = (
  ('off', 'Off'),
  ('40', '40 Chars'),
  ('80', '80 Chars'),
  ('free', 'Free')
)

class Preferences (models.Model):
   user = models.OneToOneField(User)
   
   basedir = models.CharField('Base Directory', max_length=255)
   
   theme = models.CharField(choices=THEMES, max_length=50, default='ace/theme/textmate')
   fontsize = models.CharField('Font Size', choices=SIZES, max_length=10, default='12px')
   keybind = models.CharField('Key Bindings', choices=KBINDS, max_length=10, default='ace')
   swrap = models.CharField('Soft Wrap', choices=WRAPS, max_length=10, default='off')
   hactive = models.BooleanField('Highlight Active Line', default=True)
   hword = models.BooleanField('Highlight Selected Word', default=True)
   invisibles = models.BooleanField('Show Invisibles', default=False)
   gutter = models.BooleanField('Show Gutter', default=True)
   pmargin = models.BooleanField('Show Print Margin', default=True)
   softab = models.BooleanField('User Soft Tab', default=True)
   