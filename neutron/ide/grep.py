import re

class Grep (object):
  def __init__ (self, filepath, needle):
    self.filepath = filepath
    self.needle = needle
    
  def replace (self, rstr, rlines):
    fh = open(self.filepath, 'r')
    newlines = ''
    
    linenum = 0
    while 1:
      line = fh.readline()
      if line:
        if (linenum in rlines):
          newlines += self.needle.sub(rstr, line)
          
        else:
          newlines += line
          
        linenum += 1
        
      else:
        break
        
    fh.close()
    fh = open(self.filepath, 'w')
    fh.write(newlines)
    fh.close()
    
  def results (self):
    ret = []
    fh = open(self.filepath, 'r')
    
    linenum = 0
    while 1:
      line = fh.readline()
      if line:
        for match in self.needle.finditer(line):
          ret.append((linenum, match.start(), match.end()))
          
        linenum += 1
        
      else:
        break
        
    fh.close()
    
    return ret
    