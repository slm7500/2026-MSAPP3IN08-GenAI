"""Mesures : précision/rappel par règle, faux positifs, couverture, reproductibilité."""
from .injector import build_corpus, registry_of
from .manifest import coverage, export_jsonl, sha256_text
from .rules import RULES


def run_checker(items, checker, registry):
    rows = []
    for it in items:
        findings = checker(it["manifest"], it["content"], registry)
        rows.append({
            "artifact_id": it["manifest"].get("artifact_id"),
            "media_type": it["manifest"].get("media_type"),
            "intended_use": it["manifest"].get("intended_use", "—"),
            "truth": sorted(it["label"]),
            "pred": sorted({x["rule"] for x in findings}),
            "findings": findings,
        })
    return rows


def per_rule_metrics(rows):
    out = {}
    for r in RULES:
        tp = sum(1 for x in rows if r in x["truth"] and r in x["pred"])
        fp = sum(1 for x in rows if r not in x["truth"] and r in x["pred"])
        fn = sum(1 for x in rows if r in x["truth"] and r not in x["pred"])
        p = tp / (tp + fp) if tp + fp else 1.0
        rc = tp / (tp + fn) if tp + fn else 1.0
        f1 = 2 * p * rc / (p + rc) if p + rc else 0.0
        out[r] = {"tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": rc, "f1": f1}
    return out


def summary(rows):
    clean = [x for x in rows if not x["truth"]]
    bad = [x for x in rows if x["truth"]]
    tp = sum(len(set(x["truth"]) & set(x["pred"])) for x in rows)
    fp = sum(len(set(x["pred"]) - set(x["truth"])) for x in rows)
    fn = sum(len(set(x["truth"]) - set(x["pred"])) for x in rows)
    p = tp / (tp + fp) if tp + fp else 1.0
    r = tp / (tp + fn) if tp + fn else 1.0
    return {
        "n_total": len(rows),
        "n_conformes": len(clean),
        "n_violations": len(bad),
        "fausses_alertes_sur_conformes": sum(1 for x in clean if x["pred"]),
        "taux_fausses_alertes": sum(1 for x in clean if x["pred"]) / len(clean),
        "violations_detectees": sum(1 for x in bad if set(x["truth"]) <= set(x["pred"])),
        "taux_detection": sum(1 for x in bad if set(x["truth"]) <= set(x["pred"])) / len(bad),
        "diagnostic_exact": sum(1 for x in rows if x["truth"] == x["pred"]) / len(rows),
        "micro_precision": p,
        "micro_recall": r,
        "micro_f1": 2 * p * r / (p + r) if p + r else 0.0,
    }


def coverage_stats(items):
    vals = [coverage(it["manifest"]) for it in items]
    clean = [coverage(it["manifest"]) for it in items if not it["label"]]
    return {"moyenne_corpus": sum(vals) / len(vals),
            "moyenne_conformes": sum(clean) / len(clean),
            "minimum": min(vals)}


def reproducibility(seed=42):
    h1 = sha256_text(export_jsonl(build_corpus(seed)))
    h2 = sha256_text(export_jsonl(build_corpus(seed)))
    h3 = sha256_text(export_jsonl(build_corpus(seed + 1)))
    return {"hash_run_1": h1, "hash_run_2": h2, "identiques": h1 == h2,
            "hash_autre_graine": h3, "graine_differente_differe": h1 != h3}


def stress_evaluation(seed=7):
    """Faux positifs sur des manifestes légaux aux métadonnées « sales »."""
    from .baseline import check_naive
    from .injector import build_stress
    from .rules import check, check_v1
    items = build_stress(seed)
    registry = registry_of(items)
    res = {}
    for name, checker in [("baseline naïve", check_naive), ("vérificateur v1 (strict)", check_v1),
                          ("vérificateur v2 (normalisé)", check)]:
        rows = run_checker(items, checker, registry)
        flagged = [x for x in rows if x["pred"]]
        by_rule = {}
        for x in flagged:
            for r in x["pred"]:
                by_rule[r] = by_rule.get(r, 0) + 1
        res[name] = {"n": len(rows), "faux_positifs": len(flagged),
                     "taux_faux_positifs": len(flagged) / len(rows), "par_regle": by_rule}
    return res


def full_evaluation(seed=42):
    from .baseline import check_naive
    from .rules import check, check_v1
    items = build_corpus(seed)
    registry = registry_of(items)
    rows_full = run_checker(items, check, registry)
    rows_naive = run_checker(items, check_naive, registry)
    rows_v1 = run_checker(items, check_v1, registry)
    return {
        "metrics_v1": per_rule_metrics(rows_v1),
        "summary_v1": summary(rows_v1),
        "stress": stress_evaluation(),
        "items": items,
        "registry": registry,
        "rows_full": rows_full,
        "rows_naive": rows_naive,
        "metrics_full": per_rule_metrics(rows_full),
        "metrics_naive": per_rule_metrics(rows_naive),
        "summary_full": summary(rows_full),
        "summary_naive": summary(rows_naive),
        "coverage": coverage_stats(items),
    }
