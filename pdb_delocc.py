#!/usr/bin/env python

"""
Removes double occupancies (leaves the first location found) from a PDB file.

usage: python pdb_delocc.py <pdb file>
example: python pdb_delocc.py 1CTF.pdb

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

import os
import re
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        # Read from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # File
        if not os.path.isfile(args[0]):
            sys.stderr.write('File not found: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        pdbfh = open(args[0], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return pdbfh

def _remove_double_occupancies(fhandle):
    """Enclosing logic in a function to speed up a bit"""

    coord_re = re.compile('^(ATOM|HETATM)')
    read_atoms = set()
    for line in fhandle:
        line = line.strip()
        if coord_re.match(line):
            aname = line[12:16]
            resn = line[17:20]
            resi = line[22:26]
            chain = line[21]
            atom_uid = (aname, resn, resi, chain)

            if atom_uid not in read_atoms:
                read_atoms.add(atom_uid)
                yield line[:16] + ' ' + line[17:]  + '\n' # Blank altloc field
            else:
                continue
        else:
            yield line + '\n'

if __name__ == '__main__':

    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _remove_double_occupancies(pdbfh)

    try:
        sys.stdout.write(''.join(new_pdb))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
