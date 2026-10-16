"""Construction du corpus de test : manifestes conformes + violations injectées
dont la vérité terrain est connue."""
import copy
import random

from .licenses import LICENSES, UNKNOWN_LICENSES, lic
from .manifest import manifest_hash, sha256_text
from .pipelines import Factory

R1_FIELDS = ["models", "prompt", "output_license", "content_sha256", "intended_use", "sources"]


def _add_source(f, m, spdx, kind="article"):
    s = f.new_source(spdx, kind, alias=False)
    m["sources"].append(s)
    if LICENSES[spdx].attribution:
        m["attributions"] = sorted(set(m["attributions"]) | {s["author"]})


def mut_R1(f, it, rng):
    del it["manifest"][rng.choice(R1_FIELDS)]


def mut_R2(f, it, rng):
    rng.choice(it["manifest"]["sources"])["license"] = rng.choice(UNKNOWN_LICENSES)


def mut_R3(f, it, rng):
    m = it["manifest"]
    if rng.random() < 0.5:
        _add_source(f, m, "CC-BY-NC-4.0")
    else:
        m["models"][0] = {"name": "ResearchGen-13B", "version": "0.1",
                          "license": "LicenseRef-Research-Only"}


def mut_R4(f, it, rng):
    _add_source(f, it["manifest"], "CC-BY-ND-4.0")


def mut_R5(f, it, rng):
    _add_source(f, it["manifest"], "CC-BY-SA-4.0")


def mut_R6(f, it, rng):
    m = it["manifest"]
    cands = [s for s in m["sources"]
             if lic(s["license"]) and lic(s["license"]).attribution and s["author"] in m["attributions"]]
    victim = rng.choice(cands)
    m["attributions"] = [a for a in m["attributions"] if a != victim["author"]]


def mut_R7(f, it, rng):
    if rng.random() < 0.5:
        it["content"] = it["content"] + b"\x00"          # fichier retouché après coup
    else:
        it["manifest"]["prompt"]["text"] += " (modifié)"  # prompt réécrit sans mise à jour


def mut_R8(f, it, rng):
    it["manifest"]["parents"] = [sha256_text(f"parent-fantome-{rng.random()}")]


MUTATIONS = {"R1": mut_R1, "R2": mut_R2, "R3": mut_R3, "R4": mut_R4,
             "R5": mut_R5, "R6": mut_R6, "R7": mut_R7, "R8": mut_R8}


def _has_sa(m):
    return any(lic(s["license"]) and lic(s["license"]).share_alike for s in m["sources"]) \
        or LICENSES[m["output_license"]].share_alike


PRECONDITIONS = {
    "R3": lambda m: m["intended_use"] == "commercial",
    "R5": lambda m: not _has_sa(m),
    "R6": lambda m: any(lic(s["license"]) and lic(s["license"]).attribution for s in m["sources"]),
    "R8": lambda m: m["media_type"] == "audio",
}


def _ok(rule, m):
    return PRECONDITIONS.get(rule, lambda _m: True)(m)


def build_corpus(seed=42, n_text=60, n_image=45, n_audio=45, n_per_rule=15, n_double=20):
    """Renvoie la liste des éléments {manifest, content, label}.

    label = [] pour un manifeste conforme, sinon la liste des règles violées.
    """
    f = Factory(seed)
    rng = random.Random(seed + 1)

    texts = [f.text_pipeline(f.random_intended()) for _ in range(n_text)]
    images = [f.image_pipeline(f.random_intended()) for _ in range(n_image)]
    audios = [f.audio_pipeline(f.rng.choice(texts)) for _ in range(n_audio)]
    clean = texts + images + audios

    injected = []
    for rule, mutate in MUTATIONS.items():
        cands = [it for it in clean if _ok(rule, it["manifest"])]
        for k in range(n_per_rule):
            it = copy.deepcopy(rng.choice(cands))
            it["manifest"]["artifact_id"] += f"-inj{rule}-{k:02d}"
            mutate(f, it, rng)
            it["label"] = [rule]
            injected.append(it)

    pair_rules = ["R3", "R4", "R6", "R7"]
    for k in range(n_double):
        rules = sorted(rng.sample(pair_rules, 2))
        cands = [it for it in clean if all(_ok(r, it["manifest"]) for r in rules)]
        it = copy.deepcopy(rng.choice(cands))
        it["manifest"]["artifact_id"] += f"-inj{'+'.join(rules)}-{k:02d}"
        for r in rules:
            MUTATIONS[r](f, it, rng)
        it["label"] = rules
        injected.append(it)

    return clean + injected


def _messy_name(name, rng):
    variants = [name.upper(), name.lower(), name.replace("-", " "),
                name.replace("-", "_"), f"  {name} ", name]
    return rng.choice(variants)


def build_stress(seed=7, n=120):
    """Corpus de robustesse : manifestes LÉGAUX mais aux métadonnées « sales »,
    comme dans la vraie vie (alias de licences fréquents, noms d'auteurs saisis
    avec des casses et séparateurs variables). Tout signalement est un faux positif."""
    f = Factory(seed, alias_rate=0.6)
    rng = random.Random(seed + 1)

    def mess(batch):
        for it in batch:
            m = it["manifest"]
            m["attributions"] = [_messy_name(a, rng) for a in m["attributions"]]
        return batch

    # Les textes sont « salis » avant de servir de parents : l'empreinte parent
    # enregistrée par l'audio reste donc valide.
    texts = mess([f.text_pipeline(f.random_intended()) for _ in range(n // 3)])
    images = mess([f.image_pipeline(f.random_intended()) for _ in range(n // 3)])
    audios = mess([f.audio_pipeline(f.rng.choice(texts)) for _ in range(n - 2 * (n // 3))])
    return texts + images + audios


def registry_of(items):
    """Registre des empreintes de manifestes connus (pour la règle R8)."""
    return {manifest_hash(it["manifest"]) for it in items}
