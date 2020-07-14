#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *


cpu = CPU()

prog_name = sys.argv[1]
print(prog_name)

cpu.load(prog_name)
cpu.run()
