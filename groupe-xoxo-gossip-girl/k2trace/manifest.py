"""Schéma du manifeste de traçabilité et fonctions d'empreinte."""
import base64
import hashlib
import json
import re

MANIFEST_VERSION = "1.0"

# Champs obligatoires d'un manifeste.
REQUIRED = [
    "manifest_version", "artifact_id", "media_type", "created_at",
    "intended_use", "output_license", "content_sha256", "models",
    "prompt", "sources", "transformations", "attributions",
]
# Champs recommandés, vérifiés pour la mesure de couverture.
RECOMMENDED_SOURCE = ["id", "title", "author", "license", "url", "sha256"]
RECOMMENDED_MODEL = ["name", "version", "license"]

EXAMPLE = {
    "manifest_version": "1.0",
    "artifact_id": "text-0001",
    "media_type": "text",
    "created_at": "2026-10-01T00:01:00Z",
    "intended_use": "commercial",
    "output_license": "CC-BY-4.0",
    "content_sha256": "<sha256 du contenu généré>",
    "models": [{"name": "TextGen-7B", "version": "1.2", "license": "Apache-2.0"}],
    "prompt": {"text": "Rédige une synthèse…", "sha256": "<sha256 du prompt>"},
    "sources": [{"id": "src-0001", "title": "Article n°1", "author": "Auteur-0001",
                 "license": "CC-BY-4.0", "url": "https://example.org/article/1",
                 "sha256": "<sha256 de la source>"}],
    "transformations": [{"step": "generate", "tool": "TextGen-7B", "derivative": True}],
    "attributions": ["Auteur-0001"],
    "parents": [],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical(obj) -> str:
    """Sérialisation JSON déterministe (clés triées, sans espaces)."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def manifest_hash(manifest: dict) -> str:
    return sha256_text(canonical(manifest))


def is_filled(field, value) -> bool:
    if field == "attributions":          # une liste vide est légitime (sources CC0)
        return isinstance(value, list)
    return value not in (None, "", [], {})


def coverage(manifest: dict) -> float:
    """Part des champs obligatoires et recommandés effectivement renseignés."""
    total = filled = 0
    for f in REQUIRED:
        total += 1
        filled += is_filled(f, manifest.get(f))
    for s in manifest.get("sources") if isinstance(manifest.get("sources"), list) else []:
        if not isinstance(s, dict):
            s = {}
        for f in RECOMMENDED_SOURCE:
            total += 1
            filled += is_filled(f, s.get(f))
    for m in manifest.get("models") if isinstance(manifest.get("models"), list) else []:
        if not isinstance(m, dict):
            m = {}
        for f in RECOMMENDED_MODEL:
            total += 1
            filled += is_filled(f, m.get(f))
    return filled / total if total else 0.0


def validate_manifest(manifest):
    """Valide les types et les champs imbriqués avant toute règle métier.

    Une liste de messages vide indique une structure exploitable. Aucun contenu
    n'est corrigé silencieusement. Les licences inconnues restent traitées par R2.
    """
    if not isinstance(manifest, dict):
        return ["le manifeste doit être un objet JSON"]
    errors = []
    for field in REQUIRED:
        if not is_filled(field, manifest.get(field)):
            errors.append(f"champ « {field} » absent ou vide")

    def text(value, path):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{path} doit être un texte non vide")

    def digest(value, path):
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-fA-F]{64}", value) is None:
            errors.append(f"{path} doit être une empreinte SHA-256 de 64 caractères hexadécimaux")

    for field in ["manifest_version", "artifact_id", "created_at", "output_license"]:
        text(manifest.get(field), field)
    if manifest.get("media_type") not in ("text", "image", "audio"):
        errors.append("media_type doit valoir text, image ou audio")
    if manifest.get("intended_use") not in ("commercial", "non-commercial"):
        errors.append("intended_use doit valoir commercial ou non-commercial")
    digest(manifest.get("content_sha256"), "content_sha256")

    prompt = manifest.get("prompt")
    if not isinstance(prompt, dict):
        errors.append("prompt doit être un objet JSON")
    else:
        text(prompt.get("text"), "prompt.text")
        digest(prompt.get("sha256"), "prompt.sha256")

    for field, fields in [("models", RECOMMENDED_MODEL), ("sources", RECOMMENDED_SOURCE)]:
        entries = manifest.get(field)
        if not isinstance(entries, list):
            errors.append(f"{field} doit être une liste")
            continue
        for i, entry in enumerate(entries):
            prefix = f"{field}[{i}]"
            if not isinstance(entry, dict):
                errors.append(f"{prefix} doit être un objet JSON")
                continue
            for key in fields:
                if key == "sha256":
                    digest(entry.get(key), f"{prefix}.{key}")
                else:
                    text(entry.get(key), f"{prefix}.{key}")

    transformations = manifest.get("transformations")
    if not isinstance(transformations, list):
        errors.append("transformations doit être une liste")
    else:
        for i, entry in enumerate(transformations):
            if not isinstance(entry, dict):
                errors.append(f"transformations[{i}] doit être un objet JSON")
                continue
            text(entry.get("step"), f"transformations[{i}].step")
            text(entry.get("tool"), f"transformations[{i}].tool")
            if not isinstance(entry.get("derivative"), bool):
                errors.append(f"transformations[{i}].derivative doit être un booléen")

    attributions = manifest.get("attributions")
    if not isinstance(attributions, list):
        errors.append("attributions doit être une liste")
    else:
        for i, name in enumerate(attributions):
            text(name, f"attributions[{i}]")
    parents = manifest.get("parents", [])
    if not isinstance(parents, list):
        errors.append("parents doit être une liste")
    else:
        for i, parent in enumerate(parents):
            digest(parent, f"parents[{i}]")
    return list(dict.fromkeys(errors))


def export_jsonl(items) -> str:
    """Export reproductible du corpus (manifestes + contenus en base64)."""
    lines = []
    for it in items:
        lines.append(canonical({
            "manifest": it["manifest"],
            "content_b64": base64.b64encode(it["content"]).decode("ascii"),
            "label": it["label"],
        }))
    return "\n".join(lines) + "\n"
