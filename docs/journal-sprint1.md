# Journal du Sprint 1

Choix faits sans demander, faute de règle dans la conception (L5 : « l'option la plus simple »).

| # | Question | Choix | Pourquoi |
|---|---|---|---|
| 1 | Déplacer `app.py` et `data/` dans `v1/` dès maintenant ? | **Non.** La v1 reste à la racine, intacte. La v2 vit dans `v2/`. | Votre application en ligne pointe sur `app.py` : la déplacer la casserait à la fusion. Le déplacement se fera à la fin du Sprint 4, quand la v2 la remplacera. |
| 2 | Comment tester les flux ? | Un script (`scripts/audit_sources.py`) lancé par GitHub Actions, chaque lundi et à la demande. | L'environnement de développement n'a pas accès aux sites d'actualité ; GitHub Actions, si. |
| 3 | Doublons entre fichiers v1 | 7 flux présents dans deux fichiers ne sont gardés qu'une fois ; la remarque indique l'autre fichier. | Évite de compter deux fois une source dans le Miroir. |
| 4 | Pays des institutions européennes | Code `EU` dans la colonne `pays`. | Ce n'est pas un code ISO, mais il est sans ambiguïté. |
| 5 | Métadonnées des sources v1 (aire, lien au pouvoir) | Renseignées par Claude d'après le nom de la source. | À relire : une ligne par source, colonne `lien_pouvoir` surtout. |
| 6 | Sources non occidentales ajoutées (47) | Adresses de flux proposées d'après leur forme habituelle, **non vérifiées** ; l'audit dira lesquelles fonctionnent. | Impossible de les tester depuis l'environnement de développement. |
| 7 | Documents de conception dans le dépôt | Seules les parties utiles au code sont copiées (`config/`, `tests/`). Les documents complets restent dans le projet claude.ai ; `docs/README.md` explique comment les ajouter. | Les recopier entièrement aurait coûté cher, pour un simple glisser-déposer de votre côté. |
| 8 | Où mettre la règle « aucune aire au-dessus de 30 % » | Appliquée par le Miroir au registre, à titre indicatif. | L1 la mesure sur les articles ; elle ne pourra être vraiment appliquée qu'au Sprint 3. |

## Constat principal du Sprint 1

Même avec 47 sources non occidentales ajoutées, **l'Europe pèse 36 % des sources actives et les États-Unis 22 %** : le registre hérité de la v1 compte une trentaine de flux d'institutions européennes et américaines. La règle des 30 % n'est pas respectée sur le registre. Deux façons d'y remédier, à décider par Gabriel :

1. **désactiver** une partie des flux institutionnels redondants (Parlement européen, EUR-Lex, Commission : une quinzaine de flux) — ils pourront revenir par la lentille INF via une source agrégée ;
2. **plafonner à la collecte** (Sprint 2) le nombre d'articles retenus par aire et par jour, ce qui respecte la règle sur les articles sans toucher au registre.

La solution 2 est prévue de toute façon ; la 1 accélère et allège la collecte.

## Résultat du premier audit (14 novembre 2026, GitHub Actions)

| Statut | Sources | Dont ajouts Sprint 1 |
|---|---|---|
| OK | 67 | 33 |
| ERREUR (page introuvable, accès refusé, délai) | 46 | 5 |
| VIDE (la page n'est pas un flux lisible) | 17 | 3 |
| ENDORMI (rien depuis 90 jours) | 8 | 3 |

- **Près de la moitié des flux hérités de la v1 ne fonctionnent plus** : tous les flux de la Commission européenne, du Parlement européen et d'EUR-Lex, ceux de l'AIE, du FMI, de l'OCDE, de l'INSEE, et 13 des 25 personnes suivies. Cela explique en partie la pauvreté de la synthèse v1.
- Sur les **seuls flux qui fonctionnent**, aucune aire ne dépasse 30 % : US 27 %, EU 22 %, AF 9 %, ASE 7 %, LA 7 %, IN 6 %. La règle est respectée sur ce périmètre.
- **Aires encore faibles** : CN (1 %), JK (3 %), MO (3 %). La Chine est la priorité du prochain lot de sources : peu de médias chinois publient un flux lisible, il faudra sans doute passer par GDELT (Sprint 2) ou par des pages.
- Certaines erreurs 403 et 429 viennent de sites qui bloquent les robots ; d'autres flux ont simplement changé d'adresse. Le détail est dans `journal/audit_sources.csv` et dans la page Miroir.

## Premier test d'Albert (gpt-oss-120b, consigne v1, 14 novembre 2026)

Sur 20 articles, 8 n'ont pas pu être lus (sites qui bloquent Colab). Sur les 11 articles pertinents lus :

| Champ | Accord | Seuil L2 |
|---|---|---|
| Tri (passe 1, 20 articles) | 95 % | 95 % |
| JSON valide | 100 % | 98 % |
| Aire du sujet | 82 % | 90 % |
| Iceberg | 64 % | 65 % |
| Nature | 64 % | 80 % |
| Lentille principale | 55 % | 80 % |
| Axe | 27 % | 70 % |
| Précipitation | 18 % | 70 % |
| Rebond | 73 % | 70 % (trompeur : le modèle ne signale jamais de rebond) |

Biais du modèle : BESOIN presque partout ; presque jamais d'axe ; SOL et PUI employés trop largement ; jamais de rebond ; un code d'aire inventé (« AS »).
Réponse : consigne `passe2_v2.txt` (définitions resserrées, trois exemples, rappel des codes).
Enseignement pour le Sprint 2 : environ 40 % des sites refusent la lecture automatique ; la collecte doit d'abord utiliser le texte du flux RSS.

## Comparaison de 7 modèles (consigne v1, 17 articles lus dont 6 en PDF, 14 novembre 2026)

| Champ (seuil) | Mistral Small | Gemma 4 | DeepSeek | gpt-oss | Ministral | Haiku 5.5 | Opus 5.5 |
|---|---|---|---|---|---|---|---|
| Tri (95 %) | 90 | 90 | 90 | 90 | 90 | 90 | 85 |
| JSON valide (98 %) | 100 | 100 | 100 | 100 | 100 | **60** | 95 |
| Lentille (80 %) | **82** | 65 | 53 | 53 | **82** | 41 | 71 |
| Iceberg (65 %) | 65 | 71 | 65 | 71 | 41 | 35 | 65 |
| Aire (90 %) | 53 | 47 | 59 | 76 | 71 | 47 | **94** |
| Nature (80 %) | 65 | 71 | 71 | **82** | 47 | 41 | 65 |
| Axe (70 %) | 18 | 29 | 29 | 29 | 12 | 6 | 35 |
| Pôle (70 %) | 24 | 35 | 41 | 29 | 35 | 12 | 35 |
| Précipitation (70 %) | 29 | 24 | 24 | 24 | 24 | 12 | 24 |
| Rebond (70 %) | 59 | 65 | 53 | 65 | 59 | 47 | 59 |
| Codes d'aire inventés | 0 | 0 | 8 | 0 | 3 | 8 | 1 |
| Secondes / article | 9,9 | 16,6 | 5,8 | 64,6 | 3,7 | 16,3 | 21,2 |

Constats :
- Aucun modèle n'atteint les seuils sur axe, pôle et précipitation, Opus compris : le problème vient de la grille ou de la référence (une seule réponse « juste » pour des champs où plusieurs sont défendables), pas du modèle.
- Le tri plafonne à 90 % pour tous : probablement les mêmes 2 articles, à revérifier dans la référence.
- Haiku est pénalisé par 40 % de JSON invalides (réponse coupée ou entourée de balises) : scores non interprétables en l'état.
- Opus est le seul à atteindre le seuil sur l'aire.
Décisions proposées : Mistral Small pour la fiche de base (lentille, iceberg, nature), Ministral pour le tri ; axe, pôle, précipitation et rebond retirés du classement automatique et confiés aux agents (Opus, par lots), ou évalués en accord large sur le jeu de 100 articles.
