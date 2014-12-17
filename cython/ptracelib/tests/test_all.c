/* Code sample: Use debuglib for setting breakpoints in a child process.
**
** Eli Bendersky (http://eli.thegreenplace.net)
** This code is in the public domain.
*/
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <syscall.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/reg.h>
#include <sys/user.h>
#include <unistd.h>
#include <errno.h>
#include <assert.h>

#include "debuglib.h"


void test2_debugger(pid_t child_pid)
{
    procmsg("debugger started\n");

    /* Wait for child to stop on its first instruction */
    wait(0);
    procmsg("child now at EIP = 0x%08x\n", get_child_eip(child_pid));

    debug_breakpoint* bp = create_breakpoint(child_pid, (void*)0x8048080);
    procmsg("breakpoint created\n");
    ptrace(PTRACE_CONT, child_pid, 0, 0);
    wait(0);

    /* Loop as long as the child didn't exit */
    procmsg("child stopped at breakpoint. EIP = 0x%08X\n", get_child_eip(child_pid));

    int addresses[] = {
        0x08048085,
        0x0804808A,
        0x0804808F,
        0x08048094,
        0x08048096,
        0x0804809B,
        0x080480A0,
        0x080480A5,
        0x080480AA,
        0x080480AC,
        0x080480B1};

    int i = 0;
    int rc = step_one(child_pid, bp);
    while (rc == 1) {
        assert(addresses[i] == get_child_eip(child_pid));
        i += 1;
        procmsg("child stopped at breakpoint. EIP = 0x%08X\n", get_child_eip(child_pid));
        rc = step_one(child_pid, bp);
    }

    cleanup_breakpoint(bp);
}

void test1_debugger(pid_t child_pid)
{
    procmsg("debugger started\n");

    /* Wait for child to stop on its first instruction */
    wait(0);
    procmsg("child now at EIP = 0x%08x\n", get_child_eip(child_pid));

    debug_breakpoint* bp = create_breakpoint(child_pid, (void*)0x8048414);
    procmsg("breakpoint created\n");
    ptrace(PTRACE_CONT, child_pid, 0, 0);
    wait(0);

    /* Loop as long as the child didn't exit */
    int stop_count = 0;
    while (1) {
        /* The child is stopped at a breakpoint here. Resume its
        ** execution until it either exits or hits the
        ** breakpoint again.
        */
        procmsg("child stopped at breakpoint. EIP = 0x%08X\n", get_child_eip(child_pid));
        procmsg("resuming\n");
        int rc = resume_from_breakpoint(child_pid, bp);
        stop_count += 1;

        if (rc == 0) {
            procmsg("child exited\n");
            break;
        }
        else if (rc == 1) {
            continue;
        }
        else {
            procmsg("unexpected: %d\n", rc);
            assert(0);
            break;
        }
    }
    assert(stop_count == 4);

    cleanup_breakpoint(bp);
}


int test1()
{
    pid_t child_pid;
    child_pid = fork();
    if (child_pid == 0)
        run_target("traced_c_loop");
    else if (child_pid > 0)
        test1_debugger(child_pid);
    else {
        perror("fork");
        return -1;
    }

    printf("TEST1 PASS\n");

    return 0;
}

int test2()
{
    pid_t child_pid;
    child_pid = fork();
    if (child_pid == 0)
        run_target("hello");
    else if (child_pid > 0)
        test2_debugger(child_pid);
    else {
        perror("fork");
        return -1;
    }

    printf("TEST1 PASS\n");

    return 0;
}

int main()
{
    test1();
    test2();
    printf("ALL TESTS PASS\n");
    return 0;
}
