import use_dwarf
funcs = use_dwarf.get_functions(1000 * 2)
for f in funcs:
    print "{} starts at {}".format(f['name'], hex(f['low_pc']))
