#!/usr/bin/env python

import re
import sys
import shutil

REPLACES = (
  (';', ';\n  '),
  (':', ': '),
  ('>', ' > '),
  ('{', ' {\n  '),
  ('}', ';\n}\n\n'),
  (',\.', ', .'),
)

def runme ():
  for fp in sys.argv[1:]:
    print fp
    shutil.copy2(fp, fp + '.old')
    
    fh = open(fp, 'r')
    data = fh.read()
    fh.close()
    
    for r in REPLACES:
      data = re.sub(r[0], r[1], data)
      
    fh = open(fp, 'w')
    fh.write(data)
    fh.close()
    
if __name__ == '__main__':
  runme()
  