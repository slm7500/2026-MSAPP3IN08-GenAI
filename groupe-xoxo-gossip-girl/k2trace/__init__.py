"""k2trace — traçabilité et licences des générations (sujet K2)."""
from .baseline import check_naive
from .injector import build_corpus, registry_of
from .licenses import LICENSES, norm
from .manifest import coverage, export_jsonl, manifest_hash, sha256_text
from .rules import RULES, check

__all__ = ["LICENSES", "RULES", "build_corpus", "check", "check_naive", "coverage",
           "export_jsonl", "manifest_hash", "norm", "registry_of", "sha256_text"]
