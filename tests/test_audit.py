"""Regression cases discovered by the independent release audit."""
import copy
import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from conteuse.device import check_device_pack
from conteuse.imports import import_playlist
from conteuse.manifest import validate
from conteuse.packages import activate, active_pack, revision
from conteuse.studio import Studio, make_server

ROOT = Path(__file__).resolve().parents[1]


def sample():
    return {'format_version': 1, 'id': 'sample', 'title': 'Sample',
            'start': 'end', 'nodes': [{'id': 'end', 'text': 'The end.'}]}


class AuditRegressionTests(unittest.TestCase):
    def test_shared_firmware_export_fixtures(self):
        fixtures = json.loads((ROOT / 'tests/fixtures/device-contract.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            for case in fixtures:
                with self.subTest(case=case['name']):
                    (source / 'manifest.json').write_text(json.dumps(case['pack']))
                    if case['accept']: self.assertEqual(check_device_pack(source), case['pack'])
                    else:
                        with self.assertRaises(ValueError): check_device_pack(source)
    def test_repeated_activation_preserves_last_different_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'source'; source.mkdir()
            first = sample(); second = copy.deepcopy(first); second['title'] = 'Second'
            for pack in (first, second, second):
                (source / 'manifest.json').write_text(json.dumps(pack))
                activate(source, root / 'library', revision(pack))
            (root / 'library/versions' / revision(second) / 'manifest.json').write_text('{}')
            self.assertEqual(active_pack(root / 'library'), first)

    def test_device_rejects_nul_in_content_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            for field in ('text', 'id', 'metadata'):
                pack = sample()
                if field == 'metadata': pack['metadata'] = {'label': 'visible\0hidden'}
                else:
                    pack['nodes'][0][field] += '\0hidden'
                    if field == 'id': pack['start'] = pack['nodes'][0]['id']
                (source / 'manifest.json').write_text(json.dumps(pack))
                with self.assertRaisesRegex(ValueError, 'NUL'): check_device_pack(source)

    def test_device_nesting_boundary_matches_firmware(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            for levels, accepted in ((11, True), (12, False)):
                pack = sample(); metadata = 'value'
                for _ in range(levels): metadata = {'next': metadata}
                pack['metadata'] = metadata
                (source / 'manifest.json').write_text(json.dumps(pack))
                if accepted: self.assertEqual(check_device_pack(source), pack)
                else:
                    with self.assertRaisesRegex(ValueError, 'nesting'): check_device_pack(source)

    def test_graph_long_chain_and_optional_cycle_have_terminal_escape(self):
        pack = sample(); count = 6000; pack['start'] = 'n0'
        pack['nodes'] = [{'id': f'n{i}', 'text': 'Continue.',
            'choices': [{'label': 'Next', 'target': f'n{i+1}'}] if i+1<count else []} for i in range(count)]
        self.assertEqual(validate(pack), [])
        pack['nodes'][1]['choices'].append({'label': 'Again', 'target': 'n0'})
        self.assertEqual(validate(pack), [])
        pack['nodes'][-1]['choices'] = [{'label': 'Loop', 'target': 'n0'}]
        self.assertTrue(any(e.startswith('trapped node:') for e in validate(pack)))

    def test_import_rejects_wrong_types_before_touching_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'new'
            for files, title in (([], 42), ('not a list', 'Title'), ([42], 'Title')):
                with self.assertRaises(ValueError): import_playlist(files, dest, title)
                self.assertFalse(dest.exists())

    def test_http_wrong_types_return_json_errors_without_disconnect(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = make_server(Studio(tmp), 'test-token', 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True);thread.start()
            try:
                client = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=3)
                for route, body in [('import', {'files': [], 'destination': tmp+'/new', 'title':42}),
                                    ('card', {'uid':42, 'revision':'a'*64}), ('inspect', []), ('inspect', {'source':42})]:
                    client.request('POST', '/api/'+route, json.dumps(body), {'Authorization':'Bearer test-token'})
                    response = client.getresponse();data=json.loads(response.read())
                    self.assertEqual(response.status,400);self.assertIn('error',data)
                client.close()
            finally:
                server.shutdown();server.server_close();thread.join()

    def test_incomplete_cad_gate_receipt_is_rejected(self):
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        try:
            from cad_contract import verify_exports
            exports=json.loads((ROOT/'enclosure/mesh-checks.json').read_text())['exports']
            for name in ('work/current/mini-usb_plug_clearance.stl','work/current/explore-cap_pair_interference.stl'):
                incomplete=copy.deepcopy(exports);incomplete.pop(name)
                with self.assertRaises(AssertionError):verify_exports(incomplete)
        finally:
            sys.path.pop(0)

    def test_failed_narration_does_not_change_catalogue_or_source_files(self):
        spec = importlib.util.spec_from_file_location('galia_narration', ROOT / 'content/starter/generate_audio.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        catalog = json.loads((ROOT / 'content/starter/index.json').read_text())
        before = copy.deepcopy(catalog)
        calls = []
        def render(plan, out):
            calls.append(out.name)
            if len(calls) == 2: raise RuntimeError('simulated interrupted renderer')
            out.write_bytes(b'first staged recording')
        with tempfile.TemporaryDirectory() as tmp, patch.object(module, 'probe_audio', return_value=(150.0, {'codec_name':'mp3','sample_rate':'22050','channels':1})):
            with self.assertRaises(RuntimeError): module.prepare_batch(catalog, Path(tmp), render, {})
            self.assertFalse((Path(tmp) / 'generation.json').exists())
        self.assertEqual(catalog, before)

    def test_existing_narration_batch_must_contain_exact_audio_bytes(self):
        spec=importlib.util.spec_from_file_location('galia_narration',ROOT/'content/starter/generate_audio.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);audio=b'exact approved bytes';credits='Voice sources'
            asset={'story_id':'example','language':'fr','path':'content/audio/'+'a'*24+'/example.fr.mp3',
                   'audio_sha256':module.sha(audio)}
            receipt={'batch_id':'a'*24,'audio_assets':[asset],'credits_sha256':module.sha(credits.encode())}
            (directory/'example.fr.mp3').write_bytes(audio);(directory/'CREDITS.txt').write_text(credits)
            (directory/'generation.json').write_text(json.dumps(receipt))
            module.verify_batch(directory,receipt)
            (directory/'example.fr.mp3').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'corrupt'):module.verify_batch(directory,receipt)
            (directory/'example.fr.mp3').unlink()
            with self.assertRaisesRegex(ValueError,'Missing'):module.verify_batch(directory,receipt)

    def test_new_narration_resets_approvals_without_mutating_input(self):
        spec=importlib.util.spec_from_file_location('galia_narration',ROOT/'content/starter/generate_audio.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        catalog=json.loads((ROOT/'content/starter/index.json').read_text())
        catalog['script_approval']=catalog['audio_approval']='approved'
        for story in catalog['stories']:story['script_approval']=story['audio_approval']='approved'
        before=copy.deepcopy(catalog)
        def render(plan,out):out.write_bytes(('render '+out.name).encode())
        with tempfile.TemporaryDirectory() as tmp,patch.object(module,'probe_audio',return_value=(180.0,{'codec_name':'mp3','sample_rate':'22050','channels':1})):
            batch,revised,receipt=module.prepare_batch(catalog,Path(tmp),render,{},'Voice credits')
            module.verify_batch(Path(tmp),receipt)
            self.assertEqual(len(receipt['audio_assets']),6)
            self.assertEqual(revised['script_approval'],'pending');self.assertEqual(revised['audio_approval'],'pending')
            for story in revised['stories']:
                self.assertEqual(story['script_approval'],'pending');self.assertEqual(story['audio_approval'],'pending')
        self.assertEqual(catalog,before)
