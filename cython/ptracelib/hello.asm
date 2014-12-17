section    .text
    ; The _start symbol must be declared for the linker (ld)
    global _start

_start:

    ; Prepare arguments for the sys_write system call:
    ;   - eax: system call number (sys_write)
    ;   - ebx: file descriptor (stdout)
    ;   - ecx: pointer to string
    ;   - edx: string length
    mov     edx, len1
    mov     ecx, msg1
    mov     ebx, 1
    mov     eax, 4

    ; Execute the sys_write system call
    int     0x80

    ; Now print the other message
    mov     edx, len2
    mov     ecx, msg2
    mov     ebx, 1
    mov     eax, 4
    int     0x80

    ; Execute sys_exit
    mov     eax, 1
    int     0x80

section    .data

msg1    db      'Hello,', 0xa
len1    equ     $ - msg1
msg2    db      'world!', 0xa
len2    equ     $ - msg2
