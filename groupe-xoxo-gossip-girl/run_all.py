"""Lance toute la campagne et écrit les résultats dans outputs/.

Usage : python run_all.py
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from k2trace.audit_ui import build_audit_html  # noqa: E402
from k2trace.evaluate import full_evaluation, reproducibility  # noqa: E402
from k2trace.manifest import export_jsonl  # noqa: E402
from k2trace.rules import RULES  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def pct(x):
    return f"{100 * x:.1f} %"


def prec(m):
    return "n/a" if m["tp"] + m["fp"] == 0 else pct(m["precision"])


def plot_rules(res, path):
    rules = list(RULES)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    colors = {"Baseline naïve": "#c9a227", "Vérificateur v2": "#2b4c7e"}
    for ax, metric, title in [(axes[0], "precision", "Précision par règle"),
                              (axes[1], "recall", "Rappel par règle")]:
        w = 0.38
        xs = range(len(rules))
        for j, (name, key) in enumerate([("Baseline naïve", "metrics_naive"),
                                         ("Vérificateur v2", "metrics_full")]):
            ms = [res[key][r] for r in rules]
            na = [metric == "precision" and m["tp"] + m["fp"] == 0 for m in ms]
            vals = [0 if n else m[metric] for m, n in zip(ms, na)]
            pos = [x + (j - 0.5) * w for x in xs]
            ax.bar(pos, vals, w, label=name if ax is axes[0] else None, color=colors[name])
            for x, n in zip(pos, na):
                if n:
                    ax.text(x, 0.02, "n/a", ha="center", fontsize=8, rotation=90)
        ax.set_xticks(list(xs), rules)
        ax.set_ylim(0, 1.05)
        ax.set_title(title, fontsize=11, loc="left")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.25)
    fig.legend(frameon=False, fontsize=9, loc="upper right", ncol=2)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_stress(stress, path):
    names = list(stress)
    vals = [stress[n]["taux_faux_positifs"] for n in names]
    fig, ax = plt.subplots(figsize=(7, 2.8))
    bars = ax.barh(names, vals, color=["#c9a227", "#9aa7b8", "#2b4c7e"])
    for b, v in zip(bars, vals):
        ax.text(v + 0.01, b.get_y() + b.get_height() / 2, pct(v), va="center", fontsize=9)
    ax.set_xlim(0, 1.1)
    ax.invert_yaxis()
    ax.set_title("Faux positifs sur 120 manifestes légaux aux métadonnées « sales »",
                 fontsize=11, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def metrics_markdown(res, repro):
    s, n, v1 = res["summary_full"], res["summary_naive"], res["summary_v1"]
    lines = ["# Résultats de la campagne (graine 42)", "",
             f"Corpus : {s['n_total']} générations — {s['n_conformes']} conformes, "
             f"{s['n_violations']} avec violations injectées (dont 20 à double violation).", "",
             "## Vue d'ensemble", "",
             "| Indicateur | Baseline naïve | Vérificateur v1 | Vérificateur v2 |",
             "|---|---|---|---|"]
    for label, key in [("Violations détectées", "taux_detection"),
                       ("Fausses alertes sur conformes", "taux_fausses_alertes"),
                       ("Diagnostic exact (bonnes règles)", "diagnostic_exact"),
                       ("Précision (micro)", "micro_precision"),
                       ("Rappel (micro)", "micro_recall"),
                       ("F1 (micro)", "micro_f1")]:
        lines.append(f"| {label} | {pct(n[key])} | {pct(v1[key])} | {pct(s[key])} |")
    lines += ["", "## Par règle", "",
              "| Règle | Description | Baseline P / R | Vérificateur v2 P / R | TP | FP | FN |",
              "|---|---|---|---|---|---|---|"]
    for r, d in RULES.items():
        a, b = res["metrics_naive"][r], res["metrics_full"][r]
        lines.append(f"| {r} | {d} | {prec(a)} / {pct(a['recall'])} | "
                     f"{prec(b)} / {pct(b['recall'])} | {b['tp']} | {b['fp']} | {b['fn']} |")
    lines += ["", "n/a : la baseline ne produit aucune alerte pour cette règle (précision non définie).", "",
              "## Robustesse (120 manifestes légaux, métadonnées « sales »)", "",
              "| Vérificateur | Faux positifs | Règles en cause |", "|---|---|---|"]
    for name, d in res["stress"].items():
        causes = ", ".join(f"{k} ×{v}" for k, v in sorted(d["par_regle"].items())) or "—"
        lines.append(f"| {name} | {d['faux_positifs']} / {d['n']} ({pct(d['taux_faux_positifs'])}) | {causes} |")
    c = res["coverage"]
    lines += ["", "## Couverture des métadonnées", "",
              f"- Moyenne sur tout le corpus : {pct(c['moyenne_corpus'])}",
              f"- Moyenne sur les manifestes conformes : {pct(c['moyenne_conformes'])}",
              f"- Minimum : {pct(c['minimum'])}", "",
              "## Reproductibilité", "",
              f"- Export, exécution 1 : `{repro['hash_run_1']}`",
              f"- Export, exécution 2 : `{repro['hash_run_2']}`",
              f"- Identiques : **{'oui' if repro['identiques'] else 'non'}**",
              f"- Autre graine : `{repro['hash_autre_graine']}` (différent : "
              f"{'oui' if repro['graine_differente_differe'] else 'non'})", ""]
    return "\n".join(lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    res = full_evaluation(42)
    repro = reproducibility(42)

    with open(os.path.join(OUT, "corpus.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(export_jsonl(res["items"]))
    with open(os.path.join(OUT, "resultats.json"), "w", encoding="utf-8") as fh:
        json.dump({k: res[k] for k in ["summary_full", "summary_v1", "summary_naive", "metrics_full",
                                       "metrics_v1", "metrics_naive", "stress", "coverage"]}
                  | {"reproductibilite": repro}, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "resultats.md"), "w", encoding="utf-8") as fh:
        fh.write(metrics_markdown(res, repro))
    with open(os.path.join(OUT, "audit.html"), "w", encoding="utf-8") as fh:
        fh.write(build_audit_html(res["items"], res["rows_full"], res["summary_full"]))
    plot_rules(res, os.path.join(OUT, "precision_rappel.png"))
    plot_stress(res["stress"], os.path.join(OUT, "robustesse.png"))
    print(metrics_markdown(res, repro))


if __name__ == "__main__":
    main()
