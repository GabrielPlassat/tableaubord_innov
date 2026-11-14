# Sprint 1 – Les quatre vérifications (L5, section 1)

*14 novembre 2026. Vérifications faites sur la documentation publique. Aucune ne remet en cause l'architecture ; deux imposent des précautions.*

## 1. Quotas d'Albert — à lire dans votre compte

- Les limites exactes d'un compte se lisent dans l'objet `limits` renvoyé par `GET /v1/me/info` ; la page publique « Tarifs et limites » ne donne qu'une vue indicative par famille de modèles (requêtes et tokens par minute et par jour, modes expérimentation et production). Source : [guide Albert API, prise en main](https://guides.ia.numerique.gouv.fr/albert-api/prise-en-main/readme.md).
- Les identifiants de modèles changent (alias `openweight-…` depuis début 2026) : ne jamais les écrire en dur, toujours les lire par `GET /v1/models`.
- **Calcul à faire ensuite** : 8 000 à 10 000 fiches par mois = 2 appels par article (passes 1 et 2), soit environ 600 appels par jour. Si le quota quotidien est inférieur, il faudra baisser le volume ou passer davantage par Haiku.

Relevé du 14 novembre 2026 (`GET /v1/me/info`). Albert donne les limites par « routeur » (un routeur par modèle), sans dire quel routeur correspond à quel modèle.

| Routeurs | Requêtes par minute | Requêtes par jour | Tokens par minute | Tokens par jour | Interprétation probable |
|---|---|---|---|---|---|
| 342, 343 | 500 | 50 000 | illimité | illimité | Vecteurs et reclassement (bge-m3, bge-reranker) |
| 1090 | 50 | illimité | 246 000 | illimité | À identifier |
| 338, 339, 420, 1086 | 50 | 1 000 | 128 000 | 2 460 000 | Modèles de génération (la plupart) |
| 337 | 10 | 1 000 | 128 000 | 1 280 000 | Un modèle plus lourd |
| 1085, 1092 | 50 | 1 000 | illimité | illimité | À identifier (audio, OCR ?) |
| 1094 | 25 | 500 | 128 000 | 2 460 000 | À identifier |

**Ce que cela permet, par modèle de génération : environ 1 000 requêtes et 2,5 millions de tokens par jour.**

Besoin estimé : environ 1 000 articles collectés par jour, dont un tiers retenu.
- Passe 1 (tri) : 1 000 requêtes d'environ 800 tokens, soit 0,8 M de tokens par jour.
- Passe 2 (fiche) : environ 330 requêtes d'environ 5 000 tokens (consigne, liste des technologies, texte, réponse), soit 1,65 M.
- Total : environ 1 330 requêtes et 2,45 M de tokens par jour. **Cela dépasse la limite de requêtes d'un seul modèle, et frôle sa limite de tokens.**

**Décision proposée** : répartir les passes sur deux modèles, chacun ayant son propre quota.
- Passe 1 sur le plus petit modèle (Ministral 8B), puisque le tri est une tâche simple.
- Passe 2 sur le modèle retenu au Sprint 3.
- Les vecteurs ne posent aucun problème (50 000 requêtes par jour).
- En secours : Haiku pour l'excédent, environ 4 à 5 $ par mois à plein volume.
- Si cela ne suffit pas : un pré-tri sans modèle (mots-clés, sources très pertinentes) pour réduire le nombre d'articles soumis à la passe 1.

## 2. Streamlit Community Cloud — une seule application privée

- Community Cloud autorise **une application privée par espace de travail** et un nombre illimité d'applications publiques ; Streamlit ne prévoit pas d'en offrir davantage. Source : [FAQ Streamlit, applications privées supplémentaires](https://discuss.streamlit.io/t/faq-deploying-additional-private-apps-on-community-cloud/63632).
- Ressources : environ 2,7 Go par application d'après la page de limites affichée aux utilisateurs ([forum Streamlit](https://discuss.streamlit.io/t/topic/118484)) ; une application sans visite pendant environ 12 heures se met en veille.
- **Conséquence** : l'application v2 (`v2/Accueil.py`) doit occuper votre unique place privée. Si une autre de vos applications est déjà privée (wikixd-chat, carte de la dépendance automobile…), il faudra la rendre publique ou renoncer à la privatisation de l'une des deux.
- L'application v1 (`app.py`) reste publique et inchangée.
- Mémoire : 6 mois de vecteurs (environ 60 000 fiches × 1 024 nombres) représentent environ 250 Mo. Compatible, à mesurer au Sprint 3.

## 3. GitHub Actions — tâches planifiées suspendues après 60 jours d'inactivité

- Dans un dépôt public, les tâches planifiées sont désactivées automatiquement quand le dépôt n'a connu aucune activité pendant 60 jours. Source : [documentation GitHub, désactiver et activer un workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows).
- La désactivation est silencieuse ; un enregistrement (commit) dans le dépôt compte comme activité ([guide cronuru](https://cronuru.com/guides/github-actions-scheduled-workflows)).
- **Conséquence** : sans risque en régime normal, puisque la collecte enregistrera son journal dans le dépôt plusieurs fois par jour à partir du Sprint 2. Précaution retenue : la page « État du système » (Sprint 2) affichera la date de la dernière exécution, et une alerte si elle a plus de 2 jours.
- Les exécutions sur un dépôt public sont gratuites pour les machines standard de GitHub ([documentation GitHub, facturation](https://help.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration)).

## 4. GDELT — accès ouvert, sans clé, à débit limité

- L'interface DOC 2.0 est ouverte et sans clé. Elle cherche dans 65 langues traduites automatiquement à partir de mots-clés anglais ([blog GDELT](https://blog.gdeltproject.org/?p=3976)) et couvre les 3 derniers mois.
- Débit : environ une requête toutes les 5 secondes, d'après les intégrations tierces récentes ([exemple](https://lobehub.com/mcp/cyanheads-gdelt-mcp-server)). Avec 14 axes × une dizaine de marqueurs, la requête quotidienne prend une quinzaine de minutes : compatible avec une tâche GitHub Actions.
- Obligation : citer « The GDELT Project » avec un lien vers gdeltproject.org dans l'application.

## 5. Vérification ajoutée : Hugging Face, jeu de données privé

- Un compte gratuit dispose de 100 Go de stockage privé ([documentation Hugging Face](https://huggingface.co/docs/hub/en/storage-limits)). À raison de quelques dizaines de Mo par mois, la marge couvre plusieurs années.

## Ce qui n'a pas pu être vérifié dans cette session

- **Le fonctionnement réel des flux** : l'environnement de développement n'accède pas aux sites d'actualité. L'audit tourne donc dans GitHub Actions (tâche « Audit des sources »).
