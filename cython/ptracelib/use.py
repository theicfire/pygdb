from use_debuglib import *
import os
import time

#run_example()

def merun_debugger(child_pid):
    print 'Starting debugger with child: ', child_pid

# Wait for child to stop on its first instruction
    pywait()
    print 'child now at EIP =', hex(pyget_child_eip(child_pid))

## Create breakpoint and run to it
    loc = 0x8048414
    pycreate_breakpoint(child_pid, loc)
    pycontinue(child_pid)
    pywait()

    rc = 0
    while True:
        #/* The child is stopped at a breakpoint here. Resume its
        #** execution until it either exits or hits the
        #** breakpoint again.
        #*/
        print 'child stopped at', hex(pyget_child_eip(child_pid))
        rc = pyresume_from_breakpoint(child_pid)

        if rc == 0:
            print 'Child exited'
            break
        elif rc == 1:
            continue
        else:
            print 'unexpected rc: ', rc
            break

    pycleanup_breakpoint()


child_pid = os.fork()
print 'CHILD IS', child_pid
if child_pid == 0:
    pyrun_target('traced_c_loop')
elif child_pid > 0:
    merun_debugger(child_pid)
else:
    raise Exception("Error: Fork")
