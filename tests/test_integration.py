import copy,importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('integration',Path(__file__).resolve().parents[1]/'scripts/integrated_hardware.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class IntegrationTests(unittest.TestCase):
 def setUp(self):self.c,self.l=m.read_data()
 def test_nominal_geometry_and_models(self):self.assertEqual(m.validate(self.c,self.l),[])
 def test_collision_detected(self):
  self.l['common'][0]['xyz']=self.l['common'][1]['xyz'][:]
  self.assertTrue(any('overlap' in x for x in m.validate(self.c,self.l)))
 def test_corrupt_model_detected(self):
  self.c['parts'][0]['model']['sha256']='invalid'
  self.assertTrue(any('changed model' in x for x in m.validate(self.c,self.l)))
 def test_quote_does_not_invent_missing_cost(self):
  q=m.quote(self.c);self.assertIn('memory_card',q['missing_quotes']);self.assertFalse(q['is_complete_landed_quote'])
 def test_shared_packs_and_fastener_rounding(self):
  q=m.quote(self.c);rows={r['part']:r for r in q['lines']}
  self.assertEqual(rows['petg']['buy_quantity'],1)
  self.assertEqual(rows['case_screw']['needed'],86)
  self.assertEqual(rows['case_screw']['buy_quantity'],100)
  self.assertEqual(m.quote(self.c,2,2)['known_subtotals']['GBP'],'62.88')
 def test_identity_required(self):
  self.c['parts'][0]['part_number']=''
  self.assertTrue(any('identification' in x for x in m.validate(self.c,self.l)))

 def test_export_manifest_matches_sources_and_print_meshes(self):
  import hashlib,json
  spec=importlib.util.spec_from_file_location('exporter',m.ROOT/'scripts/export_integrated.py');ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
  folder=m.ROOT/'enclosure/integrated/print';manifest=json.loads((folder/'manifest.json').read_text())
  self.assertEqual(len(manifest['parts']),20)
  for name,digest in manifest['source_sha256'].items():self.assertEqual(hashlib.sha256((m.ROOT/name).read_bytes()).hexdigest(),digest,name)
  for name,expected in manifest['parts'].items():self.assertEqual(ex.inspect(folder/name),expected,name)
