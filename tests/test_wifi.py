"""Exercise the real HTTP client against a fault-injecting protocol peer."""
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import wave
from conteuse.imports import import_playlist
from conteuse.packages import canonical, revision
from conteuse.studio import Studio
from conteuse.wifi import Player, card_uid

TOKEN = 'a' * 64
ROM = bytearray([1,2,3,4,5,6,7,0])
crc=0
for byte in ROM[:7]:
    for _ in range(8):
        mix=(crc^byte)&1;crc>>=1
        if mix: crc^=0x8c
        byte>>=1
ROM[-1]=crc
UID=ROM.hex().upper()
REAL_CONNECTION=http.client.HTTPConnection


class Peer:
    def __init__(self):
        self.packs={};self.mapping={UID:'old'};self.stage=None;self.fail_chunk=False;self.corrupt=False
        peer=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def do_GET(self): self.handle_request()
            def do_POST(self): self.handle_request()
            def handle_request(self):
                if self.headers.get('Authorization')!='Bearer '+TOKEN:return self.reply(403,{})
                raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
                path=urlsplit(self.path);body=json.loads(raw) if raw else None
                if path.path=='/api/status':return self.reply(200,{'current_card':UID,'assigned_revision':peer.mapping[UID]})
                if path.path=='/api/begin':
                    peer.stage={'revision':body['revision'],'manifest':json.loads(body['manifest']),'files':{}}
                    return self.reply(200,{'existing':body['revision'] in peer.packs})
                if path.path=='/api/chunk':
                    if peer.fail_chunk:return self.reply(500,{})
                    query=parse_qs(path.query);name=query['path'][0];offset=int(query['offset'][0]);files=peer.stage['files']
                    if len(files.get(name,b''))!=offset:return self.reply(409,{})
                    chunk=base64.b64decode(body['data'],validate=True);files[name]=files.get(name,b'')+chunk
                    return self.reply(200,{'next':len(files[name])})
                if path.path=='/api/commit':
                    stage=peer.stage
                    if peer.corrupt:return self.reply(409,{})
                    for a in stage['manifest']['assets']:
                        data=stage['files'].get(a['path'],b'')
                        if len(data)!=a['size'] or hashlib.sha256(data).hexdigest()!=a['sha256']:return self.reply(409,{})
                    if hashlib.sha256(canonical(stage['manifest'])).hexdigest()!=body['revision']:return self.reply(409,{})
                    peer.packs[body['revision']]=stage;return self.reply(200,{'revision':body['revision'],'state':'done'})
                if path.path=='/api/assign':
                    if body['revision'] not in peer.packs:return self.reply(409,{})
                    peer.mapping[body['uid']]=body['revision'];return self.reply(200,{**body,'state':'done'})
                self.reply(404,{})
            def reply(self,status,value):
                data=canonical(value);self.send_response(status);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        self.server=HTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()
    def connection(self,*args,**kwargs):return REAL_CONNECTION('127.0.0.1',self.server.server_port,timeout=3)


class WifiTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        audio=self.root/'test.wav'
        with wave.open(str(audio),'wb') as f:f.setparams((1,2,16000,0,'NONE','not compressed'));f.writeframes(b'\x00\x00'*16000)
        self.source=self.root/'pack';import_playlist([audio],self.source,'Wi-Fi story')
        self.studio=Studio(self.root/'studio');self.digest=self.studio.approve(self.source)
        self.peer=Peer();self.mock=patch('conteuse.wifi.http.client.HTTPConnection',side_effect=self.peer.connection);self.mock.start()
    def tearDown(self):self.mock.stop();self.peer.close();self.temp.cleanup()
    def test_real_http_upload_commit_assignment_and_reassignment(self):
        self.assertEqual(self.studio.wifi_status(TOKEN)['current_card'],UID)
        result=self.studio.wifi_card(self.source,UID.lower(),TOKEN)
        self.assertEqual(result,{'uid':UID,'revision':self.digest,'state':'done'})
        self.assertEqual(self.studio.state['cards'][UID],self.digest)
        self.assertEqual(self.peer.mapping[UID],self.digest)
        # Reusing a verified immutable pack needs no second audio upload.
        self.peer.fail_chunk=True
        self.studio.wifi_card(self.source,UID,TOKEN)
    def test_interrupted_transfer_preserves_previous_assignment_and_retry(self):
        self.peer.fail_chunk=True
        with self.assertRaises(ValueError):self.studio.wifi_card(self.source,UID,TOKEN)
        self.assertEqual(self.peer.mapping[UID],'old');self.assertNotIn(UID,self.studio.state['cards'])
        self.peer.fail_chunk=False;self.studio.wifi_card(self.source,UID,TOKEN)
        self.assertEqual(self.peer.mapping[UID],self.digest)
    def test_corrupt_commit_does_not_assign(self):
        self.peer.corrupt=True
        with self.assertRaises(ValueError):self.studio.wifi_card(self.source,UID,TOKEN)
        self.assertEqual(self.peer.mapping[UID],'old')
    def test_unapproved_or_invalid_credentials_do_not_assign(self):
        with self.assertRaises(ValueError):Player(TOKEN).send_card(self.source,UID,{})
        with self.assertRaises(ValueError):self.studio.wifi_status('b'*64)
        with self.assertRaises(ValueError):Player('not a token')
        self.assertEqual(self.peer.mapping[UID],'old')
    def test_uid_requires_family_and_crc(self):
        self.assertEqual(card_uid(UID.lower()),UID)
        for value in ['../bad','0'*16,UID[:-2]+'00',None]:
            with self.assertRaises(ValueError):card_uid(value)
    def test_incremental_verification_polling_and_deadline(self):
        client=Player(TOKEN)
        with patch.object(client,'request',side_effect=[{'state':'pending'},{'state':'done','revision':self.digest}]), patch('conteuse.wifi.time.sleep'):
            self.assertEqual(client.wait_job({'state':'pending'})['revision'],self.digest)
        with patch('conteuse.wifi.time.monotonic',side_effect=[0,7200]):
            with self.assertRaises(ValueError):client.wait_job({'state':'pending'})
        with self.assertRaises(ValueError):client.wait_job({'state':'error'})

    def test_binary_payload_includes_every_byte(self):
        payload=bytes(range(256))*40
        asset=self.source/'raw.bin';asset.write_bytes(payload)
        manifest_path=self.source/'manifest.json';manifest=json.loads(manifest_path.read_text())
        manifest['assets'].append({'path':'raw.bin','size':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
        manifest_path.write_bytes(canonical(manifest));digest=self.studio.approve(self.source)
        self.studio.wifi_card(self.source,UID,TOKEN)
        self.assertEqual(self.peer.packs[digest]['files']['raw.bin'],payload)

    def test_fat_case_collision_rejected_before_transfer(self):
        manifest_path=self.source/'manifest.json';manifest=json.loads(manifest_path.read_text())
        asset=manifest['assets'][0];other={**asset,'path':asset['path'].upper()}
        destination=self.source/other['path'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes((self.source/asset['path']).read_bytes())
        manifest['assets'].append(other);manifest_path.write_bytes(canonical(manifest))
        with self.assertRaisesRegex(ValueError,'FAT-compatible'):
            Player(TOKEN).send_card(self.source,UID,{revision(manifest)})

    def test_print_tool_is_local_and_has_fixed_physical_dimensions(self):
        from conteuse.studio import UI
        self.assertIn(b'33.6mm',UI);self.assertIn(b'38.6mm',UI)
        self.assertIn(b'createImageBitmap(file)',UI)
        self.assertNotIn(b'FormData',UI)
