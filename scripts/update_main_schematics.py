#!/usr/bin/python3
"""Update current main-board schematics from audited component contracts."""
import json
from project import HARDWARE,VARIANTS
from schematic import make_schematic
for name in VARIANTS:
 path=HARDWARE/name;make_schematic(json.loads((path/'components.json').read_text()),path,name)
