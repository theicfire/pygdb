import deps.use_dwarf
funcs = deps.use_dwarf.primes(1000 * 2)
for f in funcs:
    print "{} starts at {}".format(f['name'], hex(f['low_pc']))
