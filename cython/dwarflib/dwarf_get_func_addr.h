
#include <libdwarf.h>
#define MAX_FNS 10
#define MAX_FNAME_LEN 100
struct func_info {
    char name[MAX_FNAME_LEN];
    Dwarf_Addr low_pc;
};
int get_funcs_in_file(const char* progname, struct func_info *finfos);
