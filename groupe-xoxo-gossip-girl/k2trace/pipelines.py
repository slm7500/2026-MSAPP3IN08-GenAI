"""Trois pipelines média simulés (texte, image, audio) qui produisent un contenu
et son manifeste de traçabilité.

Les « générations » sont déterministes et simulées : le sujet porte sur la
traçabilité, pas sur la qualité des contenus. Chaque pipeline enregistre les
modèles, le prompt, les sources, les transformations et les attributions.
"""
import copy
import random
from datetime import datetime, timedelta

from .licenses import ALIASES_BY_SPDX, LICENSES, lic, norm
from .manifest import MANIFEST_VERSION, manifest_hash, sha256_bytes, sha256_text

TOPICS = ["l'énergie solaire", "l'histoire de Marrakech", "la biodiversité urbaine",
          "le recyclage du cuir", "les marchés financiers", "la mobilité douce",
          "l'architecture art déco", "les réseaux de neurones", "la gastronomie belge",
          "le climat méditerranéen"]

MODELS = {
    "text": [("TextGen-7B", "1.2", "Apache-2.0"), ("TinyLM-1B", "0.9", "MIT")],
    "image": [("ImageGen-XL", "3.5", "OpenRAIL-M")],
    "upscale": [("Upscaler-4x", "2.0", "BSD-3-Clause")],
    "audio": [("VoiceTTS", "1.0", "MIT")],
    "research": [("ResearchGen-13B", "0.1", "LicenseRef-Research-Only")],
}

KIND_LABEL = {"article": "Article", "image": "Image de référence", "music": "Musique"}
BASE_DATE = datetime(2026, 10, 1)


class Factory:
    """Génère des contenus et des manifestes conformes, de façon reproductible."""

    def __init__(self, seed=42, alias_rate=0.15):
        self.rng = random.Random(seed)
        self.alias_rate = alias_rate
        self.n = 0
        self.src_n = 0

    # ---------- sources ----------
    def _maybe_alias(self, spdx):
        aliases = ALIASES_BY_SPDX.get(spdx)
        if aliases and self.rng.random() < self.alias_rate:
            return self.rng.choice(aliases)
        return spdx

    def new_source(self, spdx, kind="article", alias=True):
        self.src_n += 1
        i = self.src_n
        return {
            "id": f"src-{i:04d}",
            "title": f"{KIND_LABEL[kind]} n°{i}",
            "author": f"Auteur-{i:04d}",
            "license": self._maybe_alias(spdx) if alias else spdx,
            "url": f"https://example.org/{kind}/{i}",
            "sha256": sha256_text(f"{kind}|{i}|{spdx}"),
        }

    def _pick_licenses(self, intended, k):
        """Tire k licences compatibles entre elles pour l'usage visé."""
        pool = ["CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0"]
        if intended == "non-commercial":
            pool += ["CC-BY-NC-4.0", "CC-BY-NC-SA-4.0"]
        lics = [self.rng.choice(pool) for _ in range(k)]
        sa = [l for l in lics if LICENSES[l].share_alike]
        if sa:  # une seule famille share-alike, et pas de NC si la famille SA autorise le commercial
            family = sa[0]
            fixed = []
            for l in lics:
                L = LICENSES[l]
                if L.share_alike and l != family:
                    l = "CC-BY-4.0"
                elif LICENSES[family].commercial and not L.commercial:
                    l = "CC-BY-4.0"
                fixed.append(l)
            lics = fixed
        return lics

    def _pick_sources(self, intended, kind, k):
        return [self.new_source(l, kind) for l in self._pick_licenses(intended, k)]

    def _output_license(self, intended, sources):
        spdx = [norm(s["license"]) for s in sources]
        sa = [l for l in spdx if LICENSES[l].share_alike]
        if sa:
            return sa[0]
        if any(not LICENSES[l].commercial for l in spdx):
            return "CC-BY-NC-4.0"
        if intended == "non-commercial":
            return self.rng.choice(["CC-BY-4.0", "CC-BY-NC-4.0", "CC0-1.0"])
        return self.rng.choice(["CC-BY-4.0", "CC0-1.0"])

    def _text_model(self, intended):
        if intended == "non-commercial" and self.rng.random() < 0.3:
            return MODELS["research"][0]
        return self.rng.choice(MODELS["text"])

    # ---------- assemblage ----------
    def _finalize(self, media, intended, sources, models, prompt, transformations,
                  content, parents, out=None):
        self.n += 1
        if out is None:
            out = self._output_license(intended, sources)
        attributions = sorted({s["author"] for s in sources
                               if lic(s["license"]) and lic(s["license"]).attribution})
        manifest = {
            "manifest_version": MANIFEST_VERSION,
            "artifact_id": f"{media}-{self.n:04d}",
            "media_type": media,
            "created_at": (BASE_DATE + timedelta(minutes=self.n)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "intended_use": intended,
            "output_license": out,
            "content_sha256": sha256_bytes(content),
            "models": [{"name": n, "version": v, "license": l} for n, v, l in models],
            "prompt": {"text": prompt, "sha256": sha256_text(prompt)},
            "sources": sources,
            "transformations": transformations,
            "attributions": attributions,
            "parents": parents,
        }
        return {"manifest": manifest, "content": content, "label": []}

    def random_intended(self):
        return "commercial" if self.rng.random() < 0.5 else "non-commercial"

    # ---------- pipeline 1 : texte (RAG simulé) ----------
    def text_pipeline(self, intended):
        topic = self.rng.choice(TOPICS)
        sources = self._pick_sources(intended, "article", self.rng.randint(1, 3))
        model = self._text_model(intended)
        prompt = f"Rédige une synthèse de 200 mots sur {topic} à partir des sources fournies."
        body = " ".join(f"[{s['id']}] {s['title']}." for s in sources)
        content = f"Synthèse sur {topic}. {body}".encode("utf-8")
        transformations = [
            {"step": "retrieve", "tool": "bm25-local", "derivative": False},
            {"step": "generate", "tool": model[0], "derivative": True},
        ]
        return self._finalize("text", intended, sources, [model], prompt,
                              transformations, content, [])

    # ---------- pipeline 2 : image (génération + upscaling) ----------
    def image_pipeline(self, intended):
        topic = self.rng.choice(TOPICS)
        sources = self._pick_sources(intended, "image", self.rng.randint(1, 2))
        gen, up = MODELS["image"][0], MODELS["upscale"][0]
        prompt = f"Illustration éditoriale sur {topic}, style aquarelle, d'après les images de référence."
        content = b"SIMPNG" + self.rng.randbytes(256)
        transformations = [
            {"step": "generate", "tool": gen[0], "derivative": True},
            {"step": "upscale", "tool": up[0], "derivative": True},
        ]
        return self._finalize("image", intended, sources, [gen, up], prompt,
                              transformations, content, [])

    # ---------- pipeline 3 : audio (narration d'un texte parent) ----------
    def audio_pipeline(self, parent):
        pm = parent["manifest"]
        intended = pm["intended_use"]
        sources = copy.deepcopy(pm["sources"])           # la narration hérite des sources du texte
        if self.rng.random() < 0.6:                       # musique d'ambiance
            sources.append(self.new_source(self.rng.choice(["CC0-1.0", "CC-BY-4.0"]), "music"))
        tts = MODELS["audio"][0]
        prompt = f"Lis le texte {pm['artifact_id']} d'une voix calme, puis mixe la musique en fond."
        content = b"SIMWAV" + self.rng.randbytes(384)
        transformations = [
            {"step": "tts", "tool": tts[0], "derivative": True},
            {"step": "mix", "tool": "ffmpeg", "derivative": True},
        ]
        return self._finalize("audio", intended, sources, [tts], prompt, transformations,
                              content, [manifest_hash(pm)], out=pm["output_license"])
