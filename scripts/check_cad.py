#!/usr/bin/env python3
"""Source-to-source dimensional assertions; does not prove mechanical fit."""
import json
from pathlib import Path
import re
root = Path(__file__).resolve().parents[1]
data = json.loads((root/'enclosure/controls.json').read_text())
source = (root/'enclosure/shell.scad').read_text()
for key, field in [('controls','actuators_mm'),('holes','holes_mm')]:
    value = re.search(r'^'+key+r' = (\[.*\]);',source,re.M).group(1)
    assert json.loads(value) == data[field], f'{key} differs from PCB'
assert data['pcb_mm'] == [70,65,1.6]
# Nominal inner shell and board extents; does not include tolerance stack.
assert 15 > 2.4 and 15+70 < 100-2.4
assert 98 > 2.4 and 98+65 < 174-2.4
assert 2.4+6.5+1.6 < 19
print('CAD source dimensions agree; physical fit remains pending')
