from optparse import OptionParser
import inspect
import cyout.use_dwarf
import os
from cyout.use_debuglib import *

class NotRunningException(Exception):
    pass
class Pygdb:
    WAIT_EXITED = 0
    WAIT_STOPPED = 1
    def __init__(self):
        self.breakpoints = []
        self.loaded = False

    def get_methods(self):
        # TODO give headers to methods like routes for easier names
        #return inspect.getmembers(self, predicate=inspect.ismethod)
        return [('b', self.add_breakpoint),
                ('gb', self.get_breakpoints),
                ('f', self.get_functions),
                ('load', self.load_program),
                ('r', self.run),
                ('c', self.cont)]
    def step(self):
        print 'step'
    def add_breakpoint(self, loc):
        if not self.loaded:
            raise NotRunningException("Load the program before adding breakpoints")
        print 'Adding breakpoint at ', loc
        loc = int(loc)
        self.breakpoints.append(loc)
        pycreate_breakpoint(self.child_pid, loc)
    def get_breakpoints(self):
        print 'breakpoints', self.breakpoints
        return self.breakpoints
    def get_regs(self):
        print 'get_regs'
    def mem_peek(self, addr):
        print 'mem_peek', addr
    def mem_poke(self, addr, val):
        print 'mem_poke at {} with {}'.format(addr, val)
    def get_functions(self):
        fns = cyout.use_dwarf.get_functions(0)
        for f in fns:
            print '{}: {}'.format(f['name'], hex(f['low_pc']))
        return fns
    def wait(self):
        ret = pywait()
        if ret == 0:
            self.loaded = False
        return ret
    def cleanup_breakpoint(self):
        pycleanup_breakpoint()
    # TODO there should be one continue, not a start and continue
    def load_program(self, progname):
        self.progname = progname
        self.child_pid = os.fork()
        if self.child_pid == 0:
            pyrun_target(progname)
        elif self.child_pid < 0:
            raise Exception("Error: Fork")
        self.loaded = True
        return self.wait()
    def run(self):
        pycontinue(self.child_pid)
        return self.wait()
    def current_eip(self):
        return pyget_child_eip(self.child_pid)
    def cont(self):
        if not self.loaded:
            raise NotRunningException("Nothing running")
        rc = pyresume_from_breakpoint(self.child_pid)

        if rc == Pygdb.WAIT_EXITED:
            print 'Child exited'
            self.loaded = False
        elif rc != 1:
            raise Exception('Unexpected rc {}'.format(rc))

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
    return False

if __name__ == "__main__":
    pygdb = Pygdb()
    while True:
        take_input(pygdb, raw_input(">>> "))

