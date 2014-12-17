from libc.string cimport memset
cdef extern from "dwarf_get_func_addr.h":
    cdef struct func_info:
        int low_pc "low_pc"
        char* name "name"
    int get_funcs_in_file(const char* progname, func_info *finfos)
    int MAX_FNS


def get_functions(name):
    # TODO fix this 10 constant. Actually, come up with a way to malloc inside of c and return
    # that list of addresses to free here.
    cdef func_info finfos[10]
    memset(finfos, 0, sizeof(func_info) * MAX_FNS)
    cdef int num_funcs = get_funcs_in_file(name, finfos)
    if num_funcs < 0:
        return num_funcs

    return [finfos[i] for i in range(num_funcs)]

