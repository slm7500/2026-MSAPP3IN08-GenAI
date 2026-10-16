"""Base de licences simplifiée (identifiants SPDX) et normalisation des alias.

Les règles encodées ici sont une modélisation pédagogique des clauses principales
(usage commercial, œuvres dérivées, share-alike, attribution). Elles ne constituent
pas un avis juridique.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class License:
    spdx: str
    commercial: bool      # usage commercial autorisé
    derivatives: bool     # œuvres dérivées autorisées
    share_alike: bool     # la dérivée doit reprendre la même licence
    attribution: bool     # l'auteur doit être crédité
    kind: str             # "content" (source) ou "model" (poids / service)


LICENSES = {lic.spdx: lic for lic in [
    # Contenus (sources)
    License("CC0-1.0",           True,  True,  False, False, "content"),
    License("CC-BY-4.0",         True,  True,  False, True,  "content"),
    License("CC-BY-SA-4.0",      True,  True,  True,  True,  "content"),
    License("CC-BY-NC-4.0",      False, True,  False, True,  "content"),
    License("CC-BY-NC-SA-4.0",   False, True,  True,  True,  "content"),
    License("CC-BY-ND-4.0",      True,  False, False, True,  "content"),
    # Modèles
    License("MIT",               True,  True,  False, True,  "model"),
    License("Apache-2.0",        True,  True,  False, True,  "model"),
    License("BSD-3-Clause",      True,  True,  False, True,  "model"),
    License("OpenRAIL-M",        True,  True,  False, True,  "model"),
    License("LicenseRef-Research-Only", False, True, False, True, "model"),
]}

# Écritures courantes rencontrées dans les métadonnées réelles.
ALIASES = {
    "CC BY 4.0": "CC-BY-4.0",
    "CC-BY 4.0": "CC-BY-4.0",
    "Creative Commons Attribution 4.0": "CC-BY-4.0",
    "CC BY-SA 4.0": "CC-BY-SA-4.0",
    "CC BY-NC 4.0": "CC-BY-NC-4.0",
    "CC BY-NC-SA 4.0": "CC-BY-NC-SA-4.0",
    "CC BY-ND 4.0": "CC-BY-ND-4.0",
    "CC0": "CC0-1.0",
    "Public Domain (CC0)": "CC0-1.0",
    "Apache 2.0": "Apache-2.0",
    "MIT License": "MIT",
}

_LOOKUP = {k.lower(): k for k in LICENSES}
_LOOKUP.update({k.lower(): v for k, v in ALIASES.items()})

ALIASES_BY_SPDX = {}
for _alias, _spdx in ALIASES.items():
    ALIASES_BY_SPDX.setdefault(_spdx, []).append(_alias)

# Chaînes volontairement non reconnues (utilisées pour l'injection de la règle R2).
UNKNOWN_LICENSES = ["CC-BY-4", "Creative Commons", "CC-BY-NC-5.0",
                    "LicenseRef-Custom-Agency", "libre de droits", "voir site"]


def norm(license_str):
    """Renvoie l'identifiant SPDX canonique, ou None si la licence est inconnue."""
    if not isinstance(license_str, str):
        return None
    return _LOOKUP.get(license_str.strip().lower())


def lic(license_str):
    """Objet License correspondant, ou None."""
    spdx = norm(license_str)
    return LICENSES.get(spdx) if spdx else None
