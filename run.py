from optparse import OptionParser
import inspect
import cyout.use_dwarf
import os
from cyout.use_debuglib import *
import sys
import argparse

class NotRunningException(Exception):
    pass

class NotLoadedException(Exception):
    pass

class Pygdb:
    WAIT_EXITED = 0
    WAIT_STOPPED = 1
    def __init__(self, progname=None):
        self.breakpoints = []
        self.loaded = False
        self.running = False
        if progname:
            self.load_program(progname)

    def get_methods(self):
        return [('b', self.add_breakpoint),
                ('gb', self.get_breakpoints),
                ('f', self.get_functions),
                ('exec-file', self.load_program),
                ('run', self.run),
                ('c', self.cont),
                ('regs', self.get_regs),
                ('s', self.step),
                ('q', self.quit),
                ('read', self.read_memory),
                ('example', self.example)]
    def step(self):
        if not self.running:
            raise NotRunningException("Already running")
        s = pystep(self.child_pid)
        self.set_wait_status(s)
        return s

    def example(self):
        self.load_program('hello')
        self.add_breakpoint(0x8048080)
        self.run()

    def add_breakpoint(self, loc):
        if not self.loaded:
            raise NotLoadedException("Load the program before adding breakpoints")
        if type(loc) == str:
            loc = int(loc, 16)
        print 'Adding breakpoint at ', hex(loc)
        self.breakpoints.append(loc)
        pycreate_breakpoint(self.child_pid, loc)

    def get_breakpoints(self):
        print 'breakpoints', self.breakpoints
        return self.breakpoints

    def quit(self):
        sys.exit(0)

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
        self.progname = progname
        self.child_pid = os.fork()
        if self.child_pid == 0:
            try:
                pyrun_target(progname)
            except Exception as e:
                print 'Could not run the program:', e
                sys.exit(0)
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

    def read_memory(self, addr, size):
        if type(addr) == str:
            addr = int(addr, 16)
        if type(size) == str:
            size = int(size)
        ret = pyread_memory(self.child_pid, addr, size)
        print '{}: {}'.format(hex(addr), map(hex, ret))
        return ret

    def set_memory(self, addr, mem):
        if type(addr) == str:
            addr = int(addr, 16)
        mem_str = ''.join(map(chr, mem))
        return pyset_memory(self.child_pid, addr, mem_str)

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
    parser = argparse.ArgumentParser(description="calculate X to the power of Y")
    parser.add_argument("program", type=str, help="The file to debug", nargs='?')
    args = parser.parse_args()

    pygdb = Pygdb(args.program)
    while True:
        take_input(pygdb, raw_input(">>> "))

