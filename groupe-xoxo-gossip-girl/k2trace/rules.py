"""Vérificateur de conformité : huit règles appliquées à un manifeste."""
import re

from .licenses import lic, norm
from .manifest import sha256_bytes, sha256_text, validate_manifest

RULES = {
    "R1": "Structure de métadonnées absente, incomplète ou invalide",
    "R2": "Licence non reconnue",
    "R3": "Clause non commerciale (NC) violée",
    "R4": "Œuvre « pas de modification » (ND) transformée",
    "R5": "Share-alike (SA) non respecté par la licence de sortie",
    "R6": "Attribution d'un auteur manquante",
    "R7": "Empreinte (hash) du contenu ou du prompt incorrecte",
    "R8": "Manifeste parent introuvable dans le registre",
}


def _label(x):
    return x.get("id") or x.get("name") or "?"


def norm_author(name):
    """« auteur_0001 », « AUTEUR 0001 » et « Auteur-0001 » désignent la même personne."""
    if not isinstance(name, str):
        return None
    return re.sub(r"[\s\-_.]+", " ", name.strip().lower())


def check_v1(manifest, content=None, registry=None):
    """Version 1 : comparaison stricte des noms d'auteurs (avant correction)."""
    return check(manifest, content, registry, strict_authors=True)


def check(manifest, content=None, registry=None, strict_authors=False):
    """Renvoie la liste des constats {rule, message}. Liste vide = conforme."""
    out_findings = []

    def add(rule, msg):
        out_findings.append({"rule": rule, "message": msg})

    # R1 — structure exploitable, y compris les objets imbriqués.
    # Les règles métier ne sont pas évaluables tant que la structure est invalide.
    structural_errors = validate_manifest(manifest)
    if structural_errors:
        return [{"rule": "R1", "message": message} for message in structural_errors]

    sources = manifest.get("sources") or []
    models = manifest.get("models") or []
    out = manifest.get("output_license")
    intended = manifest.get("intended_use")

    # R2 — licences reconnues (après normalisation des alias)
    for x in sources + models:
        if lic(x.get("license")) is None:
            add("R2", f"{_label(x)} : licence « {x.get('license')} » non reconnue")
    if out is not None and lic(out) is None:
        add("R2", f"licence de sortie « {out} » non reconnue")

    known_sources = [s for s in sources if lic(s.get("license"))]
    known_models = [m for m in models if lic(m.get("license"))]
    out_lic = lic(out)

    # R3 — non commercial
    for x in known_sources + known_models:
        if not lic(x["license"]).commercial:
            if intended == "commercial":
                add("R3", f"{_label(x)} ({x['license']}) interdit l'usage commercial visé")
            elif out_lic and out_lic.commercial and x in known_sources:
                add("R3", f"{_label(x)} ({x['license']}) : la licence de sortie {out} "
                          f"autoriserait un usage commercial")

    # R4 — pas de modification
    derivative = any(t.get("derivative") for t in manifest.get("transformations") or [])
    if derivative:
        for s in known_sources:
            if not lic(s["license"]).derivatives:
                add("R4", f"{_label(s)} ({s['license']}) interdit les œuvres dérivées")

    # R5 — partage dans les mêmes conditions
    if out_lic:
        for s in known_sources:
            if lic(s["license"]).share_alike and norm(s["license"]) != out_lic.spdx:
                add("R5", f"{_label(s)} ({s['license']}) impose la même licence, "
                          f"sortie déclarée : {out}")

    # R6 — attribution
    key = (lambda a: a) if strict_authors else norm_author
    credited = {key(a) for a in manifest.get("attributions") or []}
    for s in known_sources:
        if lic(s["license"]).attribution and key(s.get("author")) not in credited:
            add("R6", f"{_label(s)} : l'auteur « {s.get('author')} » n'est pas crédité")

    # R7 — intégrité
    declared = manifest.get("content_sha256")
    if content is not None and not isinstance(content, bytes):
        add("R7", "le contenu à vérifier doit être fourni en bytes")
    elif content is not None and declared and sha256_bytes(content) != declared:
        add("R7", "l'empreinte du contenu ne correspond pas au fichier")
    prompt = manifest.get("prompt")
    if isinstance(prompt, dict) and prompt.get("text") is not None and prompt.get("sha256"):
        if sha256_text(prompt["text"]) != prompt["sha256"]:
            add("R7", "l'empreinte du prompt ne correspond pas au texte")

    # R8 — chaîne de provenance
    if registry is not None:
        for h in manifest.get("parents") or []:
            if h not in registry:
                add("R8", f"parent {h[:12]}… introuvable")

    return out_findings
