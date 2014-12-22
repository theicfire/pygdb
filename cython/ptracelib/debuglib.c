/* Code sample: simplistic "library" of debugging tools.
**
** Eli Bendersky (http://eli.thegreenplace.net)
** This code is in the public domain.
*/
#include <stdio.h>
#include <assert.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/reg.h>
#include <sys/user.h>
#include <unistd.h>
#include <errno.h>

#include "debuglib.h"


/* Print a message to stdout, prefixed by the process ID
*/
void procmsg(const char* format, ...)
{
    va_list ap;
    fprintf(stdout, "[%d] ", getpid());
    va_start(ap, format);
    vfprintf(stdout, format, ap);
    va_end(ap);
}


/* Run a target process in tracing mode by exec()-ing the given program name.
*/
void run_target(const char* programname)
{
    procmsg("target started. will run '%s'\n", programname);

    /* Allow tracing of this process */
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) < 0) {
        perror("ptrace1");
        return;
    }

    /* Replace this process's image with the given program */
    execl(programname, programname, 0);
    perror("ERROR, could not open program");
}


long get_child_eip(pid_t pid)
{
    struct user_regs_struct regs;
    if (ptrace(PTRACE_GETREGS, pid, 0, &regs) < 0) {
        perror("ptrace2");
        return -1;
    }
#ifdef ENVIRONMENT32
    return regs.eip;
#else
    return regs.rip;
#endif
}


void dump_process_memory(pid_t pid, unsigned from_addr, unsigned to_addr)
{
    procmsg("Dump of %d's memory [0x%08X : 0x%08X]\n", pid, from_addr, to_addr);
    for (unsigned addr = from_addr; addr <= to_addr; ++addr) {
        unsigned word;
        if ((int) (word = ptrace(PTRACE_PEEKTEXT, pid, addr, 0)) == -1 && errno != 0) {
            perror("ptrace3");
            return;
        }
        // TODO error here.. don't know what to do about unsigned though
        printf("  0x%08X:  %02x\n", addr, word & 0xFF);
    }
}




/* Enable the given breakpoint by inserting the trap instruction at its 
** address, and saving the original data at that location.
*/
static void enable_breakpoint(pid_t pid, debug_breakpoint* bp)
{
    assert(bp);
    if ((int) (bp->orig_data = ptrace(PTRACE_PEEKTEXT, pid, bp->addr, 0)) == -1 && errno != 0) {
        perror("ptrace");
        return;
    }
    if (ptrace(PTRACE_POKETEXT, pid, bp->addr, (bp->orig_data & ~(0xFF)) | 0xCC) < 0) {
        perror("ptrace5");
        return;
    }
}


/* Disable the given breakpoint by replacing the byte it points to with
** the original byte that was there before trap insertion.
*/
static void disable_breakpoint(pid_t pid, debug_breakpoint* bp)
{
    assert(bp);
    unsigned data;
    if ((int) (data = ptrace(PTRACE_PEEKTEXT, pid, bp->addr, 0)) == -1 && errno != 0) {
        perror("ptrace");
        return;
    }
    assert((data & 0xFF) == 0xCC);
    if (ptrace(PTRACE_POKETEXT, pid, bp->addr, (data & ~(0xFF)) | (bp->orig_data & 0xFF)) < 0) {
        perror("ptrace7");
        return;
    }
}


debug_breakpoint* create_breakpoint(pid_t pid, void* addr)
{
    debug_breakpoint* bp = malloc(sizeof(*bp));
    bp->addr = addr;
    bp->was_continue = 1;
    enable_breakpoint(pid, bp);
    return bp;
}


void cleanup_breakpoint(debug_breakpoint* bp)
{
    free(bp);
}

int stopped_at_breakpoint(pid_t pid, debug_breakpoint* bp)
{
    struct user_regs_struct regs;

    if (ptrace(PTRACE_GETREGS, pid, 0, &regs) < 0) {
        perror("ptrace8");
        return -1;
    }
    /* Make sure we indeed are stopped at bp */
    /*printf("reg is %ld, bp is %ld\n", regs.eip, (unsigned long) bp->addr + 1);*/
#ifdef ENVIRONMENT32
    return (regs.eip == (long) bp->addr + 1) && bp->was_continue;
#else
    return (regs.rip == (unsigned long) bp->addr + 1) && bp->was_continue;
#endif
}

int step_one(pid_t pid, debug_breakpoint* bp)
{
    if (stopped_at_breakpoint(pid, bp)) {
        return step_over_breakpoint(pid, bp);
    }

    bp->was_continue = 0;
    if (ptrace(PTRACE_SINGLESTEP, pid, 0, 0)) {
        perror("ptrace10");
        return -1;
    }
    if (wait_common() == 0) {
        return 0;
    }
    return 1;
}

int step_over_breakpoint(pid_t pid, debug_breakpoint* bp)
{
    struct user_regs_struct regs;
    assert(stopped_at_breakpoint(pid, bp));

    if (ptrace(PTRACE_GETREGS, pid, 0, &regs) < 0) {
        perror("ptrace8");
        return -1;
    }

    /* Now disable the breakpoint, rewind EIP back to the original instruction
    ** and single-step the process. This executes the original instruction that
    ** was replaced by the breakpoint.
    */
#ifdef ENVIRONMENT32
    regs.eip = (long) bp->addr;
#else
    regs.rip = (long) bp->addr;
#endif
    if (ptrace(PTRACE_SETREGS, pid, 0, &regs) < 0) {
        perror("ptrace9");
        return -1;
    }
    disable_breakpoint(pid, bp);
    int ret;
    bp->was_continue = 0;
    if ((ret = step_one(pid, bp)) <= 0) {
        return ret;
    }

    /* Re-enable the breakpoint and let the process run.
    */
    enable_breakpoint(pid, bp);

    return ret;
}

int resume_from_breakpoint(pid_t pid, debug_breakpoint* bp)
{
    if (stopped_at_breakpoint(pid, bp)) {
        int ret = step_over_breakpoint(pid, bp);
        if (ret <= 0) {
            return ret;
        }
    }

    bp->was_continue = 1;
    if (ptrace(PTRACE_CONT, pid, 0, 0) < 0) {
        perror("ptrace11");
        return -1;
    }
    return wait_common();
}

int
wait_common(void)
{
    int wait_status;
    wait(&wait_status);

    if (WIFEXITED(wait_status)) {
        return 0;
    } else if (WIFSTOPPED(wait_status)) {
        return 1;
    }
    return -1;
}

