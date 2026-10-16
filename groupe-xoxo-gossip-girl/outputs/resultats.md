# Résultats de la campagne (graine 42)

Corpus : 290 générations — 150 conformes, 140 avec violations injectées (dont 20 à double violation).

## Vue d'ensemble

| Indicateur | Baseline naïve | Vérificateur v1 | Vérificateur v2 |
|---|---|---|---|
| Violations détectées | 55.0 % | 100.0 % | 100.0 % |
| Fausses alertes sur conformes | 74.7 % | 0.0 % | 0.0 % |
| Diagnostic exact (bonnes règles) | 23.1 % | 100.0 % | 100.0 % |
| Précision (micro) | 24.7 % | 100.0 % | 100.0 % |
| Rappel (micro) | 59.4 % | 100.0 % | 100.0 % |
| F1 (micro) | 34.9 % | 100.0 % | 100.0 % |

## Par règle

| Règle | Description | Baseline P / R | Vérificateur v2 P / R | TP | FP | FN |
|---|---|---|---|---|---|---|
| R1 | Structure de métadonnées absente, incomplète ou invalide | 100.0 % / 100.0 % | 100.0 % / 100.0 % | 15 | 0 | 0 |
| R2 | Licence non reconnue | 18.8 % / 100.0 % | 100.0 % / 100.0 % | 15 | 0 | 0 |
| R3 | Clause non commerciale (NC) violée | 29.0 % / 100.0 % | 100.0 % / 100.0 % | 27 | 0 | 0 |
| R4 | Œuvre « pas de modification » (ND) transformée | 100.0 % / 100.0 % | 100.0 % / 100.0 % | 23 | 0 | 0 |
| R5 | Share-alike (SA) non respecté par la licence de sortie | 8.6 % / 100.0 % | 100.0 % / 100.0 % | 15 | 0 | 0 |
| R6 | Attribution d'un auteur manquante | n/a / 0.0 % | 100.0 % / 100.0 % | 25 | 0 | 0 |
| R7 | Empreinte (hash) du contenu ou du prompt incorrecte | n/a / 0.0 % | 100.0 % / 100.0 % | 25 | 0 | 0 |
| R8 | Manifeste parent introuvable dans le registre | n/a / 0.0 % | 100.0 % / 100.0 % | 15 | 0 | 0 |

n/a : la baseline ne produit aucune alerte pour cette règle (précision non définie).

## Robustesse (120 manifestes légaux, métadonnées « sales »)

| Vérificateur | Faux positifs | Règles en cause |
|---|---|---|
| baseline naïve | 115 / 120 (95.8 %) | R2 ×96, R3 ×48, R5 ×64 |
| vérificateur v1 (strict) | 103 / 120 (85.8 %) | R6 ×103 |
| vérificateur v2 (normalisé) | 0 / 120 (0.0 %) | — |

## Couverture des métadonnées

- Moyenne sur tout le corpus : 99.8 %
- Moyenne sur les manifestes conformes : 100.0 %
- Minimum : 94.4 %

## Reproductibilité

- Export, exécution 1 : `ba08ace25149344cafb975eefecef58f33836dd1ff6cf6b1d88cbc13b1419f8d`
- Export, exécution 2 : `ba08ace25149344cafb975eefecef58f33836dd1ff6cf6b1d88cbc13b1419f8d`
- Identiques : **oui**
- Autre graine : `2fdcbd9b764e119442e63b41bdb9aa4eb8c3abe18638e6cc7d79c6e85f40b6c3` (différent : oui)
