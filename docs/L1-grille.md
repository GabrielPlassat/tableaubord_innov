# L1 – La grille d'analyse intégrale (Innovation Radar v2)

*Version 1.0 du 14 novembre 2026, validée par Gabriel (voir `decisions-sprint0.md`). Document de référence : tout code cité ici est repris à l'identique dans L2, L3, L5 et dans `config/`.*

---

## 0. Ce qui a changé par rapport à l'ébauche, et pourquoi

| # | Constat | Décision |
|---|---|---|
| 1 | Il n'y avait **aucune lentille pour le monde physique** (eau, sols, climat, biodiversité). | Nouvelle lentille **Milieux et ressources** (MIL). |
| 2 | Le **Miroir des angles morts** n'est pas une lentille : c'est un calcul sur le corpus. | Le Miroir devient une **fonction transversale**. On reste à 7 lentilles, donc à 7 couleurs. |
| 3 | Noter **TRL, phase Gartner, levier de Meadows et rebond article par article** est illusoire : un article apporte un indice, pas un verdict. | Deux étages. L'**article** porte des étiquettes simples et des *indices*. Les **objets** (technologie, cas, mutation, précipitation) portent les notes fines, attribuées par les agents d'analyse à partir de plusieurs articles, puis validées par Gabriel. |
| 4 | Le cycle de **Gartner mesure des attentes**, pas une réalité ; seul, il reproduit le regard des marchés occidentaux. | On le garde, noté par zone, avec une **échelle d'adoption réelle**. L'écart entre les deux devient le signal principal. |
| 5 | **« Occident / Sud Global »** est à la fois une tension et une catégorie contestée. | Axe reformulé : « ordre à prétention universelle ↔ monde pluriel ». Les zones restent une dimension à part. |
| 6 | **« Marché ↔ communs »** mélange trois pôles : marché, État, communs. | Deux axes : marché ↔ État stratège ; propriété exclusive ↔ communs. |
| 7 | L'axe **Fourquet** est décrit pour l'Occident. Le terme du livre est « régime psychique » ([L'Éclaireur Fnac, 2 octobre 2026](https://leclaireur.fnac.com/article/694980-homo-occidentalis-jerome-fourquet-analyse-lhomme-moderne/)). | Axe généralisé « accomplissement de soi ↔ appartenances et devoirs », avec ses équivalents locaux. |
| 8 | La **matrice de puissance** oubliait l'alimentation et l'eau, la défense, la capacité d'exécution des États. | 13 dimensions (section 8). |
| 9 | L'**effet rebond** suppose des besoins déjà satisfaits. | Rebond **de suffisance** (rattrapage) distinct du rebond **de surconsommation** ; type **transfert** ajouté. |

---

## 1. Finalités : les 14 questions directrices

Le tableau de bord doit pouvoir répondre à chacune en permanence. Une question tourne chaque semaine sur le cockpit.

| Code | Question | Module qui répond |
|---|---|---|
| Q01 | Quelle mutation progresse en silence, avec une adoption réelle forte et peu de bruit ? | Horloge, Mutations |
| Q02 | Où une offre et un besoin vont-ils se rencontrer d'ici 2 à 5 ans ? | Précipitations |
| Q03 | Que voit-on depuis Lagos, Jakarta, Chengdu ou São Paulo qu'on ne voit pas depuis Paris ? | Lecture croisée, Miroir |
| Q04 | Où la tension écologie / niveau de vie est-elle dépassée sans rebond de surconsommation ? | Tensions, Galerie |
| Q05 | Quelle infrastructure invisible vient de changer de mains, de norme ou de tracé ? | Lentille INF |
| Q06 | Quelle richesse circule sans passer par le PIB ni par le dollar ? | Lentille MON |
| Q07 | Quelle technique passe d'un domaine à un autre ? | Passerelles |
| Q08 | Quelle zone gagne ou perd de l'autonomie, et de quoi dépend-elle désormais ? | Matrice de puissance |
| Q09 | Quel collectif agit sur les règles, les buts ou les paradigmes (leviers 5 à 1) ? | Galerie |
| Q10 | Quelle solution vantée déplace son coût ailleurs (autre région, autre matière, autre génération) ? | Galerie, Contradicteur |
| Q11 | Quelle technologie est en désillusion ici et en production là-bas ? | Horloge |
| Q12 | Quel mode de vie se défait ou se recompose, et quelle demande nouvelle en sort ? | Lentille SOC |
| Q13 | Quelle tension nouvelle apparaît dans plusieurs aires à la fois ? | Tensions émergentes |
| Q14 | Sur quoi me suis-je trompé ? | Journal d'hypothèses |

---

## 2. Les 7 lentilles et la fonction Miroir

Règle d'étiquetage : **une lentille principale obligatoire, une secondaire facultative**. La principale est celle sans laquelle l'article n'aurait pas été écrit.

| Code | Lentille | Dedans | Dehors | Exemples réels | Indicateurs de suivi |
|---|---|---|---|---|---|
| TEC | Technologies, matériaux, systèmes productifs | Procédés, coûts, usines, chaînes de valeur, brevets, passages d'un domaine à l'autre | Lancements de produits sans nouveauté, résultats trimestriels | Batteries LFP passant de l'automobile au stockage résidentiel au Pakistan ; motos électriques à batteries échangeables | Coût unitaire, capacité installée, part d'adoption, dépôts de brevets par zone |
| INF | Infrastructures invisibles | Normes, protocoles, paiements, câbles, cloud, identité numérique, registres, logistique, droit, cartes | L'infrastructure quand elle n'est qu'un décor de l'article | Étude de liaison Pix–TIPS entre banques centrales du Brésil et de la zone euro ; stations d'échange de batteries | Qui possède, qui opère, quelle norme, combien d'utilisateurs |
| MON | Monnaies et flux de richesses | Réserves, monnaies de règlement, dette, transferts de migrants, finance informelle, richesses non monétaires au sens de Noubel | Cours de bourse au jour le jour | Dollar à 56,7 % des réserves de change mondiales fin juin 2026 ([Central Banking](https://www.centralbanking.com/central-banks/economics/data/7977210/dollars-share-of-foreign-reserves-fell-slightly-in-q2-imf)) ; tontines, hawala, waqf | Parts de devises, or des banques centrales, volumes hors dollar, encours des paiements instantanés |
| PUI | Rapports de puissance | Dépendances, contrôles à l'exportation, alliances, sanctions, politique industrielle | Politique intérieure sans effet extérieur | Contrôles chinois sur les terres rares ; hilirisasi du nickel en Indonésie | Cases de la matrice de puissance |
| SOC | Sociétés et modes de vie | Famille, démographie, valeurs, travail, consommation, religion, santé mentale, habitat | Faits divers, sondages électoraux | « Homo occidentalis » (Fourquet et Rabinovitch) ; chômage long des jeunes diplômés coréens ; 躺平 en Chine | Fécondité, taille des ménages, enquêtes de valeurs, temps de travail |
| SOL | Solutions systémiques | Toute action décrite avec un résultat : politique, collectif, entreprise, pratique | Annonces et intentions sans mise en œuvre | Interdiction d'importer des véhicules thermiques en Éthiopie ; forêts communautaires au Népal | Levier de Meadows, rebond, transférabilité |
| MIL | Milieux et ressources | Eau, sols, climat, biodiversité, pollutions, santé environnementale, limites physiques | Météo du jour | Pompes solaires et nappes en Inde ; pollution des centrales captives du nickel à Sulawesi | Niveaux de nappes, émissions, surfaces, mortalité attribuable |

**Fonction Miroir (MIR)**, calculée et jamais étiquetée :
- part de chaque aire et de chaque langue dans les articles lus ;
- sujets couverts par une seule aire ;
- zones sans article depuis 30 jours ;
- répartition des lectures de Gabriel.

---

## 3. Les échelles de lecture

### 3.1 L'iceberg

| Code | Niveau | Test pratique | Exemple |
|---|---|---|---|
| N1 | Événement | L'article dit « hier, X a fait Y » | Yadea signe un accord avec Spiro |
| N2 | Tendance | Il donne une série, une répétition, un « de plus en plus » | Les importations de batteries du Pakistan triplent en un an |
| N3 | Structure | Il explique *ce qui produit* la tendance : règle, infrastructure, rapport de force, incitation | Les contrats de capacité font monter les tarifs à mesure que les clients quittent le réseau |
| N4 | Modèle mental | Il met au jour une croyance qui rend la structure évidente pour ses acteurs | « Le développement passe par la transformation locale des minerais, quel qu'en soit le coût » |

Règle : on note **le niveau le plus profond explicitement traité**, pas celui qu'on devine. Environ 80 % des articles seront N1 ou N2 : la profondeur vient de l'agrégation.

### 3.2 Les 12 leviers de Meadows, adaptés à la transition écologique

Numérotation de Meadows : 12 = le moins puissant, 1 = le plus puissant. Pour le classement automatique, quatre **familles** suffisent ; le numéro précis est attribué au niveau du cas.

| Famille | Levier | Formulation « transition » | Deux exemples réels |
|---|---|---|---|
| **FA Paramètres** | M12 Chiffres : taxes, subventions, seuils | Changer un prix ou une norme sans toucher au reste | Taxe carbone suédoise (1991) ; réforme des subventions aux carburants en Indonésie (2014-2015) |
| | M11 Stocks tampons | Créer des réserves qui amortissent | Batterie réseau de Hornsdale, Australie-Méridionale (2017) ; récupération d'eau de pluie obligatoire au Tamil Nadu (2003) |
| | M10 Structure physique | Bâtir ou retirer des réseaux | Réseau ferré à grande vitesse chinois, environ 50 000 km ; bus en site propre de Curitiba (1974) et Bogotá (2000) |
| **FB Boucles et information** | M9 Délais | Raccourcir le temps entre décision et effet | Zones d'accélération des renouvelables, directive européenne RED III (2023) ; durées de construction en série des infrastructures chinoises |
| | M8 Boucles correctrices | Faire payer ou plafonner ce qui dérape | Protocole de Montréal (1987) et amendement de Kigali (2016) ; paiements pour services environnementaux au Costa Rica (1997) |
| | M7 Boucles amplificatrices | Amorcer un cercle vertueux, freiner un cercle vicieux | Tarifs d'achat allemands (2000) puis échelle industrielle chinoise dans le solaire ; incitations norvégiennes au véhicule électrique |
| | M6 Flux d'information | Rendre visible ce qui ne l'était pas | Carte Blue Map de l'IPE de Ma Jun, Chine (2006) ; alertes satellitaires de déforestation DETER, Brésil (2004) |
| **FC Règles et pouvoir** | M5 Règles | Interdire, obliger, donner des droits | Interdiction des sacs plastique au Rwanda (2008) ; interdiction d'importer des véhicules thermiques en Éthiopie (2024) |
| | M4 Auto-organisation | Donner aux acteurs le pouvoir de changer la structure | Groupes d'usagers des forêts communautaires au Népal (loi de 1993) ; régénération naturelle assistée par les paysans au Niger |
| **FD Buts et paradigmes** | M3 Buts | Changer ce que le système cherche à maximiser | Bonheur national brut dans la Constitution du Bhoutan (2008) ; loi galloise sur les générations futures (2015) |
| | M2 Paradigme | Changer ce qui va de soi | Droits de la nature dans la Constitution de l'Équateur (2008) ; personnalité juridique du fleuve Whanganui, Nouvelle-Zélande (2017) |
| | M1 Dépasser les paradigmes | Tenir plusieurs visions du monde sans en absolutiser une | Etuaptmumk, « voir avec deux yeux », des Mi'kmaq au Canada ; évaluation IPBES des valeurs multiples de la nature (2022) |

**Mise en garde** : un levier élevé n'est pas « meilleur » en soi. L'Éthiopie (M5) fait passer les véhicules électriques de moins de 1 % à près de 6 % du parc en deux ans ([Daba Finance, février 2026](https://dabafinance.com/en/news/ethiopia-ev-import-ban-energy-sovereignty)), mais la question du réseau de recharge reste entière. On note toujours le levier **et** le rebond. Les dates des exemples sans lien sont à vérifier.

### 3.3 L'effet rebond

**Score**

| Code | Définition |
|---|---|
| R0 | Aucun rebond identifié, ou un garde-fou l'empêche (plafond, quota, norme sociale) |
| R1 | Rebond plausible mais limité : une petite part du gain est reprise |
| R2 | Rebond significatif : une large part du gain est reprise, ou la charge est transférée |
| R3 | Retour de flamme : l'effet net est négatif, ou le transfert est grave |
| R? | Non évalué. Valeur par défaut, à préférer à une note inventée |

**Types** (plusieurs possibles)

| Code | Type | Exemple réel |
|---|---|---|
| DIR | Direct : on utilise plus ce qui coûte moins | Pompes solaires à coût marginal nul et inquiétudes sur les nappes en Haryana ([Mongabay India](https://india.mongabay.com/2025/06/running-on-sunshine-but-running-out-of-water)) |
| IND | Indirect : l'argent économisé part ailleurs | Économies de carburant redépensées en transport aérien |
| ECO | Économique : toute l'économie s'ajuste | Gains d'efficacité des modèles d'IA suivis d'une hausse de la demande de calcul |
| SYS | Systémique : verrouillage, nouvelle norme sociale | Circulation alternée à Mexico (Hoy No Circula) suivie d'achats de secondes voitures |
| TRA | Transfert : la charge change de lieu, de matière, de payeur ou de génération | Nickel « pour batteries » en Indonésie alimenté par des centrales à charbon captives, environ 80 % des nouvelles capacités charbon du pays selon le CREA ([Kompas, 18 août 2026](https://lestari.kompas.com/read/2026/08/18/100300486/emisi-nox-industri-nikel-di-sulawesi-maluku-lampaui-sumber-polusi?page=2)) |

**Nature** : `SUF` suffisance (un besoin de base enfin couvert) ou `SUR` surconsommation. Un ménage pakistanais qui s'équipe de panneaux pour garder un ventilateur allumé relève de SUF.

**Garde-fou présent ?** oui / non / inconnu. Exemples : quota de véhicules à croissance nulle à Singapour (2018) ; preuve de stationnement exigée au Japon (1962) ; Cool Biz, norme vestimentaire japonaise qui réduit la climatisation (2005).

### 3.4 L'horizon de temps

`H1` moins de 2 ans · `H2` 2 à 10 ans · `H3` plus de 10 ans.

---

## 4. Les axes de tension

### 4.1 Principes

1. **On ne tranche jamais.** On décrit qui se situe où, et ce qui déplace le curseur.
2. **Un axe a deux pôles défendables.** Si l'un des deux est une caricature, l'axe est mal formulé.
3. **Deux voix par zone** quand les sources le permettent : `GOUV` (discours et actes des gouvernants) et `SOC` (opinion, mouvements, pratiques). En v2, une seule voix au départ (L5, section 6.2).
4. **Position** sur une échelle de −2 (pôle A dominant) à +2 (pôle B dominant). **Intensité** du débat de 0 à 3.
5. **Dépassement** : on signale à part les acteurs qui prétendent sortir du dilemme. C'est là que se trouvent les candidats à la galerie des solutions.
6. **Douze axes validés au maximum.** Au-delà, il faut fusionner ou archiver.

### 4.2 La liste : 11 axes validés, 3 axes observés

**Famille A – Finalités**

| Code | Pôle A ↔ Pôle B | Pourquoi cet axe | Marqueurs observables | Où il est le plus vif |
|---|---|---|---|---|
| T01 | **Urgence écologique ↔ urgence sociale et droit au développement** | Généralise « fin du monde / fin du mois ». À l'échelle mondiale, le pôle B s'appelle droit au développement. | fr : fin du mois, écologie punitive · en : just transition, greenlash, cost of living · zh : 先立后破, 发展权 · es : transición justa · hi : विकास बनाम पर्यावरण · id : hilirisasi | EU et US (société contre gouvernants), IN, ASE, AF (droit au développement) |
| T02 | **Croissance comme but ↔ autres finalités** | Porte sur la fin poursuivie, pas sur les moyens. | en : degrowth, beyond GDP, wellbeing economy · zh : 高质量发展, 生态文明 · ja : 脱成長 · es : buen vivir, decrecimiento · hi : विकसित भारत | EU et JK (débat ouvert), LA (buen vivir), CN et IN (croissance requalifiée, pas abandonnée) |
| T03 | **Solution par la technique ↔ sobriété et critique de la technique** | La technique résout-elle le problème ? | fr : low-tech, sobriété, technosolutionnisme · en : techno-optimism, e/acc · zh : 新质生产力, 科技向善 · hi : जुगाड़ · ja : Society 5.0 | US (pôle A), EU (clivé), CN (pôle A d'État), IN (frugalité pratique) |

**Famille B – Régimes économiques**

| Code | Pôle A ↔ Pôle B | Pourquoi cet axe | Marqueurs observables | Où il est le plus vif |
|---|---|---|---|---|
| T04 | **Coordination par le marché ↔ État stratège** | Le retour de la politique industrielle traverse toutes les zones. | en : industrial policy, state capitalism · zh : 国进民退, 举国体制 · es : Estado emprendedor · id : hilirisasi | US (bascule depuis 2022), EU, CN, ASE |
| T05 | **Propriété exclusive ↔ communs et ouverture** | Brevets, données, semences, logiciels, foncier. | en : open source, right to repair, IP waiver · fr : communs · zh : 开源, 山寨 · es : bienes comunes, procomún · digital public goods | IN (infrastructures numériques publiques), CN (modèles ouverts), EU, AF (semences, foncier) |
| T06 | **Performance et optimisation ↔ robustesse** | L'axe « vitesse / robustesse », nommé d'après ce qu'on sacrifie. | en : just-in-time vs just-in-case, de-risking, resilience · fr : robustesse · zh : 内卷 ↔ 韧性, 统筹发展和安全 · ja : 強靱化 | JK, EU, CN (sécurité contre efficacité), GLO (chaînes d'approvisionnement) |

**Famille C – Ordre du monde**

| Code | Pôle A ↔ Pôle B | Pourquoi cet axe | Marqueurs observables | Où il est le plus vif |
|---|---|---|---|---|
| T07 | **Ordre à prétention universelle ↔ monde pluriel et multi-alignement** | Reformule « Occident / Sud Global » : qui écrit les règles, et valent-elles pour tous ? | en : rules-based order, multipolarity, multi-alignment · zh : 人类命运共同体, 多极化 · ru : многополярный мир · hi : वसुधैव कुटुम्बकम् · pt : Sul Global · ar : الجنوب العالمي | IN, GO, ASE, LA (multi-alignement), RU et CN (pôle B revendiqué), EU et US (pôle A) |
| T08 | **Interdépendance ↔ souveraineté et relocalisation** | L'échelle à laquelle on veut maîtriser sa subsistance, monnaie comprise. | en : decoupling, friend-shoring · fr : autonomie stratégique · zh : 双循环, 自主可控, 去美元化 · hi : आत्मनिर्भर भारत · ru : импортозамещение · es : desdolarización | Toutes les zones ; écarts forts GOUV / entreprises |

**Famille D – Sociétés**

| Code | Pôle A ↔ Pôle B | Pourquoi cet axe | Marqueurs observables | Où il est le plus vif |
|---|---|---|---|---|
| T09 | **Accomplissement de soi ↔ appartenances et devoirs** | Généralise Fourquet et Rabinovitch (ancien régime psychique du devoir, nouveau régime de la jouissance et de la performance). Le pôle B n'est pas « le passé » : il est majoritaire dans bien des aires. | fr : régime psychique, développement personnel, archipel · en : self-care, loneliness epidemic, tradwife · zh : 躺平, 孝 · ja : 自分らしさ, おひとりさま · ko : N포세대, 비혼 | EU et US (pôle A dominant, contre-courants), JK et CN (bascule rapide), MO, IN, AF (pôle B fort, jeunesse urbaine en tension) |
| T10 | **Centres connectés ↔ périphéries** | L'archipellisation vue du monde : métropoles et classes mobiles contre campagnes, petites villes, travailleurs de l'informel. | fr : France périphérique · en : left behind, rural-urban divide · zh : 城乡差距, 户口, 乡村振兴 · hi : भारत बनाम इंडिया · pt : periferia, interior | CN, IN, US, EU, LA, AF |
| T11 | **Contrôle et sécurité ↔ libertés et vie privée** | Identité numérique, surveillance, modération, souveraineté des données. | en : surveillance, digital ID, data sovereignty · zh : 社会信用, 数据安全 · hi : आधार · ru : суверенный интернет | CN, IN, EU, US, GO, RU |

**Axes au statut « observé »**

| Code | Pôle A ↔ Pôle B | Pourquoi l'observer | Marqueurs |
|---|---|---|---|
| T12 | **Automatisation qui remplace ↔ travail humain préservé ou augmenté** | Distinct de T03 : la question est celle du travail et de la dignité. | en : AI layoffs, augmentation · zh : 机器换人 · ko : AI 일자리 |
| T13 | **Générations installées ↔ générations entrantes** | Dette, retraites, logement, climat, emploi. Mouvements de jeunesse depuis 2024 au Kenya, au Bangladesh, au Népal, à Madagascar, au Maroc. | en : Gen Z protests · ja : 世代間格差 · fr : conflit de générations |
| T14 | **Natalisme et famille comme institution ↔ émancipation et égalité de genre** | Croise Todd et la démographie. | en : pronatalism · ko : 4B (4비) · ja : 少子化 · zh : 三孩政策 |

**Écartés** : « pour / contre le capitalisme » (trop global ; T02, T04 et T05 en mesurent les composantes observables) ; « sécularisation ↔ retour du religieux » (à suivre d'abord comme marqueur de T07 et T09).

### 4.3 La règle de détection des nouvelles tensions

**Étape 1 – Collecte.** Lors du classement, si un article met en scène une opposition explicite qui ne correspond à aucun axe, le modèle remplit un champ `tension_libre` : deux pôles de cinq mots au plus chacun. Zéro ou une par article.

**Étape 2 – Regroupement.** Chaque semaine, les tensions libres des 8 dernières semaines sont regroupées par proximité de sens (vecteurs).

**Étape 3 – Seuils** (`config/seuils.yaml`). Un groupe devient **candidat** s'il réunit, sur 4 semaines glissantes :
- au moins 15 articles ;
- provenant d'au moins 8 sources distinctes ;
- d'au moins 3 aires culturelles de source, dont au moins une hors EU et US ;
- dans au moins 2 langues d'origine ;
- et si moins de 60 % de ses articles portent déjà un même axe existant. Au-dessus de 60 %, le groupe est proposé comme **nouveau marqueur** de cet axe, pas comme nouvel axe.

Ces seuils sont calibrés pour environ 8 000 à 10 000 articles classés par mois, à recaler après deux mois de données.

**Étape 4 – Cycle de vie.**

| Statut | Entrée | Qui décide | Ce que fait le système |
|---|---|---|---|
| Candidate | Seuils de l'étape 3 atteints | Automatique | Affiche les deux pôles proposés, le décompte, les aires, 5 extraits. Au plus 3 candidates par semaine sont soumises. |
| Observée | Gabriel clique « observer », ou la candidate tient 8 semaines | Gabriel, ou automatique | Code provisoire `TX…`, étiquetage et suivi, en gris |
| Validée | 3 mois d'observation, au moins 4 aires, des acteurs identifiables aux deux pôles | **Gabriel seul** | Code `T…` définitif, entrée au baromètre, rédaction de la fiche tension |
| Archivée | Intensité nulle 6 mois de suite, ou fusion | Gabriel, sur proposition | Historique conservé, réactivation possible |

Actions offertes à chaque étape : renommer, fusionner, scinder, rejeter. Un rejet est mémorisé pour ne pas reproposer le même groupe.

---

## 5. Les zones de précipitation

### 5.1 Définition

Une **zone de précipitation** est un couple (offre, besoin) **dans une zone géographique donnée**, où l'offre existe presque et où le besoin est presque formulé, de sorte qu'un seul événement peut déclencher la rencontre. La même précipitation se note séparément dans chaque zone. Le germe qui la déclenche est le **catalyseur**.

### 5.2 Échelle de maturité de l'offre

| Code | Niveau | Signaux observables |
|---|---|---|
| O0 | Idée | Publications, concepts, TRL 1 à 3 |
| O1 | Démonstrateur | Prototype, pilote subventionné, TRL 4 à 6 |
| O2 | Premiers clients | Ventes payantes, séries courtes, prix élevé, TRL 7 à 8 |
| O3 | Disponible en niche | Catalogue, quelques fournisseurs, service après-vente local rare |
| O4 | Industrialisée | Plusieurs fournisseurs, prix en baisse rapide, normes en cours, financement proposé |
| O5 | Abondante et bon marché | Produit banalisé, marché de l'occasion, réparateurs, plans ouverts |

### 5.3 Échelle de formulation du besoin

| Code | Niveau | Signaux observables |
|---|---|---|
| B0 | Latent | Le problème est subi et n'a pas de nom ; seuls des observateurs le décrivent |
| B1 | Symptômes | Plaintes, bricolages, contournements, détournements d'usage |
| B2 | Nommé | Le besoin a un mot, des communautés, des reportages |
| B3 | Revendiqué | Collectifs, pétitions, acheteurs pionniers, demande mesurée par enquête |
| B4 | Institutionnalisé | Réglementation, appels d'offres, subventions, normes d'usage |
| B5 | Solvable | Des payeurs, des budgets, des canaux d'achat et du crédit existent |

### 5.4 Le catalyseur

Événement ou décision extérieur au couple offre-besoin, qui supprime d'un coup le dernier obstacle.

| Code | Type | Exemple réel |
|---|---|---|
| PRIX | Seuil de parité ou choc de prix | Chute du prix des panneaux chinois et flambée des tarifs du réseau au Pakistan |
| REGLE | Norme, interdiction, homologation, commande publique | Interdiction d'importer des véhicules thermiques en Éthiopie |
| COMPL | Infrastructure complémentaire | Réseau de stations d'échange de batteries au Kenya |
| FIN | Financement accessible | Location de batterie et crédit adossé au numéro de téléphone |
| CHOC | Crise, pénurie, catastrophe | Tensions d'approvisionnement en carburant |
| RECIT | Légitimation par un récit, une figure, un événement | Une ville vitrine, un champion national |
| PONT | Acteur-pont : distributeur, plateforme, alliance inattendue | Accord Yadea–Spiro, avec le fabricant de téléphones Transsion au capital du fonds investisseur ([21世纪经济报道, 25 octobre 2026](https://cj.sina.com.cn/articles/view/1651428902/626ece2601901l0t2)) |

### 5.5 Statuts et règle de proximité

| Statut | Règle |
|---|---|
| Lointaine | O + B inférieur à 5 |
| En approche | O + B entre 5 et 6, et au moins un des deux en hausse sur 6 mois |
| Imminente | O ≥ 3 et B ≥ 3 et O + B ≥ 7 |
| En cours | Adoption mesurable (A2 ou plus, voir 6.2) et croissance rapide |
| Précipitée | Adoption A3 ou plus : l'objet bascule vers une fiche Mutation |
| Dissoute | Recul de O ou de B deux semestres de suite, ou substitution par autre chose |

Chaque fiche porte aussi : obstacles, horizon (H1 à H3), enjeu (population concernée, impact écologique), risque de rebond, hypothèse liée, et **au moins 3 preuves d'offre et 3 preuves de besoin provenant de sources de la zone**.

### 5.6 Quatre exemples notés (estimations à discuter)

| Précipitation | Zone | Offre | Besoin | Statut | Catalyseur | Rebond |
|---|---|---|---|---|---|---|
| Stockage par batteries chez les particuliers | IN (Pakistan) | O4 | B5 | En cours | REGLE : passage à la facturation nette en 2026, qui rend l'injection moins rentable ([The Friday Times, 7 octobre 2026](https://thefridaytimes.com/07-Oct-2026/pakistan-s-solar-boom-moving-faster-power-grid)) | R2 SYS : les charges fixes du réseau retombent sur ceux qui restent ([Dawn](https://www.dawn.com/news/1915999/pakistan-imports-328gw-of-solar-pv-modules-in-5-years)) |
| Moto-taxi électrique à batterie échangeable | AF (Kenya, Nigeria) | O4 | B4 | En cours | COMPL + FIN | R? ; risque social : véhicule verrouillé à distance en cas d'impayé, selon une tribune de [观察者网, 28 septembre 2026](https://www.guancha.cn/chenghongwei/2026_09_28_901171.shtml) |
| Paiements instantanés transfrontaliers en monnaie locale | LA, EU | O3 | B3 | Imminente | REGLE : accord entre banques centrales, après l'étude de faisabilité Pix–TIPS lancée en septembre 2026 ([Capital Aberto](https://capitalaberto.com.br/economia-e-financas/2026/10/pix-e-sistema-europeu-devem-reduzir-custos-de-pagamentos)) | R0 |
| Véhicules intermédiaires (vélis) en zones peu denses | EU (France) | O2 à O3 | B1 à B2 | En approche | REGLE ou commande publique (hypothèse) | R? |

---

## 6. L'horloge des technologies

Trois mesures par couple (technologie, zone), plus une classe de lenteur par technologie.

### 6.1 La phase d'attentes (Gartner), notée par zone

Gartner place lui-même les attentes en ordonnée de sa courbe : c'est un indicateur de discours.

| Code | Phase | Critères observables dans les sources **de la zone** |
|---|---|---|
| G0 | Absente | Pas de couverture locale |
| G1 | Déclencheur | Premières annonces, démonstrations, couverture en hausse depuis un niveau faible |
| G2 | Pic des attentes | Couverture maximale, levées de fonds, promesses chiffrées, peu de déploiements |
| G3 | Désillusion | Faillites, projets annulés, ton négatif, couverture en baisse |
| G4 | Éclaircissement | Retours d'expérience, deuxième génération, normes, couverture basse et factuelle |
| G5 | Productivité | Sujet devenu banal, traité en pages économie et non innovation |
| G? | Non noté | Moins de 3 sources de la zone sur 6 mois |

Attribut `saut` (oui / non) : la zone est passée directement à l'usage sans phase d'emballement.

### 6.2 L'adoption réelle, notée par zone

Part du marché pertinent dans la zone (ventes annuelles ou parc, à préciser dans la fiche).

| Code | Part | Lecture |
|---|---|---|
| A0 | Moins de 0,1 % | Inexistant |
| A1 | 0,1 à 1 % | Pionniers |
| A2 | 1 à 5 % | Amorçage |
| A3 | 5 à 25 % | Bascule engagée |
| A4 | 25 à 50 % | Diffusion de masse |
| A5 | Plus de 50 % | Nouvelle norme |
| A? | Pas de donnée chiffrée sourcée | |

**Les deux lectures croisées qui comptent :**
- attentes fortes (G2) et adoption faible (A0 ou A1) : bulle possible ;
- attentes faibles (G0, G4, G5) et adoption forte (A3 ou plus) : **mutation silencieuse**, réponse directe à Q01.

### 6.3 Le TRL

1 à 9, noté **au niveau mondial** (l'état de l'art), pas par zone. La zone est décrite par G et A.

### 6.4 Les classes de lenteur

Durée typique entre la première mise sur le marché et une diffusion de masse (A4). Ordres de grandeur issus de l'histoire des techniques (Grübler, Smil, Wilson), à affiner cas par cas.

| Code | Classe | Durée typique | Repères |
|---|---|---|---|
| C1 | Logiciel et services numériques | 2 à 7 ans | Messageries, paiements mobiles, assistants d'IA |
| C2 | Biens d'équipement des ménages | 10 à 20 ans | Smartphone, climatiseur ; un parc automobile se renouvelle en 15 à 20 ans |
| C3 | Matériaux et procédés industriels | 20 à 40 ans | Batterie lithium-ion : commercialisée en 1991, massive vers 2015-2020 |
| C4 | Énergie et grandes infrastructures | 30 à 70 ans | Chaque transition énergétique a pris un demi-siècle ou plus |
| C5 | Institutions, droit, normes | 10 à 50 ans | Très dispersé : une interdiction peut être immédiate, un régime de propriété séculaire |
| C6 | Valeurs et structures familiales | 50 à 100 ans et plus | Deux à quatre générations |

Règle : la **durée observée** dans une zone est comparée à la durée typique de la classe. Un écart de plus d'un tiers déclenche une alerte. Les techniques **granulaires** (petites unités produites en série) se diffusent plus vite que les grands ouvrages.

### 6.5 Les marqueurs de bascule

Valeurs du champ `indice_maturite` d'un article : `COUT` (baisse de coût chiffrée), `VOLUME` (ventes, capacités), `NORME` (standard, homologation), `MARCHE_PUBLIC` (première grande commande), `USINE` (capacité de production annoncée ou ouverte), `ECHEC` (faillite, abandon), `OCCASION` (marché de seconde main, réparation), `BREVET_PUBLI` (pic de brevets ou de publications).

---

## 7. Les zones et les aires culturelles

### 7.1 Les 12 zones et le code global

| Code | Zone | Contenu | Pays pivots |
|---|---|---|---|
| EU | Europe | UE, Royaume-Uni, AELE, Balkans, Ukraine | Allemagne, France (zoom), Pologne |
| US | Amérique du Nord | États-Unis, Canada | États-Unis |
| CN | Chine | Chine continentale, Hong Kong | – |
| JK | Asie de l'Est avancée | Japon, Corée du Sud, Taïwan | Japon, Corée du Sud |
| IN | Asie du Sud | Inde, Pakistan, Bangladesh, Sri Lanka, Népal | Inde |
| ASE | Asie du Sud-Est | Pays de l'ASEAN | Indonésie, Vietnam |
| RU | Russie et Eurasie | Russie, Biélorussie, Caucase, Asie centrale | Russie, Kazakhstan |
| GO | Golfe | Pays du Conseil de coopération du Golfe | Arabie saoudite, Émirats |
| MO | Moyen-Orient et Afrique du Nord hors Golfe | Turquie, Iran, Égypte, Maghreb, Levant, Israël | Turquie, Égypte |
| AF | Afrique subsaharienne | – | Nigeria, Kenya, Éthiopie, Afrique du Sud |
| LA | Amérique latine et Caraïbes | Mexique inclus | Brésil, Mexique |
| OC | Océanie et Pacifique | Australie, Nouvelle-Zélande, îles | Australie |
| GLO | Global | Sujet ou source sans ancrage (ONU, FMI, BRICS) | – |

Chaque objet porte aussi le **pays** (code ISO) quand il est connu (`config/zones_pays.csv`). Les zones hétérogènes (AF, LA, ASE, MO, IN) sont toujours notées avec leur dispersion.

### 7.2 Deux attributs géographiques par article, jamais confondus

- `aire_source` : où la source est **ancrée**. Reuters écrivant sur le Kenya reste US-EU.
- `aire_sujet` : de qui ou de quoi parle l'article. Plusieurs valeurs possibles.

Et un attribut d'ancrage de la source : `LOCAL`, `DIASPORA`, `CORRESPONDANT` (média étranger sur place), `INTERNATIONAL` (organisation multilatérale).

### 7.3 Le lien au pouvoir, noté de façon symétrique

Signaler seulement les « médias d'État » vise en pratique la Chine et la Russie et épargne la BBC, RFI, Voice of America ou les médias de milliardaires. Le registre note donc pour **toutes** les sources :

`ETAT`, `PARTI`, `GROUPE_PRIVE` (conglomérat ou grande fortune), `FONDATION_ONG`, `INSTITUTION` (organisation internationale, banque centrale), `ENTREPRISE` (communication d'entreprise), `INDEPENDANT`, `INCONNU`.

Un média lié à un pouvoir n'est pas exclu. Il est une **source primaire sur la manière dont ce pouvoir se raconte**, et ne peut pas être l'unique source d'un fait.

### 7.4 L'attribut de fond : structures familiales (Todd)

Valeurs indicatives, portées par le pays : nucléaire absolue, nucléaire égalitaire, souche, communautaire exogame, communautaire endogame, communautaire asymétrique, anomique, systèmes africains (à ne pas réduire à une case).

Mise en garde : typologie construite à partir de l'ethnographie européenne, au pouvoir explicatif contesté. **Couche d'hypothèse** affichable sur la carte, jamais explication seule.

---

## 8. La matrice de puissance et le SWOT des zones

### 8.1 Les 13 dimensions

| Code | Dimension | Ce qu'on mesure | Sources ouvertes à privilégier |
|---|---|---|---|
| P01 | Énergie | Autonomie, coût, part bas carbone, capacité d'équipement | Energy Institute Statistical Review, AIE, IRENA, Ember |
| P02 | Matières critiques | Extraction, **raffinage**, stocks, recyclage | AIE Global Critical Minerals Outlook, USGS |
| P03 | Alimentation et eau | Autosuffisance céréalière, stress hydrique, engrais | FAO (FAOSTAT, AQUASTAT), WRI Aqueduct |
| P04 | Capacités industrielles | Valeur ajoutée manufacturière, machines-outils, construction navale, montée en cadence | ONUDI, Comtrade |
| P05 | Science et technologie | Publications, brevets, semi-conducteurs, talents | OpenAlex, OMPI, Nature Index |
| P06 | Numérique et infrastructures invisibles | Cloud, câbles, paiements, identité, normes, modèles d'IA | UIT, TeleGeography, BRI, organismes de normalisation |
| P07 | Monnaie et finance | Rôle international de la monnaie, dette, profondeur des marchés, exposition aux sanctions | FMI (COFER), BRI, SWIFT RMB Tracker, Conseil mondial de l'or |
| P08 | Démographie et capital humain | Structure par âge, fécondité, éducation, migrations | ONU World Population Prospects, UNESCO |
| P09 | Cohésion sociale et confiance | Inégalités, confiance, conflictualité | World Inequality Database, World Values Survey, Afrobarometer, Latinobarómetro, Asian Barometer |
| P10 | Capacité d'État | Aptitude à planifier et à **exécuter** : délais de réalisation, recettes fiscales, continuité des politiques | FMI, délais réels de projets, rapports de cours des comptes |
| P11 | Sécurité et défense | Dépenses, base industrielle de défense, dépendances | SIPRI |
| P12 | Alliances, normes et influence | Accords, votes à l'ONU, présence dans les organismes de normalisation, portée des médias et des plateformes | Votes de l'Assemblée générale, ISO, UIT, OMC |
| P13 | Robustesse écologique | Exposition aux chocs climatiques, état des sols et de l'eau, capacité d'adaptation | GIEC, ND-GAIN, EM-DAT |

### 8.2 La méthode de notation

Chaque case (zone × dimension) contient **six éléments, sans score global** :

1. **Autonomie** de 1 à 5 (1 = dépendance critique à un fournisseur ; 5 = autosuffisance avec marges).
2. **Levier** de 1 à 5 (1 = personne ne dépend d'elle ; 5 = goulot mondial).
3. **Tendance** sur 3 ans : ↑, →, ↓, pour chacune des deux notes.
4. **Preuves** : 2 à 4 indicateurs avec valeur, année et source.
5. **Confiance** : `A` = au moins 2 indicateurs chiffrés de sources indépendantes, dont une internationale ou d'une autre aire ; `B` = un seul indicateur chiffré ou des sources d'une seule aire ; `C` = appréciation qualitative.
6. **Lecture contradictoire** : ce que dit la zone d'elle-même, ce qu'en dit un rival.

Cinq règles d'honnêteté :
- **Pas de note sans preuve.** Une case sans indicateur reste grise.
- **Les grandeurs physiques avant les indices composites.** Les indices composites (gouvernance, liberté économique, puissance douce) sont cités, jamais convertis en note.
- **Pas de total ni de classement général.**
- **La dispersion est affichée** pour les zones hétérogènes.
- **Toute variation de plus d'un point** entre deux trimestres cite l'événement qui la justifie.

### 8.3 Deux cases remplies à titre d'exemple

| Case | Autonomie | Levier | Tendance | Preuves | Confiance |
|---|---|---|---|---|---|
| P02 × CN | 4 | 5 | Levier → | Hors terres rares, la part du premier pays raffineur est passée de 70 % en 2023 à 72 % en 2025 ; la part chinoise dans le raffinage des terres rares a reculé de plus de 90 % en 2023 à 85 % en 2025 ([Mining Digital](https://miningdigital.com/news/iea-investment-in-critical-minerals-has-fallen-9) et [OGN](https://ognnews.com/ArticleTA/465215), d'après l'AIE, juillet 2026) | A |
| P07 × US | 5 | 5 | Levier ↓ lent | Dollar à 56,7 % des réserves de change fin juin 2026, euro à 20,6 % ; plus haut à 71,4 % en 2001 ([DaveManuel.com, d'après le FMI](https://www.davemanuel.com/dollar-share-of-world-reserves.php)). Lecture contradictoire : le FMI attribue une part des variations aux effets de change. | A |

### 8.4 Le SWOT d'une zone

Dérivé de la matrice, puis commenté :
- **Forces** : dimensions où autonomie ou levier ≥ 4.
- **Faiblesses** : dimensions où l'autonomie ≤ 2.
- **Opportunités** : précipitations « en approche » ou « imminentes » dans la zone ; tendances ↑.
- **Menaces** : dépendances à un fournisseur unique ; tendances ↓ ; dimension P13.

---

## 9. Désoccidentaliser la grille elle-même

### 9.1 Les concepts de la grille qui portent un biais occidental

| Concept | Le biais | Parade inscrite dans la grille |
|---|---|---|
| **Innovation** | Valorise la nouveauté et la rupture ; ignore l'entretien, la réparation, l'imitation, la tradition. | TEC et SOL acceptent la maintenance, le réemploi, la copie adaptée (山寨, jugaad). |
| **TRL et Gartner** | Trajet linéaire du laboratoire vers le marché ; ne voient pas les sauts d'étape. | Phase par zone, attribut `saut`, échelle d'adoption réelle. |
| **Signal faible** | Faible pour qui ? Ce qui est banal à Shenzhen est un signal faible à Paris. | Tout signal porte l'aire où il est faible et l'aire où il est courant. |
| **Iceberg, leviers de Meadows** | Pensée systémique née au MIT : suppose un ingénieur extérieur au système. | Levier M1 pris au sérieux ; cadres relationnels en contrepoids (9.2). |
| **Effet rebond** | Suppose la saturation des besoins. | Nature SUF ou SUR ; type TRA. |
| **Sud Global, Occident** | Catégories définies par l'Occident ; masquent les rapports de force Sud-Sud. | Douze zones ; axe T07 reformulé ; dépendances Chine–Afrique ou Golfe–Asie du Sud suivies comme les autres. |
| **Fin du monde / fin du mois** | Formule française de 2018. Pour des peuples autochtones, la fin du monde a déjà eu lieu (Krenak). | Axe T01 formulé en « droit au développement ». |
| **État-nation comme unité de puissance** | Ignore villes, diasporas, entreprises, réseaux religieux. | Le type Acteur inclut ces formes ; flux de diasporas suivis dans MON. |
| **Cohésion mesurée par la « confiance »** | La question des enquêtes ne signifie pas la même chose partout. | P09 note d'abord des faits et cite les baromètres régionaux. |
| **Richesses selon Noubel** | Cadre formulé depuis l'Occident. | Pratiques existantes en regard : tontines, hawala, waqf, zakat, gotong royong, minga, harambee. |
| **Fiabilité des sources** | Le label « média d'État » appliqué à sens unique. | Attribut `lien_pouvoir` symétrique (7.3). |
| **Structures familiales de Todd** | Typologie d'origine européenne. | Couche d'hypothèse, jamais explication seule. |

### 9.2 Les cadres non occidentaux en contrepoids

| Auteur de référence | Contrepoids | Concept utile | Question opérationnelle |
|---|---|---|---|
| Meadows | Yuk Hui (Hong Kong) | Cosmotechnique : toute technique porte une vision du monde | Quelle cosmologie cette technique suppose-t-elle, et qui ne la partage pas ? |
| Meadows | Alberto Acosta, Eduardo Gudynas (Andes) | Buen vivir, sumak kawsay | Le « but du système » peut-il être autre chose qu'un stock à faire croître ? |
| Meadows | Mogobe Ramose (Afrique australe) | Ubuntu : la personne existe par les autres | Qui sont « les autres » dont dépend ce système, et sont-ils dans le périmètre ? |
| Meadows | J. C. Kumarappa (Inde) | Économie de la permanence | La solution entretient-elle ce dont elle vit ? |
| Meadows | Pratiques : satoyama (Japon), zaï (Sahel), subak (Bali) | Systèmes anciens régulés par l'usage | Existe-t-il déjà une solution vernaculaire que l'« innovation » remplace ? |
| Fourquet | Yan Yunxiang, Xiang Biao (Chine) | Individualisation chinoise ; involution (内卷) ; « disparition du proche » (附近的消失) | La bascule décrite en France a-t-elle une forme locale différente ? |
| Fourquet | Yamada Masahiro (Japon) | Société des écarts (格差社会), célibataires parasites | Qu'a déjà vécu une société vieillie depuis 30 ans ? |
| Fourquet, Todd | Ibn Khaldoun (Maghreb, XIVe siècle) | 'Asabiyya : la cohésion se gagne à la périphérie et se perd au centre | Où se reforme la cohésion pendant que les centres s'individualisent ? |
| Fourquet | Felwine Sarr (Sénégal) | Afrotopia : cesser de se mesurer à l'aune d'un autre | L'indicateur utilisé suppose-t-il un rattrapage ? |
| Todd | Rita Segato, Aníbal Quijano (Amérique latine) | Colonialité du pouvoir | La catégorie utilisée vient-elle de l'administration coloniale ? |
| Baverez | Zhou Xiaochuan, Yu Yongding (Chine) | Critique du rôle du dollar depuis un pays créancier | Comment un détenteur de réserves voit-il la même monnaie ? |
| Baverez | Ndongo Samba Sylla (Sénégal) | Souveraineté monétaire, franc CFA | Qui décide de la monnaie de ceux qui l'utilisent ? |
| Baverez | Ha-Joon Chang (Corée du Sud), Justin Yifu Lin (Chine) | « Retirer l'échelle » ; nouvelle économie structurelle | La règle prônée a-t-elle été suivie par celui qui la prône ? |
| Baverez, puissance | Samir Amin (Égypte) | Déconnexion | Que gagne une zone à moins échanger ? |
| Baverez, puissance | Zhao Tingyang (Chine), Kishore Mahbubani (Singapour) | Tianxia ; siècle asiatique | À quoi ressemble un ordre mondial qui ne part pas de l'État-nation westphalien ? |
| Noubel | Hernando de Soto (Pérou), Anil Gupta (Inde) | Capital informel ; Honey Bee Network et innovation de base | Quelle richesse existe ici sans titre ni compte ? |
| Tous | Arturo Escobar (Colombie) | Plurivers | Cette synthèse suppose-t-elle un seul monde ? |
| Tous | Achille Mbembe (Cameroun) | Brutalisme ; devenir-nègre du monde | Qui est traité comme matière première dans ce récit ? |
| Tous | Kohei Saito (Japon) | Communisme de décroissance | Voix du pôle B de T02 depuis un pays riche non occidental |
| Tous | Ailton Krenak (Brésil) | Repousser la fin du monde | De quelle fin du monde parle-t-on, et pour qui a-t-elle déjà eu lieu ? |

Limite assumée : ces auteurs sont des universitaires publiés et traduits, donc déjà filtrés par l'édition occidentale. Le vrai contrepoids reste la lecture de sources ordinaires en langue d'origine.

### 9.3 Les règles chiffrées

Mesurées sur les **articles classés** d'un mois glissant, par `aire_source` (`config/seuils.yaml`) :

| Règle | Seuil |
|---|---|
| Part maximale d'une aire | 30 % |
| Part cumulée EU + US + OC | 45 % au plus |
| Part minimale de chacune des aires CN, IN, ASE, JK, AF, LA, MO + GO | 5 % |
| Part des articles non occidentaux lus dans leur langue d'origine | 50 % au moins |
| Part des articles d'ancrage `LOCAL` parmi ceux qui portent sur AF, LA, ASE, IN, MO | 50 % au moins |

**Indicateur affiché en permanence** : nombre d'aires au-dessus de 5 % et part de l'aire dominante. Exemple : « 9 aires · dominante EU 27 % ».

**Règle des trois aires** : toute synthèse cite au moins 3 aires de source. À défaut, elle l'écrit en tête.

**Langues prioritaires** : français, anglais, chinois, espagnol, portugais, arabe, hindi, indonésien, japonais, russe, puis coréen, turc, swahili, vietnamien.

---

## 10. Les objets de la base et leurs relations

### 10.1 Deux étages

**Étage 1 – La fiche article**, produite par le classement automatique (L2). Elle joue le rôle de « signal » : il n'y a pas d'objet Signal distinct.

**Étage 2 – Les objets d'analyse**, proposés par les agents (L3) et validés par Gabriel. Tous portent : identifiant, titre, statut (`candidat`, `observé`, `validé`, `archivé`), dates de création et de mise à jour, confiance (`forte`, `moyenne`, `faible`), liste des fiches qui les justifient, historique des versions.

| Objet | Champs propres | Seuil de création |
|---|---|---|
| **Tendance** | Lentilles, niveau N2 ou N3, zones, vitesse (accélère, stable, ralentit), date de première apparition, aire où elle est banale, aire où elle est un signal faible | 10 fiches, 5 sources, 4 semaines |
| **Mutation** | De quoi, vers quoi, moteurs, freins, zone la plus avancée, vitesse, gagnants, perdants, tensions déplacées, famille de levier, signaux à surveiller, classe de lenteur | Une tendance N3 ou une précipitation « précipitée », avec adoption A3 dans au moins une zone |
| **Précipitation** | Voir section 5 ; une ligne par zone | 3 preuves d'offre et 3 de besoin |
| **Cas** (galerie des solutions) | Acteurs, zone, problème traité, levier M1 à M12, rebond (score, types, nature, garde-fou), résultats chiffrés, ancienneté, transférabilité, critiques connues | 2 sources indépendantes dont une locale ; résultat mesuré |
| **Hypothèse** | Énoncé réfutable, échéance, confiance initiale et actuelle en pourcentage, signaux pour, signaux contre, issue | Créée par Gabriel ou proposée par un agent |
| **Axe de tension** | Voir section 4 ; positions par zone et par voix, intensité | Voir 4.3 |
| **Technologie** | Nom normalisé, classe de lenteur, TRL mondial, puis par zone : G, A, saut ; courbe de coût si disponible | Entrée dans la liste normalisée |
| **Zone** | Matrice P01 à P13, SWOT, positions sur les axes | Liste fixe |
| **Acteur** | Type (`ETAT`, `ENTREPRISE`, `COLLECTIF`, `VILLE`, `INSTITUTION`, `PERSONNE`, `RESEAU`), pays, lien au pouvoir | Cité dans 3 fiches |
| **Infrastructure** | Type, propriétaire, opérateur, norme, zones desservies | Citée dans 3 fiches |
| **Flux** | Nature (`MONETAIRE`, `MATIERE`, `ENERGIE`, `DONNEES`, `PERSONNES`, `NON_MONETAIRE`), origine, destination, ordre de grandeur, source | Une donnée chiffrée sourcée |
| **Dossier** | Question, périmètre, plan type, relecture du contradicteur | À la demande |

### 10.2 Les relations (liste fermée)

| Relation | De → vers | Exemple |
|---|---|---|
| `nourrit` | Fiche → tout objet | Un article nourrit une tendance |
| `devient` | Tendance → Mutation ; Précipitation → Mutation | Promotion |
| `déplace` | Mutation ou Cas → Axe (avec sens et zone) | Le solaire pakistanais déplace T08 vers la souveraineté des ménages |
| `dépasse` | Cas → Axe | Un cas sort du dilemme T01 |
| `dépend_de` | Zone ou Acteur → Zone, Acteur, Infrastructure, Flux | L'Europe dépend du raffinage chinois |
| `utilise` | Technologie → Technologie ou matériau | Passerelles |
| `migre_vers` | Technologie → secteur | Batterie LFP : automobile → stockage domestique |
| `opère` / `possède` | Acteur → Infrastructure | |
| `catalyse` | Événement, règle ou acteur → Précipitation | |
| `freine` | Tout → Mutation ou Précipitation | |
| `contredit` / `confirme` | Fiche → Hypothèse | |
| `ressemble_à` | Cas → Cas ; Mutation → Mutation | Analogie entre zones |

---

## 11. Tableau récapitulatif des valeurs autorisées

| Étiquette | Niveau | Valeurs |
|---|---|---|
| Lentille | Article | TEC, INF, MON, PUI, SOC, SOL, MIL (1 principale, 0 ou 1 secondaire) |
| Iceberg | Article, objet | N1, N2, N3, N4 |
| Horizon | Article, objet | H1, H2, H3 |
| Aire de source | Article | EU, US, CN, JK, IN, ASE, RU, GO, MO, AF, LA, OC, GLO |
| Aire du sujet | Article | Mêmes codes, 1 à 3 valeurs ; pays ISO en complément |
| Ancrage | Source | LOCAL, DIASPORA, CORRESPONDANT, INTERNATIONAL |
| Lien au pouvoir | Source | ETAT, PARTI, GROUPE_PRIVE, FONDATION_ONG, INSTITUTION, ENTREPRISE, INDEPENDANT, INCONNU |
| Nature | Article | FAIT, ANALYSE, OPINION, COMMUNICATION |
| Axes de tension | Article | T01 à T14 (0 à 2), avec pôle mis en avant : A, B, LES_DEUX, DEPASSEMENT |
| Tension libre | Article | Texte : « pôle A ↔ pôle B », 0 ou 1 |
| Signal de précipitation | Article | OFFRE, BESOIN, CATALYSEUR, AUCUN ; si catalyseur : PRIX, REGLE, COMPL, FIN, CHOC, RECIT, PONT |
| Indice de maturité | Article | COUT, VOLUME, NORME, MARCHE_PUBLIC, USINE, ECHEC, OCCASION, BREVET_PUBLI, AUCUN |
| Famille de levier | Article (si lentille SOL) | FA, FB, FC, FD, AUCUN |
| Indice de rebond | Article | MENTIONNE (avec type DIR, IND, ECO, SYS, TRA), NON_MENTIONNE |
| Confiance du classement | Article | 1 à 3 |
| Levier de Meadows | Cas | M12 à M1 |
| Rebond | Cas, Précipitation, Mutation | R0 à R3, R? ; types ; SUF ou SUR ; garde-fou oui, non, inconnu |
| Offre, besoin | Précipitation × zone | O0 à O5 ; B0 à B5 |
| Statut de précipitation | Précipitation × zone | Lointaine, En approche, Imminente, En cours, Précipitée, Dissoute |
| TRL | Technologie | 1 à 9 |
| Attentes | Technologie × zone | G0 à G5, G? ; saut oui ou non |
| Adoption | Technologie × zone | A0 à A5, A? |
| Classe de lenteur | Technologie, Mutation | C1 à C6 |
| Position sur un axe | Axe × zone × voix | −2 à +2 ; voix GOUV ou SOC ; intensité 0 à 3 |
| Puissance | Zone × dimension | Autonomie 1 à 5 ; levier 1 à 5 ; tendance ↑ → ↓ ; confiance A, B, C |
| Statut d'objet | Tout objet | candidat, observé, validé, archivé |

---

## 12. Validation

Grille appliquée par Claude à 20 articles réels en 9 langues, puis vérifiée par Gabriel (4 articles classés à la main en moins de 3 minutes chacun, mêmes résultats ; les 16 autres jugés justes). L1 est validée pour le développement ; le test complet se fera sur 100 articles au Sprint 3, avec les réponses acceptables (`decisions-sprint0.md`).
