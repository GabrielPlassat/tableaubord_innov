# Sprint 0 – Décisions prises (14 novembre 2026)

Ce document complète L1, L2, L3 et L5 sans les réécrire. En cas d'écart, il l'emporte sur eux.

## Décisions validées par Gabriel

1. Les cinq hypothèses de départ :
   - périmètre généraliste, avec mobilité, énergie, industrie et numérique comme sujets suivis prioritaires ;
   - neutralité stricte sur les axes de tension, jugement critérié seulement dans la galerie des solutions ;
   - outil personnel, avec des sorties publiables plus tard ;
   - 30 à 45 minutes de validation par semaine ;
   - France incluse dans la zone EU, avec un zoom pour la lentille Sociétés.
2. La lentille **Milieux et ressources (MIL)** remplace le Miroir, qui devient une fonction calculée (L1, section 2).
3. La liste des axes : 11 axes validés (T01 à T11) et 3 observés (T12 à T14), avec un plafond de 12 axes validés (L1, section 4.2).
4. La v2 réduite à 9 écrans, avec renvoi en v3 du graphe des passerelles, des écrans Monnaies et Sociétés et des couches détaillées de la carte. Les données correspondantes sont collectées dès la v2 (L5, section 6.2).
5. Le dépôt GitHub est public (L5, décision 3).
6. **L'application Streamlit est privée** pour commencer. À vérifier au Sprint 1 : les conditions actuelles des applications privées sur Streamlit Community Cloud.
7. **Les fiches sur Hugging Face sont dans un jeu de données privé**, par cohérence avec l'application privée et par prudence sur les résumés d'articles de presse (proposition de Claude, à confirmer par Gabriel).
8. **Le budget API Claude** : alerte à 50 $ par mois, arrêt des appels non essentiels à 60 $. Le même plafond de 60 $ est fixé dans la console Anthropic. Ces valeurs remplacent celles de L5 (60 $ et 90 $).

## Ajustements pour tenir le budget de 50 $

L'estimation de L3 (section 5) était d'environ 60 $ par mois. Pour tenir sous 50 $ :

| Poste | Changement | Estimation |
|---|---|---|
| Assistant | Sonnet 5.5 par défaut, Opus sur demande ; 150 questions par mois au plus | ≈ 8 $ au lieu de 16 $ |
| Agents mensuels et trimestriels (A3 à A9) | Traitement différé (Batch), qui divise le prix par deux, sans changer de modèle | ≈ 9 $ au lieu de 18 $ |
| Dossiers | 2 par mois au plus | ≈ 8 $ au lieu de 12 $ |
| Synthèse hebdomadaire, curateur, contradicteur | Inchangés | ≈ 10 $ |
| Secours Haiku pour le classement | Inchangé | ≈ 2,5 $ |
| **Total estimé** | | **≈ 38 $**, soit une marge d'environ 12 $ |

À mesurer sur un mois réel au Sprint 6.

## Les clés et accès nécessaires

| Clé | Rôle | Où elle est rangée |
|---|---|---|
| Albert API | Classement, résumés, vecteurs | Secrets GitHub Actions ; secrets Streamlit (recherche de l'assistant) |
| API Anthropic | Agents d'analyse, assistant, dossiers. Distincte de l'abonnement Claude, facturée à l'usage | Secrets GitHub Actions ; secrets Streamlit |
| Hugging Face, en écriture | Enregistrer les fiches | Secrets GitHub Actions |
| Hugging Face, en lecture | Lire les fiches d'un jeu de données privé | Secrets Streamlit |
| GitHub, jeton limité au dépôt | Écrire les annotations depuis l'application | Secrets Streamlit |

## Test de la grille L1

- Feuille de test : 20 articles en 9 langues (artifact « Test de la grille L1 – 20 articles à classer »).
- Gabriel a classé les 4 premiers articles à la main, en moins de 3 minutes chacun, avec les mêmes résultats que la proposition de Claude. Il juge les 16 autres propositions justes.
- Il a hésité sur certaines étiquettes, et considère normal que plusieurs réponses soient possibles.
- **L1 est considérée comme validée pour lancer le Sprint 1.** Le test complet de la grille se fera avec le jeu de 100 articles du Sprint 3.

## Modification qui découle du test : les réponses acceptables

Plusieurs réponses peuvent être justes pour un même article. Le jeu de référence et la mesure d'accord en tiennent compte. Cette règle complète L2, section 6.

- Pour chaque article de référence, Gabriel indique **une réponse principale** et, s'il le souhaite, **une ou deux réponses acceptables** pour les étiquettes suivantes : lentille principale, iceberg, aire du sujet, axe de tension et pôle, précipitation, rebond.
- Un modèle est compté « d'accord » s'il donne la réponse principale ou une réponse acceptable.
- Deux taux sont suivis : l'accord **strict** (réponse principale seulement) et l'accord **large** (réponses acceptables comprises). Les seuils de L2, section 6.2, s'appliquent à l'accord large. L'accord strict sert à repérer les définitions à préciser.
- Une étiquette où l'écart entre les deux taux dépasse 20 points signale une définition floue, à préciser dans L1.
- La fiche classée par le modèle garde une seule valeur par étiquette. Les hésitations du modèle se lisent dans le champ `confiance`.

## Décisions encore ouvertes

Elles sont listées en fin de L2, L3 et L5. Aucune ne bloque le Sprint 1. Les plus structurantes, à trancher avant le Sprint 3 :

- L2 : qui étiquette le jeu de 100 articles ; volume de 8 000 à 10 000 fiches par mois ; 6 000 caractères lus par article.
- L3 : une synthèse hebdomadaire au lieu de sept ; un contradicteur sur l'autre modèle ; plafond de 10 décisions par semaine ; recherche web pour l'agent Matrice.
- L5 : évaluation des modèles avancée au Sprint 3 ; dossiers lancés depuis GitHub.
