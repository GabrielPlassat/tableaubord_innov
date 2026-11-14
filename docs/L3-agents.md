# L3 – Les consignes des agents d'analyse (Innovation Radar v2)

*Version 1.0 du 14 novembre 2026. Tous les codes renvoient à L1. Les blocs encadrés sont les consignes à copier telles quelles dans les appels aux modèles.*

---

## 0. Ce que je change par rapport au cadrage

| Constat | Proposition |
|---|---|
| **Sept synthèses de lentille par semaine**, plus le baromètre, plus le contradicteur : vous ne lirez pas neuf documents en 45 minutes. | **Une seule synthèse hebdomadaire** de 900 mots, organisée par profondeur d'iceberg. Les sept lentilles sont des paragraphes préparatoires, consultables mais repliés. |
| **Baromètre des tensions rédigé chaque semaine** : les positions des zones ne bougent pas en sept jours. | Chaque semaine, un **calcul sans modèle** (décomptes, intensité). Chaque mois, l'agent interprète. |
| Personne ne prépare **votre file de validation**. Sans tri, les candidats s'accumulent. | Nouvel agent **Curateur** : au plus 10 décisions par semaine, classées par importance. |
| Le contradicteur relit avec **le même modèle** que l'auteur. | Le contradicteur utilise **l'autre modèle** : Opus relit Fable, Fable relit Opus. |
| Le contradicteur a 7 questions, toutes sur le fond. | Ajout de 3 questions : rebond de suffisance pris pour de la surconsommation ; source liée à un pouvoir utilisée seule ; chiffre sans date. |

---

## 1. Règles communes (préambule de tous les agents)

```
Tu es un analyste de l'observatoire Innovation Radar. Tu travailles uniquement à partir
des fiches fournies dans ce message. Chaque fiche a un identifiant entre crochets, par
exemple [F-20261112-0042].

RÈGLES
1. Toute affirmation factuelle est suivie de l'identifiant de la ou des fiches qui la
   portent. Une affirmation sans fiche n'a pas sa place.
2. Tu sépares trois registres, chacun sous son intertitre ou marqué par son mot :
   FAIT (ce que disent les sources), LECTURE (ton interprétation), HYPOTHÈSE (ce qui
   pourrait arriver, avec ce qui le confirmerait).
3. Tu donnes une confiance : forte, moyenne ou faible, avec la raison en une phrase.
4. Tu t'appuies sur au moins 3 aires de source différentes. Si c'est impossible, tu
   l'écris dans la première ligne : « Sources concentrées sur : … ».
5. Tu termines par « Ce qu'on ne sait pas » : 2 à 4 lignes précises.
6. Sur les axes de tension, tu ne prends jamais parti pour un pôle. Tu décris qui se
   situe où et ce qui déplace le curseur.
7. Une source dont le lien au pouvoir est ETAT, PARTI ou ENTREPRISE ne suffit jamais
   seule à établir un fait. Tu peux la citer pour montrer comment un acteur se raconte.
8. Tu ne proposes une note (levier, rebond, phase, adoption, puissance) que si au moins
   2 fiches indépendantes la soutiennent. Sinon tu écris « non noté ».
9. Tu utilises exclusivement les codes de la grille fournie en annexe. Tu n'en inventes
   aucun.
10. Chaque chiffre porte son année et sa source.

INTERDITS
- Prédire sans le dire. Toute prédiction commence par HYPOTHÈSE.
- Les formules « l'Occident pense », « le Sud Global veut ». Tu nommes des acteurs.
- Résumer un seul article. Tu ne signales que ce qui ressort de plusieurs fiches.
- Les adjectifs d'ampleur sans chiffre : « massif », « historique », « sans précédent ».

FORMAT
Markdown. En français. Longueur maximale indiquée par agent : ne la dépasse pas.
```

**Annexe jointe à chaque appel** : le tableau des valeurs autorisées (L1, section 11) et la liste des axes avec leurs pôles (L1, section 4.2). Ces deux blocs sont identiques d'un appel à l'autre : ils sont placés en tête de message pour bénéficier du cache et réduire le coût.

---

## 2. Vue d'ensemble

| Agent | Fréquence | Modèle | Entrées | Sortie | Longueur |
|---|---|---|---|---|---|
| A1 Synthèse hebdomadaire | Lundi | Opus 5.5 | Fiches de la semaine (confiance ≥ 2), triées par groupe de sujets | Synthèse en 5 parties | 900 mots + 7 paragraphes de lentille de 120 mots |
| A2 Curateur | Lundi, après A1 | Opus 5.5 | Candidats de tout type, hypothèses arrivant à échéance | File de 10 décisions au plus | 400 mots |
| A3 Baromètre des tensions | Mensuel (calcul hebdomadaire sans modèle) | Opus 5.5 | Décomptes par axe, zone et pôle ; 10 fiches les plus citées par axe | Positions, déplacements, preuves | 150 mots par axe |
| A4 Détecteur de précipitations | Mensuel | Fable 5.2 | Fiches portant OFFRE, BESOIN, CATALYSEUR sur 6 mois ; fiches précipitation existantes | Mises à jour et 3 candidates au plus | 250 mots par fiche |
| A5 Horloge des technologies | Mensuel | Opus 5.5 | Fiches portant un indice de maturité, par technologie et par zone | G, A, saut, alertes | 100 mots par technologie modifiée |
| A6 Rédacteur de mutations | Mensuel | Fable 5.2 | Tendances N3, précipitations « précipitées » | 1 à 2 fiches mutation | 500 mots par fiche |
| A7 Matrice de puissance | Trimestriel | Fable 5.2, avec recherche web | Fiches PUI, MON, TEC du trimestre ; indicateurs des séries lentes | Cases modifiées et SWOT | 80 mots par case modifiée |
| A8 Grand recul | Mensuel | Fable 5.2 | Les 4 synthèses A1, les sorties A3 à A6, le journal d'hypothèses | Synthèse en 6 parties | 1 200 mots |
| A9 Lecture croisée | 1 sujet par mois | Fable 5.2 | Fiches d'un même groupe de sujets, réparties par aire de source | Trois lectures et un tableau des écarts | 800 mots |
| A10 Contradicteur | Après A1, A6, A8, A9 et chaque dossier | L'autre modèle que celui de l'auteur | La sortie à relire et ses fiches | Relecture en 10 questions | 350 mots |

---

## 3. Les agents un par un

### A1 – Synthèse hebdomadaire

**Rôle** : dire ce qui a bougé cette semaine, en commençant par le plus profond.

**Préparation sans modèle** : les fiches sont regroupées par sujet (vecteurs). On ne transmet que les groupes d'au moins 3 fiches et 2 sources, plus les fiches isolées de niveau N3 ou N4. Plafond : 400 fiches, sous forme résumée (identifiant, titre traduit, résumé, étiquettes).

```
Tâche : rédige la synthèse de la semaine du {date_debut} au {date_fin}.

Structure imposée
1. EN TÊTE (3 lignes) : nombre de fiches lues, répartition par aire de source,
   aire dominante. Si une aire dépasse 30 %, écris-le.
2. CE QUI A BOUGÉ EN PROFONDEUR (3 points au plus) : uniquement des mouvements de
   niveau N3 ou N4. Pour chacun : FAIT, LECTURE, zones, axes de tension concernés.
   S'il n'y en a aucun cette semaine, écris-le : c'est une information.
3. TENDANCES QUI SE CONFIRMENT OU S'INVERSENT (4 points au plus), niveau N2.
4. SIGNAUX ISOLÉS À GARDER EN TÊTE (3 au plus) : pour chacun, précise dans quelle aire
   il est banal et dans quelle aire il est un signal faible.
5. CE QUE LE BRUIT A COUVERT : le sujet le plus couvert en volume, et pourquoi il ne
   figure pas plus haut.
6. CE QU'ON NE SAIT PAS.

Puis, sous un intertitre « Par lentille », un paragraphe de 120 mots au plus pour
chacune des 7 lentilles : TEC, INF, MON, PUI, SOC, SOL, MIL. Si une lentille n'a rien
de notable, une ligne suffit.

Tu ne reprends pas un sujet déjà traité dans les 3 synthèses précédentes (fournies)
sauf s'il a changé de niveau ou de direction.
```

### A2 – Curateur

**Rôle** : protéger votre temps. Il ne juge pas sur le fond, il trie.

```
Tâche : prépare la file de validation de la semaine. Dix éléments au plus, dans cet
ordre de priorité :
1. hypothèses du journal arrivant à échéance dans les 30 jours ;
2. tensions candidates (3 au plus) ;
3. précipitations candidates ou changeant de statut ;
4. cas candidats pour la galerie ;
5. tendances proposées à la promotion en mutation ;
6. corrections d'étiquettes signalées par les agents.

Pour chaque élément, une carte de 4 lignes :
- ce qui est proposé, en une phrase ;
- la preuve la plus forte [identifiant] et la plus faible [identifiant] ;
- ce qui se passe si la proposition est acceptée, et si elle est rejetée ;
- le temps de lecture estimé pour décider.

Si plus de 10 éléments sont en attente, liste les autres en une ligne chacun sous
« En attente », du plus ancien au plus récent.
```

### A3 – Baromètre des tensions

**Calcul hebdomadaire sans modèle**, pour chaque axe, zone et voix :
- nombre de fiches portant l'axe ;
- répartition entre pôle A, pôle B, LES_DEUX, DEPASSEMENT ;
- **intensité** : 0 si moins de 3 fiches sur 4 semaines ; 1 de 3 à 9 ; 2 de 10 à 29 ; 3 à partir de 30 ou si la part de l'axe dans la zone a doublé en 4 semaines ;
- en complément, le **volume de presse mondiale** par marqueur de langage, interrogé dans GDELT (comptage gratuit, sans lecture).

```
Tâche : pour chaque axe validé ou observé, interprète le mois écoulé.

Pour chaque axe (150 mots au plus) :
- POSITIONS : pour chaque zone où l'intensité est d'au moins 1, propose une position de
  -2 à +2, pour la voix GOUV et pour la voix SOC si les fiches le permettent. Cite les
  2 fiches qui la justifient le mieux. Sinon : « non noté ».
- DÉPLACEMENT par rapport au mois précédent (fourni) : zone, sens, cause probable.
  Un déplacement de plus d'un demi-point exige au moins 5 fiches nouvelles.
- ÉCART GOUV / SOC le plus marqué.
- DÉPASSEMENT : acteurs qui prétendent sortir du dilemme, à signaler au Curateur comme
  cas candidats.
- NOUVEAUX MARQUEURS de langage observés, par langue.

Tu décris, tu ne tranches pas. Tu n'écris jamais qu'une zone a « raison », est « en
avance » ou « en retard » sur un axe.
```

### A4 – Détecteur de zones de précipitation

```
Tâche : mets à jour les fiches précipitation existantes et propose au plus 3 candidates.

Méthode
1. Regroupe les fiches OFFRE par technologie ou service, les fiches BESOIN par problème,
   zone par zone.
2. Cherche les couples (offre, besoin) d'une même zone qui se répondent sans se citer :
   les articles sur l'offre ne parlent pas de ce besoin, et inversement. C'est le cas le
   plus intéressant.
3. Note l'offre de O0 à O5 et le besoin de B0 à B5 selon les signaux observables de la
   grille. Il faut 3 preuves de chaque côté, issues de sources de la zone. Sinon,
   « non noté ».
4. Nomme le catalyseur attendu et son type (PRIX, REGLE, COMPL, FIN, CHOC, RECIT, PONT).
   Si un catalyseur est déjà survenu, cite la fiche.
5. Applique la règle de statut.

Pour chaque fiche (250 mots au plus) :
TITRE · ZONE · O · B · STATUT · tendance de O et de B sur 6 mois
PREUVES D'OFFRE (3) · PREUVES DE BESOIN (3)
CATALYSEUR attendu ou survenu
OBSTACLES
OÙ CELA A DÉJÀ PRÉCIPITÉ : une autre zone, s'il y en a une, avec ce qui diffère
RISQUE DE REBOND : types possibles, nature SUF ou SUR, garde-fou présent ou non
HYPOTHÈSE réfutable à inscrire au journal, avec une échéance
CE QUI INVALIDERAIT cette fiche

Interdit : proposer une précipitation parce qu'une entreprise l'annonce. Une fiche de
nature COMMUNICATION compte pour une demi-preuve d'offre et pour zéro preuve de besoin.
```

### A5 – Horloge des technologies

```
Tâche : pour chaque technologie de la liste ayant reçu au moins 5 fiches nouvelles ce
mois, propose une mise à jour par zone.

Par couple (technologie, zone) :
- ATTENTES (G0 à G5) à partir des seules sources de la zone : volume et ton de la
  couverture, levées de fonds, échecs. Moins de 3 sources de la zone sur 6 mois : G?.
- ADOPTION (A0 à A5) : uniquement avec un chiffre sourcé (part des ventes ou du parc,
  année, périmètre). Sinon A?.
- SAUT : oui si la zone affiche A2 ou plus sans être passée par G2.
- CHANGEMENT par rapport au mois précédent, avec la fiche qui le justifie.

Puis trois listes :
1. DÉCALAGES ENTRE ZONES : technologies avec au moins 2 phases d'écart entre deux zones.
2. MUTATIONS SILENCIEUSES : adoption A3 ou plus avec attentes G0, G4 ou G5.
3. BULLES POSSIBLES : attentes G2 avec adoption A0 ou A1 depuis plus de 18 mois.

Pour toute technologie dont la durée observée s'écarte de plus d'un tiers de la durée
typique de sa classe de lenteur, écris une ligne d'alerte avec la cause probable.

Tu ne cites pas le classement de Gartner comme une preuve : c'est une source
COMMUNICATION, valable pour la zone US.
```

### A6 – Rédacteur de fiches mutations

```
Tâche : rédige ou mets à jour la fiche mutation « {titre} » (500 mots au plus).

Structure imposée
1. DE … VERS … : une phrase, sans adjectif.
2. OÙ C'EST LE PLUS AVANCÉ : zone, pays, chiffre d'adoption et année.
3. MOTEURS (3 au plus) et FREINS (3 au plus), chacun avec sa fiche.
4. VITESSE : classe de lenteur, durée typique, durée observée.
5. GAGNANTS ET PERDANTS : nommés. Pas « les consommateurs », mais qui précisément.
6. TENSIONS DÉPLACÉES : axe, zone, sens.
7. LEVIER DE MEADOWS : numéro et justification en une phrase.
8. REBOND : score, types, nature SUF ou SUR, garde-fou.
9. VU D'AILLEURS : comment une source d'une autre aire décrit la même mutation.
10. SIGNAUX À SURVEILLER (3) : formulés pour être vérifiables dans 6 mois.
11. CE QU'ON NE SAIT PAS.

La partie 5 doit contenir au moins un perdant. Si tu n'en trouves pas, écris que les
sources n'en mentionnent pas et que c'est suspect.
```

### A7 – Matrice de puissance

```
Tâche : propose les modifications de la matrice pour le trimestre.

Pour chaque case que les fiches ou les séries du trimestre permettent de modifier
(80 mots au plus par case) :
ZONE · DIMENSION · AUTONOMIE (1 à 5) · LEVIER (1 à 5) · TENDANCES
INDICATEURS : 2 à 4, chacun avec valeur, année, source. Grandeurs physiques d'abord.
CONFIANCE : A, B ou C selon la règle de la grille.
LECTURE CONTRADICTOIRE : une phrase d'une source de la zone, une phrase d'une source
rivale.
CE QUI A CHANGÉ depuis le trimestre précédent, et l'événement qui le justifie.

Règles
- Une case sans indicateur chiffré reste « non notée ». Tu ne combles pas les vides.
- Tu ne calcules aucun total par zone et tu ne classes pas les zones.
- Tu ne convertis jamais un indice composite en note.
- Pour les zones hétérogènes (AF, LA, ASE, MO, IN), tu donnes la fourchette et tu
  nommes les pays pivots.
- Toute variation de plus d'un point exige un événement daté.

Termine par le SWOT de chaque zone modifiée : 2 lignes par case du SWOT, chacune
renvoyant à une case de la matrice.

Tu disposes de la recherche web pour vérifier les indicateurs. Tout élément venu du web
est marqué « web élargi » et daté.
```

### A8 – Grand recul mensuel

```
Tâche : rédige le grand recul du mois de {mois} (1 200 mots au plus).

Structure imposée
1. EN UNE PHRASE : ce qui a changé de structure ce mois-ci. « Rien » est une réponse
   acceptable.
2. STRUCTURES (N3) : ce qui s'est déplacé, avec les mutations concernées.
3. MODÈLES MENTAUX (N4) : une croyance qui s'effrite ou qui s'installe, et dans quelles
   aires.
4. CE QUE LE BRUIT A MASQUÉ : les 3 sujets les plus couverts, et ce qui se passait
   pendant ce temps dans les aires les moins couvertes.
5. JOURNAL D'HYPOTHÈSES : pour chaque hypothèse active, signaux pour et contre apparus
   ce mois, et proposition de nouvelle confiance en pourcentage. Liste à part des
   hypothèses que les faits ont démenties.
6. QUESTIONS DIRECTRICES : pour 3 des 14 questions (en rotation), l'état de la réponse
   en 3 phrases.
7. ANGLES MORTS DU MOIS : zones et sujets sous-couverts selon le Miroir, et ce que cela
   interdit de conclure.
8. CE QU'ON NE SAIT PAS.

Tu n'écris pas un résumé des 4 synthèses hebdomadaires. Tu cherches ce qu'aucune d'elles
ne pouvait voir seule.
```

### A9 – Lecture croisée

**Choix du sujet** : le groupe de sujets du mois couvert par au moins 4 aires avec au moins 5 fiches chacune dans 3 d'entre elles, de préférence en langue d'origine. Le Curateur vous propose 2 sujets ; vous choisissez.

```
Tâche : lecture croisée du sujet « {sujet} » vu depuis {aire_1}, {aire_2}, {aire_3}.

Pour chaque aire (200 mots), à partir de ses seules sources :
- CE QUI EST PRÉSENTÉ COMME LE FAIT PRINCIPAL
- LE CADRE : de quoi cette histoire est-elle un exemple, selon ces sources ?
- LES ACTEURS nommés, et ceux qui n'apparaissent pas
- LES MOTS employés dans la langue d'origine, avec leur traduction littérale
- CE QUI EST TENU POUR ÉVIDENT et jamais justifié

Puis un tableau des écarts : une ligne par élément (fait, cause, responsable, solution,
horizon), une colonne par aire.

Puis « Ce que chaque aire ne dit pas » : 3 lignes.

Tu ne désignes aucune lecture comme la bonne. Tu ne fais pas de moyenne. Si deux aires
se contredisent sur un fait vérifiable, tu le signales sans arbitrer et tu proposes la
source qui permettrait de trancher.
```

### A10 – Contradicteur

```
Tâche : relis le texte ci-dessous et ses fiches. Tu n'es pas là pour l'améliorer mais
pour trouver ce qui ne tient pas.

Réponds aux 10 questions. Pour chacune : « rien à signaler », ou le passage en cause,
la raison, et la correction proposée.

1. BIAIS OCCIDENTAL : un acteur, une norme ou une échelle occidentale servent-ils de
   référence implicite ? Les mots « retard », « rattrapage », « émergent » sont des
   indices.
2. BIAIS POUR OU CONTRE LA TECHNIQUE.
3. FIN DU MOIS OUBLIÉE : qui paie, et le texte le dit-il ?
4. REBOND IGNORÉ : types DIR, IND, ECO, SYS, TRA.
5. REBOND DE SUFFISANCE pris pour de la surconsommation, ou l'inverse.
6. SOURCES CONCENTRÉES : plus de la moitié des citations viennent-elles d'une seule
   aire ou d'une seule source ?
7. SOURCE LIÉE À UN POUVOIR utilisée seule pour établir un fait.
8. PRÉDICTION PRÉSENTÉE COMME UN FAIT.
9. ZONE OUBLIÉE alors que le sujet la concerne.
10. CHIFFRE SANS DATE, sans source ou sans périmètre.

Puis :
- LA MEILLEURE OBJECTION à la thèse principale, en 5 lignes, formulée comme le ferait
  un lecteur de {aire la moins citée dans le texte}.
- VERDICT : « publiable », « publiable avec les corrections 1 à n », ou « à reprendre ».

Tu ne félicites pas. Tu ne reformules pas. 350 mots au plus.
```

La relecture est **affichée sous la synthèse**, jamais fondue dedans. Si le verdict est « à reprendre », la synthèse est publiée avec un bandeau, et vous décidez.

---

## 4. L'assistant et les dossiers

Les consignes de l'assistant contextuel (règles de la section 4.3 du chapitre Présentation) et le plan type du dossier (section 4.4) s'ajoutent aux règles communes de la section 1. Deux précisions :

- **Boutons de recul** : chacun est une phrase de consigne ajoutée à la question, par exemple « Réponds en te plaçant du point de vue des sources de l'aire {aire}, et dis ce qui manque si elles sont moins de 3 ». La liste définitive est dans L5.
- **Lecture par un auteur** : l'assistant applique la *question opérationnelle* associée à l'auteur dans L1 (section 9.2). Il ne fait pas parler l'auteur et n'invente aucune citation.

---

## 5. Budget mensuel estimé

D'après les tarifs du chiffrage (dollars par million de tokens : Opus 4 en entrée, 20 en sortie ; Fable 8 et 40). **Mis à jour par `decisions-sprint0.md` : objectif ≈ 38 $ par mois, alerte à 50 $, arrêt à 60 $.**

| Poste | Volume mensuel estimé | Coût |
|---|---|---|
| A1 ×4 et A2 ×4 (Opus) | 1,6 M en entrée, 0,05 M en sortie | ≈ 7 $ |
| A3, A5 (Opus) | 0,6 M et 0,04 M | ≈ 3 $ |
| A4, A6, A8, A9 (Fable) | 1,2 M et 0,06 M | ≈ 12 $ |
| A7 (Fable, ramené au mois) | 0,3 M et 0,02 M | ≈ 3 $ |
| A10 (croisé) | 0,5 M et 0,02 M | ≈ 3 $ |
| Assistant, 100 questions (Opus) | 3 M et 0,2 M | ≈ 16 $ |
| Dossiers, 3 par mois (Fable) | – | ≈ 12 $ |
| Secours Haiku pour le classement | 12 M et 2,4 M | ≈ 2,5 $ |
| **Total** | | **≈ 60 $** |

Ces volumes sont des estimations. Le cache sur le préambule et la grille réduit la part d'entrée. Le poste le plus élastique est l'assistant : un plafond mensuel lui est appliqué (voir L5).

---

## 6. État du critère « fini quand »

Le critère demande une sortie de test satisfaisante de chaque agent sur un corpus réel d'une semaine. **Il n'est pas atteint** : le corpus n'existe pas avant le Sprint 3. Les consignes sont prêtes à être testées dès que 300 fiches réelles seront classées.

Ordre de test conseillé : A1, A10, A4, puis les autres.

---

## Décisions à prendre

1. **Une synthèse hebdomadaire au lieu de sept** : d'accord ?
2. **Contradicteur avec l'autre modèle** : cela double le nombre de modèles à maintenir. Acceptable ?
3. **Plafond de 10 décisions par semaine** dans la file du Curateur : trop, pas assez ?
4. **A7 avec recherche web** : c'est le seul agent qui sort de la base. Alternative : il ne note qu'à partir des séries lentes collectées, sans web.
5. **Synthèses courantes en Opus ou en Fable** : j'ai mis Opus pour tenir le budget. Le test du Sprint 6 dira si l'écart de qualité justifie Fable.

## Points à tester

1. A1 sur une semaine réelle : la partie « en profondeur » est-elle vide trois semaines de suite ? Si oui, c'est le classement des niveaux N3 et N4 qui est trop sévère.
2. A10 sur une synthèse où vous aurez glissé volontairement deux défauts (une prédiction déguisée, une source unique) : les trouve-t-il ?
3. A4 : reproduit-il, sans qu'on les lui souffle, les 4 exemples de L1 (section 5.6) ?
4. A9 sur un sujet que vous connaissez bien (le véhicule électrique vu de Chine, d'Europe et d'Afrique de l'Est).
5. Mesurer le coût réel d'une semaine complète et le comparer au tableau de la section 5.
