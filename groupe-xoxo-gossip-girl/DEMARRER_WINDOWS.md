# Ouvrir K2 sur Windows

1. Extraire complètement l'archive avec clic droit, puis **Extraire tout**.
2. Ouvrir le dossier **groupe-xoxo-gossip-girl**.
3. Pour voir l'interface immédiatement : ouvrir **outputs**, puis double-cliquer sur **audit.html**.
4. Pour voir la présentation : ouvrir **slides**, puis **K2_Xoxo_Gossip_Girl.pptx** avec PowerPoint. Le texte oral est dans **GUIDE_ORAL.md**.
5. Pour reproduire le projet : revenir dans le dossier groupe-xoxo-gossip-girl. Dans la barre d'adresse de l'Explorateur, saisir **cmd**, puis Entrée.
6. Saisir les commandes ci-dessous, une à la fois.

```text
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run_all.py
.venv\Scripts\python.exe demo_validation.py
.venv\Scripts\python.exe -m unittest discover tests -v
```

Si py n'est pas reconnu, installer Python depuis son site officiel python.org, puis rouvrir le terminal. Les deux dépendances doivent être téléchargées une fois pour reconstruire les graphiques. Les fichiers d'audit et le PowerPoint déjà fournis s'ouvrent sans Python.

Résultat attendu : 20 tests réussis. La démo doit afficher « Conforme aux règles du démonstrateur » pour le premier cas, puis des alertes R1 pour les deux cas invalides.

Le projet ne demande aucune clé API. Ne saisir aucun mot de passe ou secret dans le code. Le travail GitHub du projet est distinct de celui des TP. Lire REMISE_GITHUB.md avant dépôt.
