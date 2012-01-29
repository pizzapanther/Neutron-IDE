from django.conf import settings

MODES_DEFAULT = (
  'c_cpp', 'coffee', 'css', 'java', 'perl', 'python',
  'scss', 'xml', 'clojure', 'csharp', 'html', 'javascript', 'php',
  'ruby', 'svg', 'groovy', 'json', 'ocaml', 'scad', 'scala', 'textile'
)

THEMES_DEFAULT = (
  'clouds', 'cobalt', 'eclipse', 'kr_theme', 'merbivore_soft',
  'monokai', 'twilight', 'clouds_midnight', 'dawn', 'idle_fingers',
  'merbivore', 'mono_industrial', 'pastel_on_dark', 'vibrant_ink',
  'textmate', 'crimson_editor', 'solarized_dark', 'solarized_light'
)

TEXT_EXTENSIONS_DEFAULT = {
  'clj': 'clojure',
  
  'c': 'c_cpp', 'cpp': 'c_cpp',
  
  'cof': 'coffee',
  
  'cs': 'csharp',
  
  'css': 'css',
  
  'htm': 'html', 'html': 'html',
  
  'java': 'java', 'class': 'java', 'jsp': 'java',
  
  'js': 'javascript',
  
  'json': 'json',
  
  'php': 'php',
  
  'pl': 'perl', 'pm': 'perl',
  
  'py': 'python',
  
  'rb': 'ruby', 'rbx': 'ruby',
  
  'sass': 'scss', 'scss': 'scss', 'less': 'scss',
  
  'svg': 'svg',
  
  'xml': 'xml', 'rss': 'xml', 'atom': 'xml',
  
  'groovy': 'groovy',
  
  'ml': 'ocaml', 'mli': 'ocaml', 'mll': 'ocaml',
  
  'scad': 'scad',
  
  'scala': 'scala', 
  
  'textile': 'textile',
}

SITE_NAME_DEFAULT = 'Neutron IDE'

IMG_EXTENSIONS_DEFAULT = ('.jpg', '.jpeg', '.png', '.bmp', '.pxd')
IMG_EDITOR_URL_DEFAULT = 'http://www.aviary.com/online/image-editor'
IMG_EDITOR_READ_DEFAULT = 'imageurl'
IMG_EDITOR_API_KEY_DEFAULT = '324cd8fc0'
IMG_EDITOR_METHOD_DEFAULT = 'client'
IMG_EDITOR_PORT_DEFAULT = 8001

IMG_PARAMS_DEFAULT = {
  'service_name': 'sitename',
  'image_url': 'loadurl',
  'filename': 'defaultfilename',
  'method': 'postagent',
  'save_url': 'posturl',
  'api_key': 'apil'
}

IDE_TRACK_DEFAULT = True
IDE_TRACK_CODE_DEFAULT = """
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-4108685-13']);
  _gaq.push(['_setDomainName', 'neutronide.com']);
  _gaq.push(['_setAllowLinker', true]);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>
"""

TEXT_EXTENSIONS = getattr(settings, 'TEXT_EXTENSIONS', TEXT_EXTENSIONS_DEFAULT)
MODES = getattr(settings, 'MODES', MODES_DEFAULT)
THEMES = getattr(settings, 'THEMES', THEMES_DEFAULT)

SITE_NAME = getattr(settings, 'SITE_NAME', SITE_NAME_DEFAULT)

IDE_TRACK = getattr(settings, 'IDE_TRACK', IDE_TRACK_DEFAULT)
IDE_TRACK_CODE = getattr(settings, 'IDE_TRACK_CODE', IDE_TRACK_CODE_DEFAULT)

IMG_EXTENSIONS = getattr(settings, 'IMG_EXTENSIONS', IMG_EXTENSIONS_DEFAULT)
IMG_EDITOR_URL = getattr(settings, 'IMG_EDITOR_URL', IMG_EDITOR_URL_DEFAULT)
IMG_EDITOR_READ = getattr(settings, 'IMG_EDITOR_READ', IMG_EDITOR_READ_DEFAULT)
IMG_PARAMS = getattr(settings, 'IMG_PARAMS', IMG_PARAMS_DEFAULT)
IMG_EDITOR_API_KEY = getattr(settings, 'IMG_EDITOR_API_KEY', IMG_EDITOR_API_KEY_DEFAULT)
IMG_EDITOR_METHOD = getattr(settings, 'IMG_EDITOR_METHOD', IMG_EDITOR_METHOD_DEFAULT)
IMG_EDITOR_PORT = getattr(settings, 'IMG_EDITOR_PORT', IMG_EDITOR_PORT_DEFAULT)

SKIP_CELERY_CHECK = getattr(settings, 'SKIP_CELERY_CHECK', False)
CELERY_ON = getattr(settings, 'CELERY_ON', False)

