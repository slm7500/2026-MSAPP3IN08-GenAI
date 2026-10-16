# K2 : Traçabilité et licences des générations

Groupe G26 « Xoxo Gossip Girl ». Version corrigée après audit technique du 16 octobre 2026.

## Groupe et contributions
Compte connu : @slm7500. Le second compte GitHub doit être renseigné par le binôme avant la PR publique. Les consignes du dépôt demandent les pseudonymes GitHub et excluent les noms civils, e-mails et numéros étudiants de la PR.

La répartition orale est une proposition, pas une attestation de contributions. Chaque membre doit lire, exécuter et adapter le code et contribuer réellement à l'historique Git. Aucun historique artificiel n'est fourni.

**Assistance IA déclarée :** Claude a préparé la version initiale. ChatGPT a audité le code, corrigé la validation de structure, ajouté les tests de régression et préparé les documents de soutenance. Le binôme doit comprendre et vérifier cette préparation avant remise.

## Sujet et MVP
- Sujet K2 du catalogue : associer à chaque génération modèles, prompt, sources, transformations et contraintes de licence.
- MVP : manifeste JSON, règles de compatibilité pédagogiques, trois pipelines média simulés et interface d'audit.
- Attribution du sujet : à confirmer par l'enseignant. Le dossier n'affirme pas une réservation exclusive de K2.

## Architecture
`pipelines.Factory` construit un contenu et son manifeste. `injector` ajoute des violations connues. `manifest.validate_manifest` valide les types et champs imbriqués. `rules.check` applique R1 à R8. `evaluate` calcule les métriques par comparaison aux étiquettes. `audit_ui` construit la page autonome.

Les artefacts audio référencent un manifeste texte parent par empreinte. Le registre teste la présence d'un parent. Il ne constitue ni une signature, ni une preuve de l'identité d'un émetteur.

## Installation sous Windows
Python 3.10 ou ultérieur. Versions principales vérifiées : matplotlib 3.10.8 et pandas 2.2.3. Aucun GPU ni service externe nécessaire. Utiliser un environnement virtuel.

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run_all.py
.venv\Scripts\python.exe -m unittest discover tests -v
.venv\Scripts\python.exe demo_validation.py
```

Sous Linux/macOS : `python3 -m venv .venv`, puis utiliser `.venv/bin/python` pour les mêmes commandes.
Le fichier `.env.example` indique qu'aucun paramètre secret n'est nécessaire. Ne jamais commiter de véritable `.env`.

## Utilisation
Ouvrir `outputs/audit.html` dans un navigateur après `run_all.py`. Filtrer par média, statut ou règle, puis sélectionner une ligne pour lire le manifeste et le détail des alertes. La page est générée à partir du corpus ; elle n'est pas une interface d'import de fichiers réels.

La démo de corrections se lance avec `python demo_validation.py`. Trois cas : manifeste correct, empreinte du prompt absente, sources de type entier. Les deux cas invalides doivent produire R1, sans exception non gérée.

Le notebook `K2_Tracabilite_Licences.ipynb` explique les étapes. Les diapositives se trouvent dans `slides/`. Lire `GUIDE_ORAL.md` pour répéter.

## Pipelines simulés
Texte : synthèse fabriquée à partir de métadonnées de sources fictives.
Image : octets préfixés SIMPNG, étapes génération et upscaling déclarées.
Audio : octets préfixés SIMWAV, narration et mixage déclarés.
**SIMPNG et SIMWAV ne sont pas des fichiers image/audio lisibles.** Les noms de modèles et les URL example.org sont fictifs. Aucun vrai modèle n'est exécuté.

## Tests et résultats
`python -m unittest discover tests -v` : **20 tests réussis**, dont les 8 tests initiaux et 12 régressions de structure. La validation rejette les prompts sans empreinte, les types invalides et les objets imbriqués incomplets. Les règles métier sont suspendues tant que R1 signale une structure inexploitable.

Campagne initiale reproduite : 290 artefacts, dont 150 conformes aux règles et 140 fautifs. Détection : baseline 55 %, v2 100 %. Fausses alertes sur conformes : baseline 74,7 %, v2 0 %. Corpus de robustesse synthétique : 115 / 120 fausses alertes pour la baseline, 103 / 120 pour la v1 et 0 / 120 pour la v2.

Les chiffres reposent sur une vérité terrain construite avec la même politique que le vérificateur. Ils ne constituent pas une mesure indépendante sur des données réelles. Les nouvelles régressions testent la structure et ne sont pas incluses dans les 290 artefacts de cette campagne.

Deux exports avec la graine 42 sont identiques au bit près. Une autre graine produit un export différent. Résultats complets dans `outputs/resultats.json` et `outputs/resultats.md`.

## Limites et plan B
- Politique simplifiée des licences. Une source SA n'entraîne pas automatiquement une conclusion sur toute sortie IA : le lien de dérivation est une hypothèse du démonstrateur.
- Le parseur valide une structure attendue, pas tout le standard JSON Schema ni la vérité des métadonnées.
- Aucune intégration de C2PA, aucune signature, aucune autorité de registre.
- Auteurs normalisés : risque de fusion de noms distincts.
- Test de robustesse construit sur des variations connues, sans corpus externe indépendant.
- Plan B hors ligne : résultats pré-générés, page HTML, notebook et slides. Aucun appel API nécessaire.

## Licence et références
Le code est distribué sous licence MIT, cohérente avec celle du dépôt des projets. Voir LICENSE. Le fait qu'un modèle fictif porte une licence dans le corpus n'attribue pas cette licence au projet. Les dépendances sont matplotlib (licence Matplotlib) et pandas (BSD-3-Clause), à consulter dans leurs distributions.

Les licences de contenus et modèles constituent ici des données pédagogiques, pas une validation juridique.
- Catalogue et règles du projet : https://github.com/jsboigeEPF/2026-MSAPP3IN08-GenAI
- Production Patterns : https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/GenAI/Texte/09_Production_Patterns.ipynb
- SPDX : https://spdx.dev/
- C2PA : https://c2pa.org/

## Remise GitHub
Forker **jsboigeEPF/2026-MSAPP3IN08-GenAI**, distinct du dépôt des TP. Créer une branche et n'ajouter que `groupe-xoxo-gossip-girl/`, en conservant les fichiers du dépôt hors de ce dossier. Relire le contenu avant commit. Ouvrir une PR brouillon tôt, puis la compléter et la soumettre au plus tard deux jours avant la soutenance. Le lien vers l'issue d'attribution et le second pseudonyme GitHub restent à renseigner. Voir `REMISE_GITHUB.md`.
