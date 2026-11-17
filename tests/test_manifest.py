import copy
import json
from pathlib import Path
import unittest
from conteuse.manifest import validate


class ManifestTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "examples/first-adventure/manifest.json"
        self.pack = json.loads(path.read_text())

    def test_valid_example_unchanged(self):
        before = copy.deepcopy(self.pack)
        self.assertEqual(validate(self.pack), [])
        self.assertEqual(self.pack, before)

    def test_dangling_choice(self):
        self.pack["nodes"][0]["choices"][0]["target"] = "missing"
        self.assertTrue(any("missing node" in e for e in validate(self.pack)))

    def test_duplicate_node(self):
        self.pack["nodes"].append(self.pack["nodes"][0])
        self.assertTrue(any("duplicate node" in e for e in validate(self.pack)))

    def test_unreachable_node(self):
        self.pack["nodes"].append({"id": "lost", "text": "Lost."})
        self.assertIn("unreachable node: lost", validate(self.pack))

    def test_bad_start(self):
        self.pack["start"] = []
        self.assertIn("start must reference an existing node", validate(self.pack))

    def test_malformed_input(self):
        for value in (None, [], "hello", 4):
            with self.subTest(value=value):
                self.assertTrue(validate(value))

    def test_invalid_nodes_and_choices(self):
        for node in (None, {}, {"id": "x", "choices": None},
                     {"id": "x", "text": "hi", "choices": [None, {"target": []}]}):
            with self.subTest(node=node):
                self.pack["nodes"] = [node]
                self.assertTrue(validate(self.pack))

    def test_boolean_is_not_version(self):
        self.pack["format_version"] = True
        self.assertTrue(validate(self.pack))


if __name__ == "__main__":
    unittest.main()
