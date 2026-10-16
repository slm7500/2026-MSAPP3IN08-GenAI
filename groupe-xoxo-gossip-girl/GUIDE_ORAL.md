# Guide oral K2

Répartition proposée : intervenante 1 = Salma, intervenante 2 = Hiba. Cette proposition ne remplace pas vos contributions réelles. Durée indicative : 12 à 15 minutes avec démo, à ajuster à la consigne du professeur.

## Diapositive 1 : Traçabilité et licences des générations
Intervenante 1

Nous présentons K2. Notre objectif est de savoir quels modèles, sources et transformations ont contribué à un contenu, puis de vérifier des contraintes déclarées. Les contenus sont simulés : nous évaluons la chaîne de traçabilité, pas la qualité d’un modèle génératif.

## Diapositive 2 : Le besoin de traçabilité
Intervenante 1

Une image ou un texte seul ne raconte pas sa fabrication. Nous attachons donc un manifeste à chaque artefact. Le programme peut expliquer une alerte, par exemple un usage commercial incompatible avec une restriction définie dans notre modèle pédagogique.

## Diapositive 3 : Architecture du démonstrateur
Intervenante 1

Le module pipelines construit des couples contenu-manifeste. L’injecteur ajoute des défauts connus. Le vérificateur reçoit le manifeste, le contenu et le registre. L’évaluation compare les règles détectées à la vérité terrain. Les mêmes résultats alimentent l’interface HTML.

## Diapositive 4 : Le manifeste JSON
Intervenante 1

JSON donne une structure lisible par une machine. L’empreinte est calculée à partir du contenu. Si le contenu change sans mise à jour du manifeste, le contrôle le détecte. Une empreinte ne prouve pas qui a écrit le manifeste et ne garantit pas la véracité des métadonnées.

## Diapositive 5 : Trois pipelines média simulés
Intervenante 1

Les trois pipelines enregistrent leurs modèles et leurs transformations. L’audio pointe vers le manifeste du texte qui le précède. Les fichiers image et audio sont des octets synthétiques, pas de véritables fichiers PNG ou WAV. Ce choix rend la démonstration gratuite et déterministe, mais limite son réalisme.

## Diapositive 6 : Huit règles explicables
Intervenante 2

Nous vérifions d’abord que les objets et leurs champs ont les bons types. Si cette étape échoue, nous retournons une alerte R1 et nous suspendons les règles métier. Les règles de licence sont des conventions simplifiées du projet. La règle SA est une politique du démonstrateur, pas une conclusion juridique automatique sur toute génération IA.

## Diapositive 7 : Protocole d’évaluation
Intervenante 2

Les données sont entièrement synthétiques. La baseline est volontairement simple : elle repère des mots-clés de licence sans comprendre le contexte. Nous mesurons les détections, les fausses alertes et le diagnostic exact. La même modélisation sert à construire les défauts et les règles : un excellent score ne généralise donc pas au monde réel.

## Diapositive 8 : Détection sur le corpus principal
Intervenante 2

La baseline repère 55 pour cent des artefacts fautifs selon la métrique du projet. La v2 détecte tous les défauts prévus. La micro-précision et le micro-rappel de la v2 valent aussi 100 pour cent sur ce jeu. Ce résultat valide notre implémentation dans le cadre des cas construits, pas une conformité générale.

## Diapositive 9 : Robustesse des métadonnées
Intervenante 2

La v1 comparait les auteurs à l’identique. Des variations de casse et de séparateurs provoquaient des alertes injustifiées. La normalisation résout ces cas construits. Elle peut cependant fusionner des noms distincts : un identifiant stable serait préférable. Les 120 exemples ne couvrent pas toutes les erreurs réelles.

## Diapositive 10 : Corrections après audit
Intervenante 1

L’audit a trouvé deux défauts hors du corpus initial. Nous avons ajouté une validation de structure explicite et douze tests. Les anciens tests continuent de passer. Nous avons relancé la campagne : les résultats initiaux sont conservés. Il faut être capable de montrer ces deux nouveaux cas en direct.

## Diapositive 11 : Démonstration en direct
Intervenante 2

Nous commençons dans un environnement préparé à partir de requirements.txt. Dans l’interface, nous choisissons une alerte de licence puis une erreur d’intégrité. Nous lançons ensuite la démo de structure et les tests. En cas de souci technique, les exports et le notebook fournissent le plan B hors ligne.

## Diapositive 12 : Limites et poursuite du projet
Ensemble

Le MVP produit une traçabilité consultable et des alertes explicables sur des cas maîtrisés. Nous ne revendiquons ni une validation juridique ni un système complet C2PA. L’attribution de K2 doit être confirmée. Le rendu public doit montrer nos contributions réelles et déclarer l’assistance IA. La répartition proposée pour l’oral ne prouve pas un historique de développement.

## Répétition
Chacune doit exécuter la démo et les tests, puis expliquer le manifeste. Choisir un cas R3 et un cas R7 dans l'audit HTML. Modifier une métadonnée et prédire l'alerte avant exécution.

## Réponses à comprendre
Pourquoi 100 % ? Les violations sont construites avec le même modèle que le vérificateur. Cela ne prouve pas une performance universelle.
Pourquoi pas une vraie image ? La simulation isole la traçabilité. Elle limite la démonstration et doit être annoncée.
Hash ou signature ? Le hash détecte une incohérence entre des octets et une empreinte. Une signature ajoute un mécanisme d'authentification de l'émetteur.
Que corrige validate_manifest ? La présence de métadonnées imbriquées et leurs types avant d'évaluer les règles.
Pourquoi le prompt sans empreinte est R1 ? Il manque une donnée requise. R7 compare des empreintes présentes aux octets correspondants.
