"""Parent-initiated transfer to the player's private WPA2 setup AP.

Only the fixed device AP address is contacted; no arbitrary URL/proxy or cloud.
Credentials are session inputs, never persisted in studio state.
"""
import base64
import http.client
import time
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from .device import check_device_pack
from .packages import canonical, revision

CHUNK_BYTES = 4096


def card_uid(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9A-Fa-f]{16}', value):
        raise ValueError('card ID must contain 16 hexadecimal characters')
    value = value.upper()
    rom = bytes.fromhex(value)
    crc = 0
    for byte in rom[:7]:
        for _ in range(8):
            mix = (crc ^ byte) & 1
            crc >>= 1
            if mix: crc ^= 0x8c
            byte >>= 1
    if rom[0] != 1 or crc != rom[7]:
        raise ValueError('card ID family/CRC is invalid')
    return value


class Player:
    address = '192.168.4.1'

    def __init__(self, token):
        if not isinstance(token, str) or not re.fullmatch(r'[0-9a-f]{64}', token):
            raise ValueError('enter the 64-character setup token shown over USB')
        self.token = token

    def request(self, method, path, value=None):
        body = canonical(value) if value is not None else None
        connection = http.client.HTTPConnection(self.address, 80, timeout=15)
        try:
            connection.request(method, path, body, {
                'Authorization': 'Bearer ' + self.token,
                'Content-Type': 'application/json',
            })
            response = connection.getresponse()
            data = response.read(65537)
            if len(data) > 65536:
                raise ValueError('oversized player reply')
            if response.status != 200:
                raise ValueError('player rejected operation (HTTP ' + str(response.status) + ')')
            result = json.loads(data)
            if not isinstance(result, dict): raise ValueError('invalid player reply')
            return result
        except (OSError, http.client.HTTPException, json.JSONDecodeError) as error:
            raise ValueError('player connection failed; reconnect to its setup Wi-Fi and retry') from error
        finally:
            connection.close()

    def wait_job(self, result):
        deadline = time.monotonic() + 7200
        while result.get('state') == 'pending':
            if time.monotonic() >= deadline:
                raise ValueError('verification not confirmed; read player status before retrying')
            time.sleep(0.1)
            result = self.request('GET', '/api/job')
        if result.get('state') != 'done':
            raise ValueError('player verification not confirmed; read player status before retrying')
        return result

    def status(self):
        return self.request('GET', '/api/status')

    def send_card(self, source, uid, approved_revisions):
        uid = card_uid(uid)
        pack = check_device_pack(source)
        paths = [a['path'].lower() for a in pack.get('assets', [])]
        for path in paths:
            if (len(path)>120 or path.count('/')>=8 or path=='manifest.json' or path.startswith('manifest.json/')
                    or not re.fullmatch(r'[a-z0-9._/-]+',path)
                    or any(other!=path and other.startswith(path+'/') for other in paths)
                    or paths.count(path)!=1):
                raise ValueError('Wi-Fi requires distinct FAT-compatible ASCII asset paths')
        digest = revision(pack)
        if digest not in approved_revisions:
            raise ValueError('approve this exact final revision before Wi-Fi transfer')
        response = self.request('POST', '/api/begin', {'revision': digest, 'manifest': canonical(pack).decode()})
        if response.get('existing') is not True:
            for asset in pack.get('assets', []):
                offset = 0
                with (Path(source) / asset['path']).open('rb') as stream:
                    while chunk := stream.read(CHUNK_BYTES):
                        path = '/api/chunk?' + urlencode({'path': asset['path'], 'offset': offset})
                        ack = self.request('POST', path, {'data': base64.b64encode(chunk).decode('ascii')})
                        offset += len(chunk)
                        if ack.get('next') != offset:
                            raise ValueError('invalid upload acknowledgement; previous assignment is preserved')
            self.wait_job(self.request('POST', '/api/commit', {'revision': digest}))
        result = self.wait_job(self.request('POST', '/api/assign', {'uid': uid, 'revision': digest}))
        if result.get('uid') != uid or result.get('revision') != digest:
            raise ValueError('assignment was not confirmed; read player status before retrying')
        return result
