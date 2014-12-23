# Minimal C Debugger in Python

The goal of this project is to make a c debugger, similar to gdb, in python. This is exclusively for educational purposes.

This debugger works by using the ptrace system call. A good chunk of the theory is [here](http://eli.thegreenplace.net/2011/01/23/how-debuggers-work-part-1/).



## Features
* Read function names from binaries
* Set breakpoints
* Read registers
* Continue to next breakpoint
* Read/Set Memory

## Setup
* Install [Vagrant](https://www.vagrantup.com/)
* `git clone https://github.com/theicfire/pygdb`
* `cd pygdb`
* `vagrant up` -- will take a bit of time
* `vagrant ssh`

Now run these commands in the VM:

* `cd /vagrant`
* `make test`

All the tests should pass!

## Example Usage
* `cd /vagrant`
* `make`
* `objdump -d hello`
* Find somewhere to break. In this case we'll pick the start of the program: `8048080`
* Start the debugger: `make interactive`
* Load the hello binary: `exec-file hello`
* Set a breakpoint: `b 0x8048080`
* Run the binary: `run`
* Get the registers. You'll notice eip is one after our breakpoint. `regs`
* Continue (Should finish): `c`

## Future Priorities
* Get this to run on 64 bit machines
* Add any number of features that GDB has
