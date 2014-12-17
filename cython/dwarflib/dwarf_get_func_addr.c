/* Code sample: Using libdwarf for getting the address of a function
** from DWARF in an ELF executable.
** Not much error-handling or resource-freeing is done here...
**
** Eli Bendersky (http://eli.thegreenplace.net)
** This code is in the public domain.
*/
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <dwarf.h>
#include <assert.h>
#include <libdwarf.h>

#include "dwarf_get_func_addr.h"

void die(char* fmt, ...)
{
    va_list args;
    
    va_start(args, fmt);
    vfprintf(stderr, fmt, args);
    va_end(args);
    
    exit(EXIT_FAILURE);
}


/* List a function if it's in the given DIE.
*/
int list_func_in_die(Dwarf_Debug dgb, Dwarf_Die the_die, struct func_info *finfo)
{
    if (dgb) {}// dgb is unused. Make the compiler happy.
    char* die_name = 0;
    const char* tag_name = 0;
    Dwarf_Error err;
    Dwarf_Half tag;
    Dwarf_Attribute* attrs;
    Dwarf_Addr lowpc, highpc;
    Dwarf_Signed attrcount, i;
    int rc = dwarf_diename(the_die, &die_name, &err);

    if (rc == DW_DLV_ERROR)
        die("Error in dwarf_diename\n");
    else if (rc == DW_DLV_NO_ENTRY)
        return -1;

    if (dwarf_tag(the_die, &tag, &err) != DW_DLV_OK)
        die("Error in dwarf_tag\n");

    /* Only interested in subprogram DIEs here */
    if (tag != DW_TAG_subprogram)
        return -1;

    if (dwarf_get_TAG_name(tag, &tag_name) != DW_DLV_OK)
        die("Error in dwarf_get_TAG_name\n");

    /* Grab the DIEs attributes for display */
    if (dwarf_attrlist(the_die, &attrs, &attrcount, &err) != DW_DLV_OK)
        die("Error in dwarf_attlist\n");

    for (i = 0; i < attrcount; ++i) {
        Dwarf_Half attrcode;
        if (dwarf_whatattr(attrs[i], &attrcode, &err) != DW_DLV_OK)
            die("Error in dwarf_whatattr\n");

        /* We only take some of the attributes for display here.
        ** More can be picked with appropriate tag constants.
        */
        if (attrcode == DW_AT_low_pc)
            dwarf_formaddr(attrs[i], &lowpc, 0);
        else if (attrcode == DW_AT_high_pc)
            dwarf_formaddr(attrs[i], &highpc, 0);
    }

    assert(strlen(die_name) + 1 <= MAX_FNAME_LEN);
    memcpy(finfo->name, die_name, strlen(die_name) + 1);
    finfo->low_pc = lowpc;
    free(attrs);
    return 0;
}


/* List all the functions from the file represented by the given descriptor.
*/
int list_funcs_in_file(Dwarf_Debug dbg, struct func_info *finfos)
{
    Dwarf_Unsigned cu_header_length, abbrev_offset, next_cu_header;
    Dwarf_Half version_stamp, address_size;
    Dwarf_Error err;
    Dwarf_Die no_die = 0, cu_die, child_die;

    /* Find compilation unit header */
    if (dwarf_next_cu_header(
                dbg,
                &cu_header_length,
                &version_stamp,
                &abbrev_offset,
                &address_size,
                &next_cu_header,
                &err) == DW_DLV_ERROR)
        die("Error reading DWARF cu header\n");

    /* Expect the CU to have a single sibling - a DIE */
    if (dwarf_siblingof(dbg, no_die, &cu_die, &err) == DW_DLV_ERROR)
        die("Error getting sibling of CU\n");

    /* Expect the CU DIE to have children */
    if (dwarf_child(cu_die, &child_die, &err) == DW_DLV_ERROR)
        die("Error getting child of CU DIE\n");

    /* Now go over all children DIEs */
    int i = 0;

    while (1) {
        int rc;
        if (list_func_in_die(dbg, child_die, &finfos[i]) == 0) {
            // TODO free findinfo->name and findinfo
            i += 1;
        }


        rc = dwarf_siblingof(dbg, child_die, &child_die, &err);

        if (rc == DW_DLV_ERROR)
            die("Error getting sibling of DIE\n");
        else if (rc == DW_DLV_NO_ENTRY)
            break; /* done */
    }
    return i;
}

int get_funcs_in_file(const char* progname, struct func_info *finfos)
{
    Dwarf_Debug dbg = 0;
    Dwarf_Error err;
    int fd = -1;
    if ((fd = open(progname, O_RDONLY)) < 0) {
        perror("open");
        return -1;
    }
    
    if (dwarf_init(fd, DW_DLC_READ, 0, 0, &dbg, &err) != DW_DLV_OK) {
        fprintf(stderr, "Failed DWARF initialization\n");
        return -1;
    }

    int num_funcs = list_funcs_in_file(dbg, finfos);

    if (dwarf_finish(dbg, &err) != DW_DLV_OK) {
        fprintf(stderr, "Failed DWARF finalization\n");
        return -1;
    }

    close(fd);
    return num_funcs;
}

int main(int argc, char** argv)
{
    const char* progname;

    if (argc < 2) {
        fprintf(stderr, "Expected a program name as argument\n");
        return 1;
    }

    progname = argv[1];

    struct func_info finfos[MAX_FNS]; // TODO make dynamic?
    memset(finfos, 0, sizeof(struct func_info) * MAX_FNS);
    int num_funcs = get_funcs_in_file(progname, finfos);
    if (num_funcs < 0) {
        return num_funcs;
    }

    printf("All the funcs:\n");
    for (int i = 0; i < num_funcs; i++) {
        printf("got back name %s\n", finfos[i].name);
        printf("got back low pc : 0x%08llx\n", finfos[i].low_pc);
    }
}

