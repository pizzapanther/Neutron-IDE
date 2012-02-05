import os
import sys
import subprocess
import pty
import fcntl
import struct
import termios
from base64 import b64decode, b64encode

import pyte

TERM_W = 80
TERM_H = 24

class Terminal:
    def __init__(self):
        self._proc = None

    def start(self, app, home, width, height, onclose=None):
        env = {}
        env.update(os.environ)
        env['TERM'] = 'linux'
        env['COLUMNS'] = str(width)
        env['LINES'] = str(height)
        env['LC_ALL'] = 'en_US.UTF8'
        sh = app 
        
        pid, master = pty.fork()
        self.pid = pid
        if pid == 0:
            os.chdir(home)
            p = subprocess.Popen(
                sh,
                shell=True,
                close_fds=True,
                env=env,
            )
            p.wait()
            
            if onclose:
              onclose()
              
            sys.exit(0)
            
        self._proc = PTYProtocol(pid, master, width, height)

    def restart(self):
        if self._proc is not None:
            self._proc.kill()
        self.start()

    def dead(self):
        return self._proc is None 

    def write(self, data):
        self._proc.write(b64decode(data))

    def kill(self):
        self._proc.kill()
        
    def resize (self, lines, columns):
        self._proc.resize(lines, columns)
        
class PTYProtocol():
    def __init__(self, proc, stream, width, height):
        self.data = ''
        self.proc = proc
        self.master = stream

        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self.mstream = os.fdopen(self.master, 'r+')
        
        self.term = pyte.DiffScreen(width, height)
        self.stream = pyte.Stream()
        self.stream.attach(self.term)
        self.data = ''
        self.unblock()
        
    def resize (self, lines, columns):
      fd = self.master
      self.term.resize(lines, columns)
      s = struct.pack("HHHH", lines, columns, 0, 0)
      fcntl.ioctl(fd, termios.TIOCSWINSZ, s)
      self.term.reset()
      
    def unblock(self):
        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def block(self):
        fd = self.master
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl - os.O_NONBLOCK)

    def read(self):
        for i in range(0,45):
            try:
                d = self.mstream.read()
                self.data += d
                if len(self.data) > 0:
                    u = unicode(str(self.data))
                    self.stream.feed(u)
                    self.data = ''
                break
            except IOError, e:
                pass
            except UnicodeDecodeError, e:
                print 'UNICODE'
                
        return self.format()

    def history(self):
        return self.format(full=True)

    def format(self, full=False):
        l = {}
        self.term.dirty.add(self.term.cursor.y)
        for k in self.term.dirty:
            try:
              l[k] = self.term[k]
              
            except:
              pass
              
        self.term.dirty.clear()
        r = {
            'lines': self.term if full else l,
            'cx': self.term.cursor.x,
            'cy': self.term.cursor.y,
            'cursor': not self.term.cursor.hidden,
        }
        return r

    def write(self, data):
        self.block()
        self.mstream.write(data)
        self.mstream.flush()
        self.unblock()

    def kill(self):
        os.kill(self.proc, 9)
        
