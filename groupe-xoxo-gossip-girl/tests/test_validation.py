"""Régressions des deux défauts relevés par l'audit. Assistance ChatGPT déclarée."""
import copy
import unittest

from k2trace.pipelines import Factory
from k2trace.rules import check


class TestValidationStructure(unittest.TestCase):
    def setUp(self):
        self.item = Factory(1).text_pipeline("commercial")

    def assert_invalid(self, manifest):
        findings = check(manifest, self.item["content"], set())
        self.assertTrue(findings)
        self.assertEqual({x["rule"] for x in findings}, {"R1"})

    def test_prompt_sans_hash(self):
        m = copy.deepcopy(self.item["manifest"])
        del m["prompt"]["sha256"]
        self.assert_invalid(m)

    def test_hash_prompt_vide(self):
        m = copy.deepcopy(self.item["manifest"])
        m["prompt"]["sha256"] = ""
        self.assert_invalid(m)

    def test_types_sources_invalides(self):
        for value in [123, "oops", {"id": 1}, [None], ["source"]]:
            with self.subTest(value=value):
                m = copy.deepcopy(self.item["manifest"])
                m["sources"] = value
                self.assert_invalid(m)

    def test_types_models_invalides(self):
        for value in [123, "oops", [False]]:
            m = copy.deepcopy(self.item["manifest"])
            m["models"] = value
            self.assert_invalid(m)

    def test_manifestes_non_objets(self):
        for value in [None, [], 123, "manifest"]:
            self.assert_invalid(value)

    def test_source_incomplete(self):
        for field in ["id", "title", "author", "license", "url", "sha256"]:
            m = copy.deepcopy(self.item["manifest"])
            del m["sources"][0][field]
            self.assert_invalid(m)

    def test_modele_incomplet(self):
        m = copy.deepcopy(self.item["manifest"])
        del m["models"][0]["version"]
        self.assert_invalid(m)

    def test_transformations_invalides(self):
        for value in ["generate", [None], [{"step": "generate", "tool": "x", "derivative": "oui"}]]:
            m = copy.deepcopy(self.item["manifest"])
            m["transformations"] = value
            self.assert_invalid(m)

    def test_attributions_invalides(self):
        for value in ["Alice", [None], [123]]:
            m = copy.deepcopy(self.item["manifest"])
            m["attributions"] = value
            self.assert_invalid(m)

    def test_parents_invalides(self):
        for value in ["parent", [123], ["invalid"]]:
            m = copy.deepcopy(self.item["manifest"])
            m["parents"] = value
            self.assert_invalid(m)

    def test_contenu_mauvais_type(self):
        findings = check(self.item["manifest"], "texte au lieu de bytes", set())
        self.assertEqual({x["rule"] for x in findings}, {"R7"})

    def test_licence_inconnue_reste_r2(self):
        m = copy.deepcopy(self.item["manifest"])
        m["sources"][0]["license"] = "Licence inconnue"
        self.assertIn("R2", {x["rule"] for x in check(m, self.item["content"], set())})


if __name__ == "__main__":
    unittest.main()
