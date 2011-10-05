from django.conf import settings

MODES_DEFAULT = (
  'c_cpp', 'coffee', 'css', 'java', 'perl', 'python',
  'scss', 'xml', 'clojure', 'csharp', 'html', 'javascript', 'php',
  'ruby', 'svg'
)

THEMES_DEFAULT = (
  'clouds', 'cobalt', 'eclipse', 'kr_theme', 'merbivore_soft',
  'monokai', 'twilight', 'clouds_midnight', 'dawn', 'idle_fingers',
  'merbivore', 'mono_industrial', 'pastel_on_dark', 'vibrant_ink'
)

TEXT_EXTENSIONS_DEFAULT = {
  'clj': 'clojure',
  
  'c': 'c_cpp', 'cpp': 'c_cpp',
  
  'cof': 'coffee',
  
  'cs': 'csharp',
  
  'css': 'css',
  
  'htm': 'html', 'html': 'html',
  
  'java': 'java', 'class': 'java', 'jsp': 'java',
  
  'js': 'javascript', 'json': 'javascript',
  
  'php': 'php',
  
  'pl': 'perl', 'pm': 'perl',
  
  'py': 'python',
  
  'rb': 'ruby', 'rbx': 'ruby',
  
  'sass': 'scss', 'scss': 'scss',
  
  'svg': 'svg',
  
  'xml': 'xml', 'rss': 'xml', 'atom': 'xml',
}

SITE_NAME_DEFAULT = 'Neutron IDE'

IMG_EXTENSIONS_DEFAULT = ('.jpg', '.jpeg', '.png', '.bmp', '.pxd')
IMG_EDITOR_URL_DEFAULT = 'http://pixlr.com/editor/'
IMG_EDITOR_READ_DEFAULT = 'image'
IMG_PARAMS_DEFAULT = {
  'service_name': 'referrer',
  'image_url': 'image',
  'filename': 'title',
  'method': 'method',
  'save_url': 'target',
}

TEXT_EXTENSIONS = getattr(settings, 'TEXT_EXTENSIONS', TEXT_EXTENSIONS_DEFAULT)
MODES = getattr(settings, 'MODES', MODES_DEFAULT)
THEMES = getattr(settings, 'THEMES', THEMES_DEFAULT)

SITE_NAME = getattr(settings, 'SITE_NAME', SITE_NAME_DEFAULT)

IMG_EXTENSIONS = getattr(settings, 'IMG_EXTENSIONS', IMG_EXTENSIONS_DEFAULT)
IMG_EDITOR_URL = getattr(settings, 'IMG_EDITOR_URL', IMG_EDITOR_URL_DEFAULT)
IMG_EDITOR_READ = getattr(settings, 'IMG_EDITOR_READ', IMG_EDITOR_READ_DEFAULT)
IMG_PARAMS = getattr(settings, 'IMG_PARAMS', IMG_PARAMS_DEFAULT)

