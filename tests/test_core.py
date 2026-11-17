import copy
import hashlib
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from conteuse.packages import activate, active_pack, check_pack, revision, safe_path
from conteuse.player import Player
from conteuse.studio import Studio, make_server
from conteuse.feeds import parse_rss, public_addresses, station_capability
from conteuse.editorial import Draft, fake_narrator
from conteuse.manifest import validate

EXAMPLE = Path(__file__).resolve().parents[1] / "examples/first-adventure"


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pack = json.loads((EXAMPLE / "manifest.json").read_text())
        self.source = self.root / "source"
        self.source.mkdir()
        self.write()

    def write(self):
        (self.source / "manifest.json").write_text(json.dumps(self.pack))

    def asset(self):
        audio = b"test bytes, not audio"
        (self.source / "audio.bin").write_bytes(audio)
        self.pack["assets"] = [{"path": "audio.bin", "size": len(audio), "sha256": hashlib.sha256(audio).hexdigest()}]
        self.pack["nodes"][0]["audio"] = "audio.bin"
        self.write()

    def test_revision_and_approval_bind_every_content_byte(self):
        self.asset()
        old = revision(self.pack)
        self.pack["nodes"][0]["text"] += " Changed"
        self.write()
        self.assertNotEqual(old, revision(self.pack))
        with self.assertRaises(ValueError):
            activate(self.source, self.root / "library", old)

    def test_transfer_restart_and_old_library(self):
        self.asset()
        library = self.root / "library"
        activate(self.source, library, revision(self.pack))
        original = active_pack(library)
        self.pack["title"] += " v2"
        self.write()
        with self.assertRaises(InterruptedError):
            activate(self.source, library, revision(self.pack), interrupt=True)
        self.assertEqual(active_pack(library), original)
        activate(self.source, library, revision(self.pack))
        self.assertEqual(active_pack(library), self.pack)
        self.assertEqual(len(list((library / "versions").iterdir())), 2)
        activate(self.source, library, revision(self.pack))

    def test_tamper_and_quota(self):
        self.asset()
        with patch('conteuse.packages.MAX_TOTAL',4):
            with self.assertRaisesRegex(ValueError,'pack quota exceeded'):
                check_pack(self.source)
        (self.source / "audio.bin").write_bytes(b"wrong")
        with self.assertRaisesRegex(ValueError, "changed asset"):
            check_pack(self.source)
        self.pack["assets"][0]["size"] = 2**40
        self.write()
        with self.assertRaisesRegex(ValueError, "size/hash"):
            check_pack(self.source)

    def test_symlinks_and_paths(self):
        for path in ("../a", "/etc/passwd", "a/../b", "a\\b", "a//b", "C:x", "a/./b", ""):
            self.assertFalse(safe_path(path), path)
        self.asset()
        (self.source / "audio.bin").unlink()
        (self.source / "audio.bin").symlink_to(EXAMPLE / "manifest.json")
        with self.assertRaisesRegex(ValueError, "symlink"):
            check_pack(self.source)

    def test_closed_cycle_and_escapable_loop(self):
        self.pack["nodes"][1]["choices"] = [{"label": "Again", "target": "pond"}]
        self.assertIn("trapped node: pond", validate(self.pack))
        self.pack["nodes"][1]["choices"].append({"label": "Exit", "target": "tree"})
        self.assertEqual(validate(self.pack), [])

    def test_player_restart_choices_and_muting(self):
        p = Player(self.pack)
        self.assertFalse(p.wifi)
        p.toggle()
        self.assertTrue(p.speaker_enabled)
        p.headphones = True
        self.assertFalse(p.speaker_enabled)
        with self.assertRaises(ValueError):
            p.choose(0)
        p.ended()
        self.assertEqual(p.view("mini")["spoken_choices"], p.view("explore")["menu"])
        p.choose(1)
        b = p.bookmark()
        q = Player(self.pack)
        q.restore(b)
        self.assertEqual(q.node, "tree")
        self.assertEqual(q.state, "paused")
        q.back()
        self.assertEqual(q.node, "gate")
        b["revision"] = "wrong"
        with self.assertRaises(ValueError):
            q.restore(b)
        p.ended()
        self.assertEqual(p.state, "ended")

    def test_radio_bounds(self):
        p = Player(self.pack)
        with self.assertRaises(ValueError):
            p.start_radio(False, True)
        p.start_radio(True, False)
        self.assertTrue(p.wifi)
        for _ in range(3):
            p.stream_failed()
        self.assertEqual(p.state, "offline")
        p.select_local()
        self.assertFalse(p.wifi)
        self.assertEqual(station_capability("https://example.org/live", "audio/mpeg"), "direct")
        self.assertEqual(station_capability("https://example.org/live", "application/vnd.apple.mpegurl"), "unsupported")

    def test_studio_approvals_cards_and_pairing(self):
        s = Studio(self.root / "studio")
        with self.assertRaises(ValueError):
            s.publish(self.source)
        digest = s.approve(self.source)
        s.assign_card("012345", digest)
        s.publish(self.source)
        self.pack["title"] += " changed"
        self.write()
        with self.assertRaises(ValueError):
            s.publish(self.source)
        with self.assertRaises(ValueError):
            s.begin_pair()
        code = s.begin_pair(True)
        secret = s.claim_pair(code, "mini-1")
        self.assertTrue(s.authenticate("mini-1", secret))
        self.assertFalse(s.authenticate("mini-1", "wrong"))
        with self.assertRaises(ValueError):
            s.claim_pair(code, "mini-2")
        self.assertTrue(Studio(s.root).authenticate("mini-1", secret))
        self.assertNotIn(secret, s.path.read_text())
        self.assertEqual(s.path.stat().st_mode & 0o777, 0o600)

    def test_episode_changed_bytes_not_title(self):
        s = Studio(self.root / "studio")
        self.assertFalse(s.observe_episode("guid", b"one")["changed"])
        changed = s.observe_episode("guid", b"two")
        self.assertTrue(changed["changed"])
        self.assertTrue(changed["approval_required"])

    def test_http_auth_origin_host_and_workflow(self):
        server = make_server(Studio(self.root / "studio"), "test-token", 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        client = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
        self.addCleanup(client.close)
        def post(action, token="test-token", **headers):
            client.request("POST", "/api/" + action, json.dumps({"source": str(self.source)}),
                           {"Authorization": "Bearer " + token, **headers})
            response = client.getresponse()
            data = json.loads(response.read())
            return response.status, data
        self.assertEqual(post("approve", "bad")[0], 403)
        self.assertEqual(post("approve", Origin="https://evil.example")[0], 403)
        self.assertEqual(post("approve", Host="evil.example")[0], 403)
        self.assertEqual(post("publish")[0], 400)
        self.assertEqual(post("inspect")[0], 200)
        self.assertEqual(post("approve")[0], 200)
        self.assertEqual(post("publish")[0], 200)

    def test_rss_and_dns_rebinding_boundary(self):
        feed = b'<rss><channel><item><guid>one</guid><title>Title</title><enclosure url="https://example.org/a.mp3" type="audio/mpeg"/></item></channel></rss>'
        self.assertEqual(parse_rss(feed)[0]["guid"], "one")
        with self.assertRaises(ValueError):
            parse_rss(b'<!DOCTYPE rss><rss/>')
        with self.assertRaises(ValueError):
            parse_rss(feed.replace(b"</channel>", feed[14:feed.index(b"</channel>")] + b"</channel>"))
        for ip in ("127.0.0.1", "169.254.169.254", "10.0.0.1", "::1"):
            with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", (ip, 443))]):
                with self.assertRaises(ValueError):
                    public_addresses("example.org")

    def test_editorial_separate_approvals_and_invalidation(self):
        draft = Draft("Original draft requiring review.", [{"title": "Source", "url": "https://example.org"}])
        with self.assertRaises(ValueError):
            draft.narrate(fake_narrator)
        draft.approve_script()
        draft.narrate(fake_narrator)
        with self.assertRaises(ValueError):
            draft.publication()
        draft.approve_audio()
        self.assertEqual(draft.publication()["transcript"], draft.script)
        draft.script += " Edit"
        with self.assertRaises(ValueError):
            draft.publication()
        draft.approve_script()
        with self.assertRaises(ValueError):
            draft.approve_audio()

class ImportTests(unittest.TestCase):
    def test_import_and_authenticated_sync_recovery(self):
        from conteuse.imports import import_playlist
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);audio=root/'voice.wav';audio.write_bytes(b'RIFFfixture')
            pack=import_playlist([audio],root/'pack','My recording')
            self.assertEqual(check_pack(root/'pack'),pack)
            studio=Studio(root/'studio');studio.approve(root/'pack')
            code=studio.begin_pair(True);secret=studio.claim_pair(code,'mini')
            with self.assertRaises(ValueError):studio.sync('mini','wrong',root/'pack',root/'device')
            studio.sync('mini',secret,root/'pack',root/'device')
            with self.assertRaises(InterruptedError):studio.sync('mini',secret,root/'pack',root/'device',interrupt=True)
            self.assertEqual(active_pack(root/'device'),pack)
            with self.assertRaises(ValueError):import_playlist([audio],root/'pack')

    def test_bad_audio_reference_and_bookmark(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'manifest.json').write_text(json.dumps({'format_version':1,'id':'x','title':'X','start':'x','nodes':None}))
            with self.assertRaisesRegex(ValueError,'nodes must be a non-empty list'):
                check_pack(root)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);pack=json.loads((EXAMPLE/'manifest.json').read_text())
            pack['nodes'][0]['audio']=[]
            (root/'manifest.json').write_text(json.dumps(pack))
            with self.assertRaises(ValueError):check_pack(root)
        pack=json.loads((EXAMPLE/'manifest.json').read_text());player=Player(pack)
        mark=player.bookmark();mark['history']=[[]]
        with self.assertRaises(ValueError):player.restore(mark)


class RecoveryTests(unittest.TestCase):
    def test_corrupt_current_falls_back_to_verified_previous(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';source.mkdir()
            pack=json.loads((EXAMPLE/'manifest.json').read_text())
            def write(): (source/'manifest.json').write_text(json.dumps(pack))
            write();activate(source,root/'library',revision(pack));old=copy.deepcopy(pack)
            pack['title']+=' second';write();activate(source,root/'library',revision(pack))
            active=root/'library'/'versions'/revision(pack)/'manifest.json'
            active.write_text('{}')
            self.assertEqual(active_pack(root/'library'),old)
            (root/'library'/'active.json').write_text('{truncated')
            self.assertEqual(active_pack(root/'library'),old)

    def test_pairing_expiry_and_wrong_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            studio=Studio(tmp);code=studio.begin_pair(True)
            with self.assertRaises(ValueError):studio.claim_pair('wrong','mini')
            with patch('conteuse.studio.time.monotonic',return_value=studio.pending_pair[1]+1):
                with self.assertRaises(ValueError):studio.claim_pair(code,'mini')

class StudioAuthoringTests(unittest.TestCase):
    def test_import_card_and_station_in_parent_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);audio=root/'voice.wav';audio.write_bytes(b'RIFFfixture')
            studio=Studio(root/'studio')
            result=studio.import_audio([str(audio)],root/'pack','Family')
            self.assertFalse(result['approved'])
            digest=studio.approve(root/'pack');studio.assign_card('aabb',digest)
            self.assertEqual(studio.state['cards']['aabb'],digest)
            station=studio.approve_station('speech','http://example.org/direct.mp3','audio/mpeg')
            self.assertTrue(station['approved'])
            with self.assertRaises(ValueError):studio.approve_station('hls','https://example.org/live.m3u8','application/vnd.apple.mpegurl')
            with self.assertRaises(ValueError):studio.approve_station('private','https://user:pass@example.org/live','audio/mpeg')

    def test_audio_change_revokes_final_editorial_publication(self):
        draft=Draft('Review me',[{'title':'Source','url':'https://example.org'}])
        draft.approve_script();draft.narrate(fake_narrator);draft.approve_audio()
        draft.audio+=b'changed'
        with self.assertRaises(ValueError):draft.publication()

class DeviceCapabilityTests(unittest.TestCase):
    def test_export_gate_canonical_pcm_and_noncanonical_media(self):
        from conteuse.device import check_device_pack
        from conteuse.imports import import_playlist
        import wave
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);audio=root/'voice.wav'
            with wave.open(str(audio),'wb') as wav:
                wav.setparams((1,2,16000,0,'NONE','not compressed'));wav.writeframes(b'\x00\x00'*100)
            import_playlist([audio],root/'pack')
            self.assertEqual(check_device_pack(root/'pack')['start'],'track-0')
            audio.write_bytes(b'not a WAV recording')
            import_playlist([audio],root/'bad')
            with self.assertRaises(ValueError):check_device_pack(root/'bad')

    def test_bounded_asset_copy_rejects_growth(self):
        from conteuse.packages import asset_digest
        import io
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'asset';path.write_bytes(b'longer than declared')
            dest=io.BytesIO()
            with self.assertRaises(ValueError):asset_digest(path,3,dest)
            self.assertEqual(dest.getvalue(),b'lon')
