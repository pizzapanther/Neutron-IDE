from django.conf import settings

MODES_DEFAULT = (
  'c_cpp', 'coffee', 'css', 'java', 'perl', 'python',
  'scss', 'xml', 'clojure', 'csharp', 'html', 'javascript', 'php',
  'ruby', 'svg'
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
