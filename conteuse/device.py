"""Capability gate for the current ESP32 bench player; no implicit transcoding."""
from pathlib import Path
import struct
from .packages import canonical, check_pack


def check_device_pack(source):
    pack = check_pack(source)
    if len(canonical(pack)) > 16384 or len(pack['nodes']) > 128 or len(pack.get('assets', [])) > 64:
        raise ValueError('pack exceeds current firmware capability limits')
    sizes = {a['path']: a['size'] for a in pack.get('assets', [])}
    for node in pack['nodes']:
        if len(node.get('choices', [])) > 16:
            raise ValueError('current firmware supports at most 16 choices per node')
        if 'audio' not in node:
            continue
        with (Path(source) / node['audio']).open('rb') as stream:
            header = stream.read(44)
        if len(header) != 44:
            raise ValueError('device requires canonical PCM WAV; transcode and reapprove')
        riff, riff_size, wave, fmt, fmt_size, encoding, channels, rate, byte_rate, alignment, bits, data, size = struct.unpack('<4sI4s4sIHHIIHH4sI', header)
        if (riff != b'RIFF' or wave != b'WAVE' or fmt != b'fmt ' or data != b'data'
                or fmt_size != 16 or encoding != 1 or channels not in (1, 2) or bits != 16
                or rate not in (16000, 22050, 44100) or alignment != channels * 2
                or byte_rate != rate * channels * 2 or not size or size % alignment
                or riff_size != size + 36 or sizes[node['audio']] != size + 44):
            raise ValueError('device requires canonical PCM WAV; transcode and reapprove')
    return pack
