# L2 – Les consignes de classement (Innovation Radar v2)

*Version 1.0 du 14 novembre 2026. Pour Albert, avec Haiku 5.5 en secours. Tous les codes viennent de L1, section 11.*

> **Dans le dépôt**, les consignes des passes 1 et 2 (sections 2 et 3 du document d'origine) sont dans `config/consignes/passe1_v1.txt` et `config/consignes/passe2_v1.txt` : ce sont elles qui font foi. Les 20 exemples de la section 5, dans la version validée par Gabriel, sont dans `tests/reference_20.csv`.

---

## 0. Ce que je change par rapport au cadrage

| Constat | Proposition |
|---|---|
| **30 000 classements complets par mois** sur un service à quotas : risqué, et la plupart des articles ne méritent pas une fiche. | Deux corpus. Le **corpus lu** : environ 30 000 articles collectés, 8 000 à 10 000 classés après le filtre. Le **corpus compté** : la presse mondiale interrogée dans GDELT par mots-clés, sans lecture ni modèle, pour mesurer les volumes (intensité des tensions, attentes par zone). |
| **Traduire, résumer, classer en trois appels.** | **Un seul appel** : le modèle lit dans la langue d'origine et produit directement un résumé en français et les étiquettes. |
| **TRL, phase Gartner, levier de Meadows et rebond par article.** | L'article ne porte que des **indices** (L1, point 3 de la section 0). Les notes sont attribuées aux objets par les agents de L3. |
| **Un seul seuil d'accord de 80 %** pour tous les champs. | Des seuils **par champ**. Deux lecteurs humains ne s'accordent pas à 80 % sur un niveau d'iceberg ; l'exiger d'un modèle conduirait à tricher sur le test. |
| **Médias d'État signalés par le modèle.** | Le lien au pouvoir est une propriété de la **source**, renseignée une fois dans le registre. Le modèle ne le devine pas. |

---

## 1. La chaîne en deux passes

```
Article collecté
   │  données connues sans modèle : source, aire_source, ancrage, lien_pouvoir,
   │  langue, date, URL (viennent du registre des sources)
   ▼
PASSE 1 – Filtre (titre + 500 premiers caractères)        → OUI / NON / DOUTE
   │  NON : on garde seulement le titre, l'URL et le motif (pour le Miroir)
   ▼
PASSE 2 – Fiche complète (titre + 6 000 premiers caractères du texte)
   ▼
Contrôles automatiques (format, codes autorisés, cohérence)
   ▼
Fiche stockée : résumé et étiquettes. Le texte de l'article n'est jamais conservé.
```

Les articles `DOUTE` passent en passe 2. Le taux de `OUI` attendu se situe entre 25 et 35 %. En dehors de cette fourchette pendant une semaine, la consigne de passe 1 est à revoir.

---

## 2. Consigne de la passe 1

Voir `config/consignes/passe1_v1.txt`.

## 3. Consigne de la passe 2

Voir `config/consignes/passe2_v1.txt`. La liste des technologies (`config/technologies.csv`) est insérée avant `ARTICLE`. La partie fixe de la consigne est identique à chaque appel.

---

## 4. Règles de décision pour les cas limites

| Cas | Règle |
|---|---|
| **Plusieurs lentilles** | Principale = celle qui porte le fait nouveau. Jamais plus de deux. Exemple : une usine de batteries financée par un État étranger : TEC si l'article détaille l'usine, PUI s'il détaille la dépendance. |
| **SOL ou autre chose ?** | SOL exige une action **déjà engagée** et **un résultat cité**. Une annonce, un plan, une promesse : la lentille du domaine, et `nature` = COMMUNICATION si le texte vient de l'acteur. |
| **MIL ou SOL ?** | Un constat sur un milieu : MIL. Une action sur ce milieu avec résultat : SOL en principale, MIL en secondaire. |
| **Communiqué promotionnel** | `nature` = COMMUNICATION, `confiance` plafonnée à 2. Jamais `precipitation` = BESOIN. |
| **Source liée à un État, un parti ou une entreprise** | Classée comme les autres. Le lien vient du registre. Les agents de L3 appliquent la règle : jamais seule pour établir un fait. |
| **Article d'opinion** | `nature` = OPINION ; le résumé commence par « L'auteur soutient que » ; les axes notent le pôle défendu. Une opinion est une bonne source pour N4. |
| **Chiffres non sourcés** | Repris dans `chiffres_cles` avec `source_citee` = null. Un tel chiffre ne peut pas alimenter une note d'adoption ni une case de la matrice. |
| **Source étrangère sur une zone** (Reuters sur le Kenya) | `aire_source` reste celle de la source ; `aire_sujet` = AF. C'est cette paire qui alimente le Miroir. |
| **Sujet mondial** | `aire_sujet` = GLO seulement si aucune zone ne domine. Sinon les zones, 3 au plus. |
| **Axe : thème ou opposition ?** | Un article sur l'intelligence artificielle ne porte pas T03 d'office. Il le porte si une position (« l'IA résoudra », « il faut ralentir ») y est exprimée ou contestée. Dans le doute : aucun axe. |
| **Iceberg : hésitation entre deux niveaux** | Le plus bas des deux, c'est-à-dire le moins profond. Un excès de N3 rend la synthèse hebdomadaire inutilisable. |
| **Texte coupé par un mur payant** | `confiance` = 1. La fiche est gardée pour le décompte, exclue des synthèses. |
| **Doublon** (dépêche reprise par dix sites) | Traité avant le classement : on garde la source la plus proche du fait et on compte les reprises dans un champ `reprises`. |

**Contrôles automatiques après la passe 2**, sans modèle :
- JSON valide et tous les codes dans les listes ; sinon un nouvel essai, puis Haiku ;
- `levier_famille` différent de AUCUN seulement si SOL figure dans les lentilles ;
- `catalyseur_type` rempli si et seulement si `precipitation` = CATALYSEUR ;
- résumé entre 200 et 900 caractères, en français ;
- chaque nombre du résumé figure dans le texte source (comparaison simple des chiffres).

---

## 5. Exemples annotés

Les 20 articles de référence validés par Gabriel sont dans `tests/reference_20.csv` (feuille de test « Test de la grille L1 – 20 articles à classer »).

**Ce que ces exemples apprennent**

- **L'effet rebond.** L'article d'Aaj Tak décrit la subvention des pompes solaires sans évoquer les nappes ; le risque est documenté ailleurs. Le rebond ne peut donc pas être noté article par article : il l'est au niveau du cas, par recoupement.
- **Les sources chinoises sur les motos électriques en Afrique** : un fait (21世纪经济报道), une lecture d'agence d'État (新华财经), une tribune critique (观察者网). Le lien au pouvoir ne prédit pas le contenu, et la critique la plus dure du modèle chinois de crédit vient ici d'un site chinois.
- **Dawn.** Un seul article peut porter un catalyseur, un rebond systémique et un dépassement d'axe. Les trois champs sont indépendants.
- **L'Éclaireur Fnac.** Un texte promotionnel peut être la seule trace accessible d'un contenu de niveau N4. On le garde, avec sa nature.
- **L'AIE** est classée INSTITUTION et GLO, mais ses membres sont surtout des pays de l'OCDE. Le registre des sources doit pouvoir le noter en remarque.
- **الاستقلال.** L'ancrage et le propriétaire du site n'ont pas pu être établis. La valeur INCONNU existe pour cela.

**Trois fiches complètes**, à insérer comme exemples dans la consigne de passe 2 :

```json
{"titre_fr": "Les émissions de NOx de l'industrie du nickel à Sulawesi et aux Moluques dépassent les sources de pollution du Grand Jakarta",
 "resume": "Selon une étude du CREA rapportée par Kompas, les centrales à charbon captives qui alimentent les fonderies de nickel de Sulawesi et des Moluques du Nord représentent environ 80 % des nouvelles capacités charbon d'Indonésie. Leurs émissions d'oxydes d'azote dépassent celles des sources du Grand Jakarta. L'étude relie cette croissance à une exception prévue par le règlement présidentiel 112 de 2022. Ces centrales fonctionnent hors du réseau national.",
 "nature": "FAIT", "aire_sujet": ["ASE"], "pays": ["ID"],
 "lentille_principale": "MIL", "lentille_secondaire": "TEC",
 "iceberg": "N3", "horizon": "H2",
 "axes": [{"code": "T01", "pole": "LES_DEUX"}, {"code": "T04", "pole": "B"}],
 "tension_libre": null, "precipitation": "AUCUN", "catalyseur_type": null,
 "technologies": ["raffinage du nickel"], "indice_maturite": "AUCUN",
 "levier_famille": "AUCUN", "rebond": "MENTIONNE", "rebond_type": "TRA",
 "entites": [{"nom": "CREA", "type": "INSTITUTION", "pays": null}],
 "chiffres_cles": [{"valeur": 80, "unite": "% des nouvelles capacités charbon", "annee": 2026, "objet": "centrales captives en Indonésie", "source_citee": "CREA"}],
 "confiance": 2}
```

```json
{"titre_fr": "Les deux-roues électriques chinois entrent en Afrique : Yadea rencontre le « roi du téléphone africain »",
 "resume": "En juin 2026, la société africaine de mobilité électrique Spiro a levé 270 millions de dollars, dont 55 millions auprès de NewTrails Capital, un fonds dont Transsion est un actionnaire important. Spiro a ensuite signé un accord avec Yadea : le constructeur chinois fournira des deux-roues adaptés localement, que Spiro raccordera à son réseau d'échange de batteries. Les deux sociétés prévoient de concevoir ensemble une plateforme adaptée aux routes africaines.",
 "nature": "FAIT", "aire_sujet": ["AF", "CN"], "pays": ["CN"],
 "lentille_principale": "TEC", "lentille_secondaire": "INF",
 "iceberg": "N1", "horizon": "H2", "axes": [], "tension_libre": null,
 "precipitation": "CATALYSEUR", "catalyseur_type": "PONT",
 "technologies": ["deux-roues électrique à batterie échangeable"], "indice_maturite": "AUCUN",
 "levier_famille": "AUCUN", "rebond": "NON_MENTIONNE", "rebond_type": null,
 "entites": [{"nom": "Spiro", "type": "ENTREPRISE", "pays": null}, {"nom": "Yadea", "type": "ENTREPRISE", "pays": "CN"}, {"nom": "Transsion", "type": "ENTREPRISE", "pays": "CN"}, {"nom": "NewTrails Capital", "type": "ENTREPRISE", "pays": "CN"}],
 "chiffres_cles": [{"valeur": 270, "unite": "millions de dollars", "annee": 2026, "objet": "levée de fonds de Spiro", "source_citee": null}],
 "confiance": 2}
```

```json
{"titre_fr": "L'adoption des véhicules électriques s'accélère en Éthiopie après l'interdiction d'importer des voitures thermiques",
 "resume": "Selon des données gouvernementales citées par Daba Finance en février 2026, la part des véhicules électriques dans le parc éthiopien est passée de moins de 1 % à près de 6 % en deux ans, après l'interdiction d'importer des voitures à essence et diesel. Le pays compte environ 1,7 million de véhicules pour 130 millions d'habitants.",
 "nature": "FAIT", "aire_sujet": ["AF"], "pays": ["ET"],
 "lentille_principale": "SOL", "lentille_secondaire": "TEC",
 "iceberg": "N2", "horizon": "H2",
 "axes": [{"code": "T04", "pole": "B"}], "tension_libre": null,
 "precipitation": "CATALYSEUR", "catalyseur_type": "REGLE",
 "technologies": ["voiture électrique"], "indice_maturite": "VOLUME",
 "levier_famille": "FC", "rebond": "NON_MENTIONNE", "rebond_type": null,
 "entites": [{"nom": "Éthiopie", "type": "ETAT", "pays": "ET"}],
 "chiffres_cles": [{"valeur": 6, "unite": "% du parc", "annee": 2026, "objet": "véhicules électriques en Éthiopie", "source_citee": "gouvernement éthiopien"}],
 "confiance": 2}
```

---

## 6. Le protocole de test

### 6.1 Le jeu de référence : 100 articles étiquetés par Gabriel

| Strate | Nombre |
|---|---|
| Non occidentaux, en langue d'origine (au moins 6 langues) | 40 |
| Non occidentaux, en anglais ou en français | 15 |
| Occidentaux | 30 |
| À rejeter en passe 1 | 15 |

Avec au moins 10 articles par lentille, 10 OPINION, 10 COMMUNICATION, 8 articles sur un sujet sensible pour un État (voir 6.4).

**Réponses acceptables** (`decisions-sprint0.md`) : pour chaque étiquette, une réponse principale et, au besoin, une ou deux réponses acceptables. On suit l'accord strict et l'accord large ; les seuils ci-dessous s'appliquent à l'accord large.

**Temps à prévoir** : 3 minutes par article, soit environ 5 heures. Pour réduire : Claude pré-remplit les 100 fiches, Gabriel corrige. L'accord mesuré sera un peu optimiste ; il faut le savoir.

### 6.2 Seuils d'accord par champ

| Champ | Mesure | Seuil |
|---|---|---|
| Passe 1 : articles pertinents retrouvés | Part des OUI de référence classés OUI ou DOUTE | ≥ 95 % |
| Passe 1 : rejets corrects | Part des NON de référence classés NON | ≥ 80 % |
| JSON valide et codes autorisés | Au premier essai | ≥ 98 % |
| `aire_sujet` | Au moins une aire commune | ≥ 90 % |
| `nature` | Exact | ≥ 80 % |
| `lentille_principale` | Exacte, ou égale à la secondaire de référence | ≥ 80 % |
| `iceberg` | Exact | ≥ 65 % ; à un niveau près ≥ 90 % |
| `axes` | Au moins un axe commun quand la référence en a ; aucun quand elle n'en a pas | ≥ 70 % |
| `precipitation` | Exact | ≥ 70 % |
| `levier_famille`, `rebond` | Exact | ≥ 70 % |
| Résumé | Note de 1 à 5 sur 30 articles : fidèle, neutre, chiffres exacts | Moyenne ≥ 4 ; aucun chiffre faux |

**Le « seuil de 80 % » du cadrage** devient : moyenne des cinq premiers champs de fond (`aire_sujet`, `nature`, `lentille_principale`, passe 1 pertinents, passe 1 rejets) ≥ 85 %, et aucun autre champ sous son seuil.

### 6.3 Les modèles à comparer

1. Deux ou trois modèles de génération d'Albert (un petit, un moyen, un grand). Leurs identifiants changent : Albert a remplacé ses alias `albert-` par des alias `openweight-` début 2026 ([Next](https://next.ink/brief-article/albert-lia-souveraine-de-la-dinum-ne-sera-pas-generalisee-dans-sa-forme-actuelle/)). La liste à jour s'obtient par `GET /v1/models` ([guide Albert API](https://guides.ia.numerique.gouv.fr/albert-api/guides/models)).
2. Haiku 5.5.
3. En étalon, Opus 5.5 sur les 100 articles : il donne le plafond atteignable par un modèle.

Pour chacun : accord par champ, coût, durée par article, taux d'échec.

### 6.4 Le test d'omission

Pour chaque modèle d'origine non européenne proposé par Albert, et pour les autres à titre de contrôle : 8 articles portant sur des sujets sensibles pour différents États (de plusieurs bords). On compare les résumés entre modèles et on vérifie qu'aucun fait central ne disparaît. Un modèle qui omet est exclu du classement, quels que soient ses autres résultats.

### 6.5 Le contrôle continu

Chaque semaine, 20 fiches tirées au hasard sont présentées à Gabriel (dans les 45 minutes de validation, ou une semaine sur deux si c'est trop). Ses corrections alimentent le suivi de l'accord, et les cas les plus instructifs remplacent les exemples de la consigne.

---

## 7. Les listes normalisées

Tenues dans des fichiers CSV modifiables depuis GitHub (`config/`), avec pour chaque entrée : nom normalisé, variantes et traductions, identifiant Wikidata si disponible.

- **Zones et pays** : `config/zones_pays.csv` (L1, section 7.1).
- **Technologies** : `config/technologies.csv`, environ 50 au départ ; une technologie citée 5 fois sous « NOUVEAU » est proposée à l'ajout.
- **Matériaux** : lithium, cobalt, nickel, cuivre, graphite, terres rares, gallium, germanium, silicium, manganèse, phosphate, potasse, sable, bauxite et aluminium, acier, uranium, hélium, eau douce.
- **Acteurs** : pas de liste fermée. Table de variantes alimentée automatiquement (une entité citée dans 3 fiches devient un Acteur), avec fusion manuelle des doublons.

---

## 8. État du critère « fini quand »

Le critère demande que le meilleur modèle atteigne le seuil sur le jeu de test. **Il n'est pas atteint** : il dépend du jeu de 100 articles (Sprint 3). Premier coup de sonde : le carnet `notebooks/sprint1_test_albert.ipynb` sur les 20 articles de référence.

## Points à tester

1. Les quotas réels d'Albert (`GET /v1/me/info`) : c'est ce qui fixe le volume.
2. Les 20 exemples dans un ou plusieurs modèles d'Albert (carnet du Sprint 1).
3. Le respect du JSON sur des textes en chinois, en arabe et en hindi.
4. Le taux de OUI de la passe 1 sur une journée réelle.
5. Le contrôle des nombres du résumé sur des écritures de chiffres non latines et sur les lakh et crore indiens.
