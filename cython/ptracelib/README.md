# Code for "How debuggers work: Part 2 - Breakpoints"

This is the code for http://eli.thegreenplace.net/2011/01/27/how-debuggers-work-part-2-breakpoints

The main additions I've added is that this compiles for both 32 and 64 bit. Additionally, there's a nice Makefile that should get you up and running faster.

###Prerequisites
1. You'll need `nasm` (Ubuntu: `sudo apt-get install nasm`).
2. You also need to make sure that the breakpoints are correct. This varies per computer. 

**Correct breakpoints for the first example:**

* `$ make`
* `$ objdump -d hello`
* Find two lines that look like
```
 8048094:       cd 80                   int    $0x80
 8048096:       ba 07 00 00 00          mov    $0x7,%edx
```
* In this case, we want to copy `8048096`, because we want to stop the debugger we've built after the `int $0x80` instruction.
* Change the address in `bp_manual.c` here (the first line if you're 32 bit, the second if 64 bit):
```c
#ifdef ENVIRONMENT32
    long addr = 0x8048096;
#else
    long addr = 0x4000c6;
#endif
```

**Correct breakpoints for the second example:**

* `$ make`
* `$ objdump -d hello`
* Find line that looks like
```
08048414 <do_stuff>:
```
* In this case, we want to copy `08048414`.
* Change the address in `bp_use_lib.c` here (the first line if you're 32 bit, the second if 64 bit):
```c
#ifdef ENVIRONMENT32
    debug_breakpoint* bp = create_breakpoint(child_pid, (void*)0x8048414);
#else
    debug_breakpoint* bp = create_breakpoint(child_pid, (void*)0x400544);
#endif
```

###Running

The first example in the post sets a breakpoint in hello.asm. To run (and compile) it:

```bash
$ make run_manual
```

The second example uses a nice library Eli built that wraps ptrace for debugging. To run (and compile) it:

```bash
$ make run_with_lib
```

Currently the second example **does not work on 64 bit machines**. An assertion error is thrown. I haven't spent the time debugging it. Pull requests on this issue are very welcome!
