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

TEXT_EXTENSIONS = getattr(settings, 'TEXT_EXTENSIONS', TEXT_EXTENSIONS_DEFAULT)
MODES = getattr(settings, 'MODES', MODES_DEFAULT)
THEMES = getattr(settings, 'THEMES', THEMES_DEFAULT)
