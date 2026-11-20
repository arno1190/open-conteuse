"""Check declared parts against native pad nets and active firmware pin names."""
import json
import re
import os
from project import ROOT, HARDWARE, BOARDS
os.environ.setdefault("XDG_CONFIG_HOME", str(ROOT / "work/config"))
import pcbnew

for name in BOARDS:
    parts = {p['ref']: p for p in json.loads((HARDWARE / name / 'components.json').read_text())['parts']}
    native = pcbnew.LoadBoard(str(HARDWARE / name / (name + '.kicad_pcb')))
    footprint_list = list(native.GetFootprints())
    footprints = {f.GetReference(): f for f in footprint_list}
    assert len(footprints)==len(footprint_list) and set(footprints)==set(parts),name
    for reference, part in parts.items():
        if re.fullmatch(r'R\d+', reference):
            assert all(net and not net.startswith('unconnected-') for net in part['pins'].values()), (name, reference, 'unused resistor terminal')
            if name == 'mini':
                assert set(part['pins'].values()) != {'3V2', 'IO8'}, (reference, 'parallel card pull-up')
        assert reference in footprints, (name, reference)
        pads = {}
        for pad in footprints[reference].Pads():
            if pad.GetNumber():
                pads.setdefault(pad.GetNumber(), []).append(pad.GetNetname().removeprefix('/'))
        assert set(pads)==set(map(str,part['pins'])),(name,reference,'pin set')
        for number, expected in part['pins'].items():
            for actual in pads[str(number)]:
                if expected is not None:
                    assert actual == expected, (name, reference, number, expected, actual)
                else:
                    assert not actual or actual.startswith('unconnected-'), (name, reference, number, actual)

header = (ROOT / 'firmware/include/board_pins.h').read_text()
reader = json.loads((HARDWARE / 'card-reader/components.json').read_text())
pullup = next(part for part in reader['parts'] if part['ref'] == 'R1')
assert pullup['mpn'] == 'RC0603FR-074K3L' and pullup['pins'] == {'1': '3V2', '2': 'IO8'}, 'single 4.3k card pull-up'
bus_pullups = []
for name in ('mini', 'card-reader'):
    for part in json.loads((HARDWARE / name / 'components.json').read_text())['parts']:
        nets = set(part['pins'].values())
        if re.fullmatch(r'R\d+', part['ref']) and '3V2' in nets and nets & {'IO8', 'CARD_DQ'}:
            bus_pullups.append((name, part['ref']))
assert bus_pullups == [('card-reader', 'R1')], ('card bus pull-ups', bus_pullups)
values = {name: int(value, 0) for name, value in re.findall(r'\b(\w+)\s*=\s*(0x[0-9a-f]+|\d+)\b', header)}
controls=(ROOT/'firmware/include/controls.h').read_text()
for key in ('Up','A','Down','Left','Right','B','Minus','Plus'):
    assert key+'=board::'+key in controls,('control key alias',key)
# ESP32-S3-WROOM-1 module pin numbers from the module datasheet, not GPIO numbers.
gpio_pads = {1:'39', 2:'38', 4:'4', 5:'5', 6:'6', 8:'12', 9:'17',
             10:'18', 11:'19', 12:'20', 13:'21', 14:'22', 21:'23', 38:'31', 47:'24', 48:'25'}
common = {'I2cSda':'I2C_SDA', 'I2cScl':'I2C_SCL', 'CodecReset':'IO4',
          'LatchClear':'IO5', 'LatchState':'IO6', 'SdCs':'SD_CS',
          'SpiMosi':'SPI_MOSI', 'SpiClock':'SPI_SCK', 'SpiMiso':'SPI_MISO',
          'SpeakerRequest':'SPK_REQUEST', 'StatusLed':'LED_STATUS', 'CodecIrq':'CODEC_IRQ'}
key_pads = {'Up':'4', 'A':'5', 'Down':'6', 'Left':'7', 'Right':'9', 'B':'10', 'Minus':'11', 'Plus':'12'}
key_nets = {'Up':'KEY_UP', 'A':'KEY_A', 'Down':'KEY_DOWN', 'Left':'KEY_LEFT', 'Right':'KEY_RIGHT', 'B':'KEY_B', 'Minus':'KEY_VOL_DOWN', 'Plus':'KEY_VOL_UP'}
for name in ('mini', 'explore'):
    parts = {p['ref']: p for p in json.loads((HARDWARE / name / 'components.json').read_text())['parts']}
    expected = dict(common)
    expected.update({'Card':'IO8'} if name == 'mini' else {'LcdCs':'LCD_CS', 'LcdDc':'LCD_DC', 'LcdReset':'IO9', 'Backlight':'IO8'})
    for key, net in expected.items():
        assert parts['U1']['pins'][gpio_pads[values[key]]] == net, (name, key, net)
    for bit, key in enumerate(key_pads):
        assert values[key] == 1 << bit and parts['U9']['pins'][key_pads[key]] == key_nets[key], (name, key)
    assert values['IoAddress'] == 0x20 and all(parts['U9']['pins'][p] == 'GND' for p in ('1','2','3'))
    assert values['CodecAddress'] == 0x18
print('Four native pad-net contracts, firmware GPIO/address/key mapping verified.')
