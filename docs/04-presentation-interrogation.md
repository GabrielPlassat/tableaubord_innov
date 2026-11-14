# Innovation Radar v2 – Présentation et interrogation du tableau de bord

*Annexe A du cahier des charges (L5). Version du 14 novembre 2026. Les points ouverts de la section 5 sont tranchés dans L5, chapitre 6 ; les modules renvoyés en v3 sont listés dans L5, section 6.2.*

---

## 1. Principes généraux

### 1.1 Lire avant de chercher
Le tableau de bord n'est pas un fil d'actualité : il montre **ce qui bouge dans les structures**. Chaque écran doit répondre à la question « qu'est-ce qui a changé, et à quel niveau de profondeur ? ».

### 1.2 Trois niveaux de zoom, identiques partout
1. **Vue d'ensemble** (cockpit, ou en-tête d'un module) : ce qui a bougé.
2. **Vue module** : une carte, une courbe, une matrice, un nuage de bulles.
3. **Fiche objet** : tension, zone, technologie, mutation, zone de précipitation, tendance, cas, hypothèse. Elle se termine toujours par la **liste des sources**.

**Règle de traçabilité :** depuis n'importe quel élément affiché, on peut remonter en deux clics aux articles qui le justifient.

### 1.3 Grammaire visuelle commune

| Élément | Codage visuel |
|---|---|
| Lentille (7) | Une couleur par lentille, la même dans tous les modules |
| Niveau d'iceberg | Pictogramme à 4 niveaux : ● événement · ▲ tendance · ■ structure · ◆ modèle mental |
| Mouvement | Flèche : direction = sens ; longueur = vitesse ; flèche double = accélération |
| Confiance | Trait plein = forte, pointillé = moyenne, grisé = faible ou candidat |
| Zone géographique | Un code court et une couleur neutre par zone (codes de L1, section 7.1) |
| Statut | Badge : candidat / observé / validé / archivé |
| Origine de l'information | Badge « base » ou « web élargi » |

### 1.4 Commandes globales, présentes sur tous les écrans
- **Barre de filtres :** zone, lentille, axe de tension, horizon de temps, niveau d'iceberg, aire culturelle et langue des sources, niveau de confiance.
- **Curseur de temps :** mode « comparer » (aujourd'hui vs il y a 3 mois, 1 an, 3 ans), à partir des photographies mensuelles.
- **Panneau assistant** (à droite, repliable) : voir la section 4.
- **Bouton « Suivre »** sur chaque objet.
- **Bouton « Annoter »** sur chaque objet.

### 1.5 Contraintes techniques de présentation
- Une application Streamlit en plusieurs pages : une page par module, plus l'accueil.
- Les graphiques interactifs avec Plotly, comme en v1 ; la carte avec une bibliothèque cartographique compatible Streamlit.
- **L'affichage ne lance aucune collecte et aucun appel coûteux.** Il lit la base déjà enrichie. Seuls l'assistant et les demandes de dossiers appellent un modèle.
- Le thème sombre de la v1 est conservé, ainsi que les CSV modifiables depuis GitHub pour les référentiels (sources, personnes).

---

## 2. Le cockpit (page d'accueil)

**Objectif :** une lecture complète en 5 minutes, chaque semaine.

| Zone de l'écran | Contenu | Interaction |
|---|---|---|
| En-tête | Date de la dernière mise à jour, nombre d'articles traités, nombre de sources actives, **jauge de diversité** des aires culturelles | Clic sur la jauge → module Miroir |
| **Ce qui a bougé cette semaine** | 5 cartes au plus, triées par profondeur (structures et modèles mentaux d'abord), avec lentille, zone, pictogramme d'iceberg et une phrase | Clic → fiche ; bouton « Pourquoi c'est important ? » → assistant |
| **Baromètre des tensions (mini)** | Une ligne par axe validé, avec une mini-courbe sur 12 mois et la zone qui a le plus bougé. Un compteur des tensions candidates en attente. | Clic → module Tensions |
| **Précipitations en approche** | Les 3 bulles les plus proches du coin « imminent », avec leur trajectoire | Clic → fiche précipitation |
| **Horloge** | Les technologies qui ont changé de phase ou de maturité, et la zone où ça s'est passé | Clic → frise de la techno |
| **Matrice de puissance (mini)** | Les cases de la matrice qui ont changé de tendance ce trimestre | Clic → fiche zone |
| **Question directrice de la semaine** | Une des 14 questions permanentes, avec l'état actuel de la réponse en 3 phrases | Bouton « Approfondir » → demande de dossier |
| **Synthèse** | Un lien vers la synthèse hebdomadaire et vers le dernier « grand recul » mensuel | – |
| **Mes sujets suivis** | Les sujets épinglés qui ont bougé | Clic → objet |
| **File de validation** | Les 10 décisions de la semaine préparées par le Curateur (L3, A2) | Valider, observer, rejeter |

---

## 3. Les modules

### 3.1 Carte du monde à couches (v2 partielle)
- **Couches activables :** événements géolocalisés (couleur = lentille) ; infrastructures (câbles sous-marins, ports, mines de minerais critiques, data centers, gazoducs) ; flux commerciaux et monétaires en arcs ; fond Todd (structures familiales) ; coloration des pays par dimension de la matrice de puissance ; position des pays sur un axe de tension choisi. **En v2 : seules les deux dernières.**
- **Interactions :** survol → résumé ; clic sur un pays → fiche zone ; clic sur un événement → fiche signal.

### 3.2 Baromètre des tensions
- **Vue axes :** pour chaque axe validé, une barre horizontale entre ses deux pôles. Chaque zone y est un point, avec une flèche indiquant son déplacement sur la période. Un indice d'intensité du débat est affiché à côté de l'axe.
- **Vue tableau croisé** (v3) : une matrice zones × axes, avec la position (couleur entre les deux pôles) et l'intensité du débat (taille du point).
- **Vue tensions émergentes :** la liste des axes candidats, chacun avec les deux pôles proposés, le nombre d'occurrences, les aires culturelles où il apparaît et 5 extraits de preuve. Actions : valider, renommer, fusionner, scinder, rejeter.
- **Fiche tension :** définition des pôles, historique des positions, preuves côté A et côté B, mutations et précipitations liées, lecture par les auteurs de référence.
- **Cycle de vie d'un axe :** candidat → observé → validé → archivé. Seul Gabriel fait passer un axe au statut « validé ».

### 3.3 Zones de précipitation
- **Vue principale :** un nuage de bulles.
  - En horizontal, la maturité de l'offre (O0 à O5) ; en vertical, la formulation du besoin (B0 à B5).
  - Taille = enjeu (population, marché, impact écologique) ; couleur = lentille.
  - Le coin en haut à droite est marqué « précipitation imminente ».
  - Chaque bulle laisse une **traînée** qui montre sa trajectoire sur 6 mois (24 mois en v3).
- **Fiche précipitation :** signes d'offre ; signes de besoin ; **catalyseur attendu** ; obstacles ; horizon estimé ; zones où la rencontre a lieu en premier ; risque de rebond ; hypothèse associée dans le journal.
- **Filtres spécifiques :** horizon, zone, lentille, niveau de confiance.

### 3.4 Horloge des technologies
- **Vue Gartner par zone :** chaque technologie a **un point par zone** sur la courbe des attentes, reliés par un trait fin, ce qui rend les décalages visibles.
- **Tableau attentes × adoption :** fait ressortir les mutations silencieuses et les bulles possibles (L1, section 6.2).
- **Vue classes de lenteur** (v3) : des couloirs horizontaux ; pour chaque technologie, une barre « durée typique » et une barre « durée observée ».
- **Frise d'une technologie** (v3 détaillée) : historique de sa maturité par zone, événements clés, courbe de coût, acteurs, publications, passerelles.
- **Alertes :** changement de phase, accélération inhabituelle, apparition dans un nouveau domaine.

### 3.5 Matrice de puissance et forces / faiblesses (SWOT) des zones
- **Vue matrice :** un tableau zones × 13 dimensions (L1, section 8.1). Chaque case porte deux notes (autonomie, levier), une flèche par note et un indice de confiance. Pas de total.
- **Comparateur** (v3) : un radar qui superpose 2 ou 3 zones.
- **Fiche zone :** SWOT en 4 cases, chaque point sourcé ; dépendances ; indicateurs monétaires ; profil de société (Todd, Fourquet ou équivalents locaux) ; positions sur les axes de tension ; mutations et précipitations en cours ; sources dominantes, pour voir **comment la zone parle d'elle-même**.
- **Mise à jour trimestrielle.** Les changements sont signalés sur le cockpit.

### 3.6 Tendances et signaux faibles
- **Cartes de tendance :** niveau d'iceberg, vitesse (accélère, stable, ralentit), date de première apparition, aires où le sujet est vu, signaux d'origine.
- **Vue rivière** (v3) : les thèmes dans le temps, l'épaisseur suivant leur poids.
- **Promotion :** quand des signaux s'agrègent en tendance ou qu'une tendance devient une mutation, la carte l'indique.

### 3.7 Mutations
- **Galerie de fiches-récits.** Chacune a une frise « de… vers… », ses moteurs, ses freins, où elle est la plus avancée, sa vitesse, ses gagnants et perdants, les tensions qu'elle déplace, son levier de Meadows et les signaux à surveiller.
- **Liens** vers les tensions, technologies, zones et précipitations associées.

### 3.8 Passerelles (graphe de connaissances) – v3
- **Réseau** qui relie technologies, matériaux, secteurs et acteurs. Les **nouveaux liens** du mois sont en surbrillance. Les relations sont enregistrées dès la v2.

### 3.9 Monnaies et richesses – v3
- **Séries temporelles :** réserves de change par devise, or des banques centrales, paiements hors dollar, monnaies numériques de banque centrale, stablecoins.
- **Indicateurs de richesses non monétaires** (Noubel) : communs, contributions ouvertes, coopératives, indicateurs de confiance.
- Les séries sont collectées dès la v2.

### 3.10 Sociétés et modes de vie – v3
- **Séries lentes :** valeurs, démographie, consommation.
- **Couche Todd** et indicateurs d'archipellisation (Fourquet), plus leurs équivalents dans d'autres aires culturelles.
- **Signaux d'évolution des pratiques et des demandes.**

### 3.11 Galerie des solutions
- **Cartes de cas**, chacune avec sa jauge de levier Meadows (12 à 1), son risque de rebond (R0 à R3), sa transférabilité, sa zone et ses acteurs.
- **Tri et filtres**, et validation des cas par Gabriel.

### 3.12 Journal d'hypothèses
- **Tableau :** l'hypothèse, sa date, la confiance initiale, la confiance actuelle, les signaux pour, les signaux contre, son statut (en cours, confirmée, infirmée, abandonnée).
- **L'agent du grand recul propose chaque mois** de réviser les confiances.

### 3.13 Miroir des angles morts (Sprint 1)
- **Répartition des sources lues** par aire, langue et type ; évolution dans le temps.
- **Zones et sujets sous-représentés**, avec des suggestions de sources (v3).
- **Répartition des lectures de Gabriel :** les fiches ouvertes, par aire.

### 3.14 Synthèses
- **Pages de lecture :** synthèse hebdomadaire, « grand recul » mensuel, lectures croisées, dossiers.
- **Chaque affirmation** est reliée à ses sources, et la relecture de l'agent contradicteur est jointe.

---

## 4. Interroger le tableau de bord

### 4.1 Les six modes

| Mode | Fonctionnement | Modèle | Délai |
|---|---|---|---|
| **Naviguer** | Clics, filtres, comparaison, curseur de temps | Aucun | Immédiat |
| **Assistant contextuel** | Chat en panneau latéral ; il connaît l'écran, la fiche, les filtres et la période | Sonnet 5.5 par défaut, Opus sur demande | Quelques secondes |
| **Boutons de recul** | Questions prêtes, à un clic, sur toute fiche (liste dans L5, section 6.4) | Idem | Quelques secondes |
| **Demande de dossier** | Recherche approfondie en différé : la base, le web et des sources en langue d'origine. Le résultat est enregistré comme une fiche « Dossier ». En v2, lancée depuis GitHub Actions. | Fable 5.2 (ou Opus) | Quelques heures |
| **Suivre un sujet** | Alertes et section dédiée dans la synthèse hebdomadaire | Aucun, puis le modèle des synthèses | Continu |
| **Annoter, corriger** | Correction d'étiquettes, notes, validation des candidats, ajout d'hypothèses | Aucun | Immédiat |

### 4.2 Les boutons de recul

La liste définitive est dans L5, section 6.4.

### 4.3 Règles de l'assistant
1. **Par défaut, il répond à partir de la base**, en citant les fiches et les sources.
2. **Il dit explicitement** quand la base ne contient pas assez d'éléments, et propose le mode élargi ou un dossier.
3. **Mode élargi** (recherche web) : activé par un interrupteur ; les éléments trouvés sont marqués « web élargi » (v3 dans l'application).
4. **Chaque réponse indique** son niveau de confiance et la **répartition des aires culturelles** des sources citées.
5. **Il sépare** les faits, les interprétations et les hypothèses.
6. **Il propose** d'enregistrer une réponse utile comme note, hypothèse ou sujet suivi.

### 4.4 La demande de dossier
- **Formulaire simple :** la question, le périmètre (zones, période), la profondeur (standard ou approfondie), les sources à privilégier ou à exclure.
- **Plan type d'un dossier :**
  1. Résumé en 10 lignes.
  2. État des faits, sourcé.
  3. Lectures par aire culturelle.
  4. Tensions en jeu.
  5. Horloge et maturité.
  6. Précipitations possibles.
  7. Forces et faiblesses des zones concernées.
  8. Effets rebond.
  9. Ce qu'on ne sait pas.
  10. Signaux à surveiller.
  11. Sources.
- **Relecture** par l'agent contradicteur avant livraison.
- **Plafond :** 2 dossiers par mois (`config/budget.yaml`).

### 4.5 Comment l'assistant trouve l'information (principe)
1. La question est transformée en vecteur (embeddings via Albert).
2. Le système retrouve les fiches les plus proches par le sens, en tenant compte des filtres de l'écran.
3. Le modèle rédige la réponse **à partir de ces fiches seulement** (hors mode élargi), en les citant.

C'est le même principe que le POC wikixd-chat, appliqué à toute la base.
