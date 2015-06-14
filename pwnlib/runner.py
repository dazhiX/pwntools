import os
import tempfile

from .asm import asm, make_elf
from .context import LocalContext
from .tubes.process import process

__all__ = ['run_assembly', 'run_shellcode', 'run_assembly_exitcode', 'run_shellcode_exitcode']

@LocalContext
def run_assembly(assembly):
    """
    Given an assembly listing, assemble and execute it.

    Returns:

        A ``process`` tube to interact with the process.

    Example:

        >>> p = run_assembly('mov ebx, 3; mov eax, SYS_exit; int 0x80;')
        >>> p.wait_for_close()
        >>> p.poll()
        3

    """
    return run_shellcode(asm(assembly))

@LocalContext
def run_shellcode(bytes):
    """Given assembled machine code bytes, execute them.

    Example:

        >>> bytes = asm('mov ebx, 3; mov eax, SYS_exit; int 0x80;')
        >>> p = run_shellcode(bytes)
        >>> p.wait_for_close()
        >>> p.poll()
        3
    """
    e = make_elf(bytes)
    f = tempfile.mktemp()
    with open(f, 'wb+') as F:
        F.write(e)
        F.flush()
    os.chmod(f, 0755)
    return process(f)

@LocalContext
def run_assembly_exitcode(assembly):
    """
    Given an assembly listing, assemble and execute it, and wait for
    the process to die.

    Returns:

        The exit code of the process.

    Example:

        >>> p = run_assembly_exitcode('mov ebx, 3; mov eax, SYS_exit; int 0x80;')
        3
    """
    return run_shellcode_exitcode(asm(assembly))

@LocalContext
def run_shellcode_exitcode(bytes):
    """
    Given assembled machine code bytes, execute them, and wait for
    the process to die.

    Returns:

        The exit code of the process.

    Example:

        >>> bytes = asm('mov ebx, 3; mov eax, SYS_exit; int 0x80;')
        >>> p = run_shellcode_exitcode(bytes)
        3
    """
    p = run_shellcode(bytes)
    p.wait_for_close()
    return p.poll()

