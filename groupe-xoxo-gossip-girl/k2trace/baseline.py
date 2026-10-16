"""Baseline naïve : liste noire par mots-clés, sans normalisation ni vérification
d'empreintes. Elle représente ce qu'on ferait « à la main » sans manifeste structuré."""
from .licenses import LICENSES
from .manifest import REQUIRED


def check_naive(manifest, content=None, registry=None):
    findings = []

    def add(rule, msg):
        findings.append({"rule": rule, "message": msg})

    for f in REQUIRED:
        if f not in manifest:
            add("R1", f"champ « {f} » absent")

    sources = manifest.get("sources") or []
    models = manifest.get("models") or []
    licenses = [x.get("license") for x in sources + models] + [manifest.get("output_license")]
    for l in licenses:
        if l is None:
            continue
        if l not in LICENSES:
            add("R2", f"licence « {l} » hors liste exacte")
        if "NC" in l or "Research" in l:
            add("R3", f"licence restrictive « {l} » détectée")
        if "ND" in l:
            add("R4", f"licence ND « {l} » détectée")
        if "SA" in l:
            add("R5", f"licence SA « {l} » détectée")
    return findings
