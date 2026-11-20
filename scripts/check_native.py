"""Run native checks and bind their reports to exact source inputs."""
import hashlib
import json
from pathlib import Path
import subprocess
from project import ROOT, HARDWARE, BOARDS


def source_paths():
    suffixes = {'.kicad_pcb', '.kicad_sch', '.kicad_pro', '.kicad_mod', '.kicad_sym'}
    return sorted([p for p in HARDWARE.rglob('*') if p.is_file() and
        (p.suffix in suffixes or p.name in {'fp-lib-table', 'sym-lib-table', 'components.json'})] +
        [ROOT / p for p in ('scripts/check_native.py', 'scripts/check_board_contracts.py',
         'firmware/include/board_pins.h', 'firmware/include/controls.h',
         'firmware/src/compact_bringup.cpp', 'firmware/platformio.ini')])


def hashes(paths):
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    frozen = hashes(source_paths())
    outputs = []
    for board in BOARDS:
        directory = HARDWARE / board
        (directory / 'checks').mkdir(exist_ok=True)
        for kind, mode, filename, extras in [('erc', 'sch', '.kicad_sch', []), ('drc', 'pcb', '.kicad_pcb', ['--schematic-parity'])]:
            output = directory / 'checks' / (kind + '.rpt')
            subprocess.run(['kicad-cli', mode, kind, str(directory / (board + filename)),
                *extras, '--exit-code-violations', '--severity-all', '-o', str(output)], check=True)
            outputs.append(output)
    subprocess.run(['/usr/bin/python3', str(ROOT / 'scripts/check_board_contracts.py')], check=True)
    assert frozen == hashes(source_paths()), 'Native inputs changed during checks'
    version = subprocess.check_output(['kicad-cli', '--version'], text=True).strip()
    receipt = {'sources': frozen, 'reports': hashes(outputs), 'tool_version': version,
        'checks': ['all-severity ERC', 'all-severity DRC', 'schematic parity', 'native pad nets', 'firmware pin contract'],
        'physical_validation': 'pending'}
    (HARDWARE / 'check-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
