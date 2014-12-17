# Code for "How debuggers work: Part 3 - Debugging information"

This is the code for http://eli.thegreenplace.net/2011/02/07/how-debuggers-work-part-3-debugging-information

The main additions I've added is that this compiles for both 32 and 64 bit. Additionally, there's a nice Makefile that should get you up and running faster.

###Prerequisites
1. You'll need libelf and libdwarf (Ubuntu `sudo apt-get install libelf-dev libdwarf-dev`)

###Running

To compile and run Eli's example program:
```bash
$ make run
```
