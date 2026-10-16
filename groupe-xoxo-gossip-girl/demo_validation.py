"""Démonstration des corrections de structure. Assistance de ChatGPT déclarée."""
import copy
from k2trace.pipelines import Factory
from k2trace.rules import check

item = Factory(1).text_pipeline("commercial")
for name, change in [
    ("Manifeste correct", lambda m: None),
    ("Empreinte du prompt absente", lambda m: m["prompt"].pop("sha256")),
    ("Sources mal formatées", lambda m: m.update(sources=123)),
]:
    manifest = copy.deepcopy(item["manifest"])
    change(manifest)
    findings = check(manifest, item["content"], set())
    print(f"\n{name}")
    if not findings:
        print("Conforme aux règles du démonstrateur")
    for finding in findings:
        print(f"{finding['rule']} : {finding['message']}")
