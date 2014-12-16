from optparse import OptionParser
import inspect
import cyout.use_dwarf

class Pygdb:
    def __init__(self, progname):
        self.breakpoints = []
        self.progname = progname
    def get_methods(self):
        # TODO give headers to methods like routes for easier names
        #return inspect.getmembers(self, predicate=inspect.ismethod)
        return [('b', self.add_breakpoint), ('l', self.get_breakpoints), ('f', self.get_functions)]
    def step(self):
        print 'step'
    def cont(self):
        print 'continue'
    def add_breakpoint(self, line):
        print 'Adding breakpoint at ', line
        line = int(line)
        self.breakpoints.append(line)
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
        return cyout.use_dwarf.get_functions(0)
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
    pygdb = Pygdb('tracedprog2')
    while True:
        take_input(pygdb, raw_input(">>> "))

