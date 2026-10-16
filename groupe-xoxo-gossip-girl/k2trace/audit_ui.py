"""Interface d'audit : page HTML autonome (aucune dépendance) listant chaque
génération, son manifeste et les constats du vérificateur."""
import json

from .rules import RULES

TEMPLATE = r"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Audit de traçabilité K2</title>
<style>
:root{--bg:#f7f6f2;--panel:#fff;--ink:#1d1d1b;--muted:#6b6a65;--line:#e3e1da;
--ok:#1f7a4d;--okbg:#e4f3ea;--bad:#b3261e;--badbg:#fbe6e4;--accent:#2b4c7e;--mono:ui-monospace,Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--panel:#1f1f1c;--ink:#ecebe6;--muted:#9c9a92;
--line:#33322e;--ok:#6fcf97;--okbg:#1d3326;--bad:#f28b82;--badbg:#3a1f1d;--accent:#8fb3e8}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:28px 16px 8px;max-width:1180px;margin:auto}
h1{margin:0;font-size:22px}header p{margin:4px 0 0;color:var(--muted)}
main{max-width:1180px;margin:auto;padding:8px 16px 40px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:16px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:24px;font-variant-numeric:tabular-nums}.kpi span{color:var(--muted);font-size:13px}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
select,input{font:inherit;padding:7px 10px;border:1px solid var(--line);border-radius:8px;
background:var(--panel);color:var(--ink)}input{flex:1;min-width:180px}
.layout{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:14px}
@media (max-width:860px){.layout{grid-template-columns:1fr}}
.list{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:auto;max-height:70vh}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
th{position:sticky;top:0;background:var(--panel);color:var(--muted);font-weight:600;font-size:12px}
tr{cursor:pointer}tr:hover td{background:color-mix(in srgb,var(--accent) 7%,transparent)}
tr.sel td{background:color-mix(in srgb,var(--accent) 15%,transparent)}
.tag{display:inline-block;padding:1px 8px;border-radius:99px;font-size:12px;font-weight:600}
.ok{background:var(--okbg);color:var(--ok)}.bad{background:var(--badbg);color:var(--bad)}
.detail{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;max-height:70vh;overflow:auto}
.detail h2{font-size:16px;margin:0 0 8px}.finding{border-left:3px solid var(--bad);padding:4px 10px;margin:6px 0}
.finding b{font-family:var(--mono)}pre{font:12px/1.45 var(--mono);background:var(--bg);padding:10px;
border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all}
.muted{color:var(--muted)}.legend{font-size:13px;color:var(--muted);margin-top:10px}
</style></head><body>
<header><h1>Audit de traçabilité et de licences</h1>
<p>Projet K2 — chaque génération (texte, image, audio) est accompagnée d'un manifeste vérifié par 8 règles.</p></header>
<main>
<div class="kpis" id="kpis"></div>
<div class="filters">
<select id="fStatus"><option value="">Tous les statuts</option><option value="ok">Conformes</option><option value="bad">Non conformes</option></select>
<select id="fRule"><option value="">Toutes les règles</option></select>
<select id="fMedia"><option value="">Tous les médias</option><option>text</option><option>image</option><option>audio</option></select>
<input id="q" placeholder="Rechercher un identifiant, une licence, un auteur…">
</div>
<div class="layout">
<div class="list"><table><thead><tr><th>Artefact</th><th>Média</th><th>Usage</th><th>Statut</th><th>Règles</th></tr></thead>
<tbody id="rows"></tbody></table></div>
<div class="detail" id="detail"><p class="muted">Sélectionnez une ligne pour voir le manifeste et les constats.</p></div>
</div>
<p class="legend" id="legend"></p>
</main>
<script>
const DATA=__DATA__, RULES=__RULES__, KPI=__KPI__;
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
$("kpis").innerHTML=KPI.map(k=>`<div class="kpi"><b>${esc(k[1])}</b><span>${esc(k[0])}</span></div>`).join("");
for(const [r,d] of Object.entries(RULES)) $("fRule").insertAdjacentHTML("beforeend",`<option value="${r}">${r} — ${esc(d)}</option>`);
$("legend").innerHTML=Object.entries(RULES).map(([r,d])=>`<b>${r}</b> ${esc(d)}`).join(" · ");
let selected=null;
function render(){
  const st=$("fStatus").value, ru=$("fRule").value, me=$("fMedia").value, q=$("q").value.toLowerCase();
  const rows=DATA.filter(d=>(!st||(st==="ok")===(d.pred.length===0))&&(!ru||d.pred.includes(ru))
    &&(!me||d.media===me)&&(!q||JSON.stringify(d).toLowerCase().includes(q)));
  $("rows").innerHTML=rows.map(d=>`<tr data-id="${esc(d.id)}" class="${d.id===selected?"sel":""}">
    <td>${esc(d.id)}</td><td>${esc(d.media)}</td><td>${esc(d.use)}</td>
    <td><span class="tag ${d.pred.length?"bad":"ok"}">${d.pred.length?"Non conforme":"Conforme"}</span></td>
    <td>${esc(d.pred.join(", "))}</td></tr>`).join("")||`<tr><td colspan="5" class="muted">Aucun résultat.</td></tr>`;
}
function show(id){
  selected=id;const d=DATA.find(x=>x.id===id);
  const f=d.findings.length?d.findings.map(x=>`<div class="finding"><b>${x.rule}</b> ${esc(x.message)}</div>`).join("")
    :`<p><span class="tag ok">Conforme</span> aucune règle enfreinte.</p>`;
  $("detail").innerHTML=`<h2>${esc(d.id)}</h2>${f}<h2 style="margin-top:14px">Manifeste</h2><pre>${esc(JSON.stringify(d.manifest,null,2))}</pre>`;
  render();
}
$("rows").addEventListener("click",e=>{const tr=e.target.closest("tr[data-id]");if(tr)show(tr.dataset.id)});
["fStatus","fRule","fMedia"].forEach(i=>$(i).addEventListener("change",render));$("q").addEventListener("input",render);
render();
</script></body></html>
"""


def build_audit_html(items, rows, summary):
    data = []
    for it, row in zip(items, rows):
        data.append({"id": row["artifact_id"], "media": row["media_type"], "use": row["intended_use"],
                     "pred": row["pred"], "findings": row["findings"], "manifest": it["manifest"]})
    kpi = [
        ["générations auditées", summary["n_total"]],
        ["déclarées conformes", sum(1 for r in rows if not r["pred"])],
        ["non conformes", sum(1 for r in rows if r["pred"])],
        ["règles vérifiées", len(RULES)],
    ]
    dump = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    return (TEMPLATE.replace("__DATA__", dump(data)).replace("__RULES__", dump(RULES))
            .replace("__KPI__", dump(kpi)))
