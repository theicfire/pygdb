from optparse import OptionParser
import inspect
import cyout.use_dwarf
import os
from cyout.use_debuglib import *

class NotRunningException(Exception):
    pass

class NotLoadedException(Exception):
    pass

class Pygdb:
    WAIT_EXITED = 0
    WAIT_STOPPED = 1
    def __init__(self):
        self.breakpoints = []
        self.loaded = False
        self.running = False

    def get_methods(self):
        return [('b', self.add_breakpoint),
                ('gb', self.get_breakpoints),
                ('f', self.get_functions),
                ('load', self.load_program),
                ('run', self.run),
                ('c', self.cont),
                ('regs', self.get_regs)]
    def step(self):
        if not self.running:
            raise NotRunningException("Already running")
        s = pystep(self.child_pid)
        self.set_wait_status(s)
        return s

    def add_breakpoint(self, loc):
        if not self.loaded:
            raise NotLoadedException("Load the program before adding breakpoints")
        print 'Adding breakpoint at ', loc
        if type(loc) == str:
            loc = int(loc, 16)
        self.breakpoints.append(loc)
        pycreate_breakpoint(self.child_pid, loc)

    def get_breakpoints(self):
        print 'breakpoints', self.breakpoints
        return self.breakpoints

    def get_regs(self):
        print 'eip:', hex(pyget_child_eip(self.child_pid))

    def mem_peek(self, addr):
        print 'mem_peek', addr

    def mem_poke(self, addr, val):
        print 'mem_poke at {} with {}'.format(addr, val)

    def get_functions(self):
        fns = cyout.use_dwarf.get_functions(self.progname)
        for f in fns:
            print '{}: {}'.format(f['name'], hex(f['low_pc']))
        return fns

    def wait(self):
        if not self.loaded:
            raise NotLoadedException("Load the program before adding breakpoints")
        s = pywait()
        self.set_wait_status(s)
        return s

    def cleanup_breakpoint(self):
        pycleanup_breakpoint()
    # TODO there should be one continue, not a start and continue

    def load_program(self, progname):
        print 'loading'
        self.progname = progname
        self.child_pid = os.fork()
        if self.child_pid == 0:
            pyrun_target(progname)
        elif self.child_pid < 0:
            raise Exception("Error: Fork")
        self.loaded = True
        return self.wait()

    def run(self):
        if self.running:
            raise NotRunningException("Already running")
        pycontinue(self.child_pid)
        ret = self.wait()
        self.running = True
        return ret

    def current_eip(self):
        return pyget_child_eip(self.child_pid)

    def cont(self):
        if not self.running:
            raise NotRunningException("Nothing running")
        s = pyresume_from_breakpoint(self.child_pid)
        self.set_wait_status(s)
        return s

    def set_wait_status(self, s):
        if s == Pygdb.WAIT_EXITED:
            print 'Child exited'
            self.loaded = False
            self.running = False
        elif s != 1:
            raise Exception('Unexpected status {}'.format(s))

    def help(self):
        print "Possible queries:"
        print [x[0] for x in self.get_methods()]


def take_input(pygdb, inp):
    parts = inp.split(' ')
    try:
        tup = next(x for x in pygdb.get_methods() if x[0] == parts[0])
        method = tup[1]
        method(*(parts[1:]))
        return True
    except StopIteration:
        print 'No such method!'
        pygdb.help()
    except TypeError as e:
        print 'TypeError:', e
        pygdb.help()
    except NotRunningException as e:
        print 'NotRunningException:', e
    except NotLoadedException as e:
        print 'NotLoadedException', e
    return False

if __name__ == "__main__":
    pass

