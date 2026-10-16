"""Tests unitaires — lancer avec : python -m unittest discover tests"""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from k2trace import build_corpus, check, export_jsonl, norm, registry_of, sha256_text  # noqa: E402
from k2trace.injector import build_stress  # noqa: E402
from k2trace.pipelines import Factory  # noqa: E402
from k2trace.rules import check_v1  # noqa: E402


class TestLicences(unittest.TestCase):
    def test_alias(self):
        self.assertEqual(norm("CC BY 4.0"), "CC-BY-4.0")
        self.assertEqual(norm(" mit license "), "MIT")
        self.assertIsNone(norm("CC-BY-4"))
        self.assertIsNone(norm(None))


class TestRegles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = build_corpus(42)
        cls.registry = registry_of(cls.items)

    def test_conformes_sans_alerte(self):
        for it in self.items:
            if not it["label"]:
                self.assertEqual(check(it["manifest"], it["content"], self.registry), [],
                                 it["manifest"]["artifact_id"])

    def test_violations_diagnostiquees(self):
        for it in self.items:
            if it["label"]:
                pred = sorted({f["rule"] for f in check(it["manifest"], it["content"], self.registry)})
                self.assertEqual(pred, it["label"], it["manifest"]["artifact_id"])

    def test_nc_commercial(self):
        it = copy.deepcopy(Factory(1).text_pipeline("commercial"))
        it["manifest"]["sources"][0]["license"] = "CC-BY-NC-4.0"
        rules = {f["rule"] for f in check(it["manifest"], it["content"])}
        self.assertIn("R3", rules)

    def test_contenu_retouche(self):
        it = Factory(2).image_pipeline("commercial")
        rules = {f["rule"] for f in check(it["manifest"], it["content"] + b"x")}
        self.assertEqual(rules, {"R7"})


class TestRobustesse(unittest.TestCase):
    def test_v2_sans_faux_positif(self):
        items = build_stress(7)
        reg = registry_of(items)
        self.assertTrue(all(check(i["manifest"], i["content"], reg) == [] for i in items))

    def test_v1_fragile(self):
        items = build_stress(7)
        reg = registry_of(items)
        self.assertTrue(any(check_v1(i["manifest"], i["content"], reg) for i in items))


class TestReproductibilite(unittest.TestCase):
    def test_export_identique(self):
        a = sha256_text(export_jsonl(build_corpus(42)))
        b = sha256_text(export_jsonl(build_corpus(42)))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
