"""Required mechanical release gates, distinct from physical qualification."""
from project import ROOT, ENCLOSURE, PARTS, VARIANTS

CAP_COUNTS = {'mini': 5, 'explore': 8}
EMPTY_GATES = ('shell_interference', 'interference', 'internal_interference',
    'cap_shell_interference', 'cap_pair_interference', 'headphone_plug_clearance',
    'usb_plug_clearance', 'strap_clearance')


def source_paths():
    return sorted(list(ENCLOSURE.glob('*.scad')) + [ROOT / p for p in (
        'scripts/export_enclosure.py', 'scripts/mesh.py', 'scripts/stl.py',
        'scripts/project.py', 'scripts/cad_contract.py',
        'enclosure/card-window.svg', 'hardware/mini/components.json', 'hardware/explore/components.json')])


def expectations():
    expected = {}
    for variant in VARIANTS:
        for name in PARTS:
            expected[f'enclosure/print/{variant}/{name}.stl'] = CAP_COUNTS[variant] if name == 'buttons' else 1
        for i in range(CAP_COUNTS[variant]):
            expected[f'enclosure/print/{variant}/cap_{i}.stl'] = 1
        expected[f'work/current/{variant}-plugs.stl'] = 2
        expected[f'work/current/{variant}-pcb.stl'] = 1
        for gate in EMPTY_GATES:
            expected[f'work/current/{variant}-{gate}.stl'] = 'empty'
    expected['work/current/mini-reader-pcb.stl'] = 1
    for name in ('front', 'back', 'print_front', 'pcb'):
        expected[f'enclosure/print/story-card/{name}.stl'] = 1
    expected['work/current/card_sweep_interference.stl'] = 'empty'
    expected['work/current/card-window-clearance.stl'] = 'empty'
    expected['work/current/card-shell-clearance.stl'] = 'empty'
    expected['work/current/wrong_card_interference.stl'] = 'positive'
    return expected


def verify_exports(exports):
    expected = expectations()
    assert set(exports) == set(expected), ('missing or unexpected CAD gates', set(expected) ^ set(exports))
    for filename, components in expected.items():
        actual = exports[filename]
        if components == 'empty':
            assert actual.get('empty') is True, filename
        else:
            assert not actual.get('empty'), filename
            if components == 'positive':
                assert actual['components'] >= 1, filename
            else:
                assert actual['components'] == components, filename
            assert actual['volume_cm3'] > 0, filename
