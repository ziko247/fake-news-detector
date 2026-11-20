# Plateforme intelligente de détection des informations trompeuses

Ce projet vise à aider à vérifier les affirmations factuelles contenues dans un article ou une publication. Une même publication peut contenir une affirmation bien documentée et une autre qui reste incertaine. L’analyse se fait donc affirmation par affirmation.

## Fonctionnement prévu

1. L’utilisateur soumet le texte d’un article ou d’une publication.
2. L’application repère les affirmations vérifiables et recherche des sources pertinentes pour chacune.
3. Elle présente les passages qui appuient ou contredisent chaque affirmation, avec les liens vers les sources. Elle indique aussi ce qui reste incertain, par exemple lorsqu’un passage ne couvre qu’une partie de l’affirmation.
4. L’utilisateur peut retrouver ses analyses et leurs références dans un historique.

## Comment lire les résultats

| Statut | Signification |
| --- | --- |
| Appuyée par les sources | Les éléments trouvés vont dans le sens de l’affirmation. |
| Contredite | Des éléments pertinents vont à l’encontre de l’affirmation. |
| Non vérifiée | La vérification de cette affirmation reste à faire. |
| Insuffisamment documentée | Une recherche a été menée, mais les éléments trouvés sont trop limités pour se prononcer. |

Chaque résultat est une appréciation provisoire fondée sur les sources consultées. Les extraits et les références permettent de revenir au texte d’origine et de vérifier si le passage cité concerne bien l’affirmation.

## Pistes techniques

Le traitement automatique du langage (NLP) peut servir à extraire les affirmations du texte. La recherche sémantique permettrait de retrouver des passages pertinents même si les sources emploient d’autres mots. Une approche RAG est envisagée pour fournir ces passages à un modèle génératif chargé de résumer les éléments trouvés et de citer leur provenance.

## Exigences communes aux projets

Le backend peut être réalisé avec Django, Flask, FastAPI ou Spring Boot. Pour l’interface, les options sont Streamlit, Angular, React JS, Flutter ou React Native. Les choix doivent être justifiés en fonction des besoins et des contraintes du projet.

| Exigence | Application au projet |
| --- | --- |
| Données | Décrire les sources autorisées, le nettoyage des textes et les limites de la couverture documentaire. |
| Composant intelligent | Justifier l’approche retenue et la comparer à une solution simple sur les mêmes exemples. Une recherche par mots-clés peut servir de référence pour la recherche de passages. |
| Backend et API | Valider les entrées, gérer les erreurs et documenter l’API. |
| Interface | Permettre de saisir ou de coller un texte, puis présenter clairement les affirmations, leurs statuts, les extraits sourcés et les incertitudes. |
| Base de données | Stocker les utilisateurs, l’historique des analyses et les retours de validation. |
| Sécurité | Authentifier les utilisateurs, contrôler l’accès aux analyses et protéger les secrets. |
| Évaluation | Mesurer la qualité du repérage des affirmations, la pertinence des passages, la cohérence des statuts avec les sources et le temps de réponse. Analyser les erreurs observées. |
| Déploiement | Fournir un environnement Docker reproductible, un guide d’installation et une démonstration. |
| Maintenance | Prévoir des tests, suivre les versions du modèle et consigner les erreurs. |

### Périmètre proposé pour le prototype

Le premier parcours part d’un texte collé et s’appuie sur un corpus autorisé et délimité. Il doit permettre de distinguer une affirmation dont la vérification reste à faire d’une affirmation pour laquelle la recherche a fourni trop peu d’éléments. La recherche sémantique et le RAG font partie des approches possibles. La priorité est de livrer un prototype limité, évalué et déployé.

## État du projet

Le parcours d’analyse est disponible en ligne de commande et dans FastAPI. La requête de démonstration a renvoyé les trois statuts attendus avec E5 en local. La prochaine étape consiste à relier le formulaire Streamlit à l’API. Les 7 cas de test final restent réservés.

## Structure du projet

| Chemin | Contenu |
| --- | --- |
| `app/` | API FastAPI, analyse des textes, extraction, recherche E5 et règles de statut. |
| `data/` | Corpus HCP, annotations, répartition des exemples et texte de démonstration. |
| `experiments/` | Commandes et résultats des essais BM25, E5, extraction, mDeBERTa et démonstration en ligne de commande. |
| `tests/` | Tests de l’API, du parcours d’analyse et des règles de statut. |
| `requirements.txt` et `requirements-dev.txt` | Versions des dépendances du backend et du client de test. |

## API FastAPI en local

Depuis la racine du projet, créer l’environnement Python 3.12 si nécessaire, installer les dépendances et démarrer le serveur.

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
& .venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Au démarrage, le serveur charge E5 depuis le cache Hugging Face et encode les passages du corpus. Le premier lancement télécharge les poids publics si nécessaire. La documentation interactive se trouve à l’adresse [`/docs`](http://127.0.0.1:8000/docs) et le contrat OpenAPI à [`/openapi.json`](http://127.0.0.1:8000/openapi.json).

`POST /analyses` accepte un objet JSON avec un champ `texte` contenant de 1 à 12 000 caractères et au moins un caractère non blanc. Exemple de requête avec le texte de démonstration.

```powershell
$texte = [IO.File]::ReadAllText((Resolve-Path data/demo-rgph.txt).Path, [Text.Encoding]::UTF8)
$payload = @{ texte = $texte } | ConvertTo-Json
$reply = Invoke-WebRequest -UseBasicParsing -Method Post -Uri http://127.0.0.1:8000/analyses -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($payload))
[Text.Encoding]::UTF8.GetString($reply.RawContentStream.ToArray()) | ConvertFrom-Json
```

| Code HTTP | Réponse |
| --- | --- |
| `200` | Objet `affirmations` contenant une liste. Chaque entrée contient `affirmation`, `statut`, `explication`, `preuves` et `passages_consultes`. La liste est vide si l’extracteur ne relève aucune affirmation. |
| `422` | Erreur de validation FastAPI si la saisie est manquante, du mauvais type, vide ou trop longue. |
| `500` | Objet `{"detail": "L’analyse a échoué."}` en cas d’erreur pendant le traitement. |

Pour exécuter les tests, installer `requirements-dev.txt` dans le même environnement, puis lancer `& .venv/Scripts/python.exe -m unittest discover -s tests -v`. Les 17 tests passent. La requête de démonstration et Swagger ont aussi été vérifiés sur un serveur Uvicorn local avec les poids E5 en cache.

## Feuille de route à cocher

Cocher une tâche après avoir vérifié le résultat décrit sur sa ligne.

### 1. Cadrer le prototype

- [x] Définir le parcours sur texte collé et décrire les quatre statuts par affirmation.
- [x] Choisir le français et les recensements marocains pour le premier exercice.
- [x] Justifier le choix de FastAPI et Streamlit pour le prototype.

### 2. Préparer le corpus et les annotations

- [x] Documenter les deux publications du HCP, les conditions de réutilisation et la préparation des quatre passages.
- [x] Annoter les trois premiers cas avec le statut attendu, le passage probant ou l’information manquante.
- [x] Élargir le corpus avec des passages proches qui diffèrent par la date, le territoire ou l’indicateur. Les 16 passages ont un identifiant, une période et une référence vers une publication du HCP. [Corpus RGPH élargi](data/corpus-rgph.md)
- [x] Annoter de nouveaux textes avec les affirmations à extraire, les statuts et les passages attendus. Les six textes couvrent les reformulations, les contradictions et les cas sans preuve suffisante. [Textes annotés RGPH](data/annotations-rgph.md)
- [x] Répartir les exemples entre développement et test final en gardant les reformulations d’une même affirmation dans le même lot. Consigner la répartition et les limites de couverture. [Répartition des exemples](data/annotations-rgph.md#répartition-pour-lévaluation)

### 3. Établir la référence BM25

- [x] Exécuter BM25 sur les quatre passages et consigner les premiers résultats pour A01, A02 et A03.
- [x] Exécuter la même recherche sur le corpus élargi. Conserver le classement par affirmation, le rang des passages attendus et le temps de recherche sur le lot de développement. [Résultats BM25](#référence-bm25-sur-le-corpus-élargi)

### 4. Construire et choisir le composant intelligent

- [x] Construire une première référence pour l’extraction d’affirmations en conservant leur phrase d’origine. Vérifier les omissions, les opinions et les phrases sélectionnées à tort. [Résultats de l’extraction](#premier-essai-dextraction)
- [x] Comparer la recherche sémantique proposée avec E5 à BM25 sur les mêmes passages et requêtes de développement. Justifier le choix selon les preuves retrouvées et le temps de réponse. [Comparaison E5 et BM25](#comparaison-e5-et-bm25)
- [x] Tester la comparaison entre une affirmation et un passage, par exemple avec mDeBERTa. Examiner les erreurs sur les dates, les quantités et les négations. [Résultats mDeBERTa](#évaluation-des-passages-avec-mdeberta)
- [x] Définir comment attribuer les quatre statuts, y compris lorsqu’une vérification reste à faire, que les sources divergent ou que les passages couvrent seulement une partie de l’affirmation. [Règles d’attribution des statuts](#règles-dattribution-des-statuts)
- [x] Faire passer un texte complet dans le traitement et contrôler chaque statut, extrait, lien et explication. Consigner les modèles retenus et leurs limites. [Démonstration de bout en bout](#démonstration-de-bout-en-bout)

### 5. Relier FastAPI et Streamlit

- [x] Exposer l’analyse dans FastAPI, documenter les entrées et les réponses et tester un texte valide, une saisie vide et une erreur de traitement. [API FastAPI en local](#api-fastapi-en-local)
- [ ] Relier le formulaire Streamlit à l’API et afficher les affirmations, statuts, incertitudes, extraits et références.
- [ ] Vérifier depuis l’interface qu’un utilisateur peut coller un article, ouvrir un passage cité et comprendre le résultat lorsqu’aucune preuve suffisante n’est trouvée.

### 6. Enregistrer et sécuriser les analyses

- [ ] Choisir la base de données et vérifier la persistance des utilisateurs, analyses, affirmations, preuves et retours de validation après redémarrage.
- [ ] Mettre en place l’authentification et charger les secrets depuis l’environnement. Vérifier qu’une requête anonyme vers un historique privé est refusée.
- [ ] Permettre à l’utilisateur de rouvrir une analyse et d’enregistrer son retour sur une affirmation.
- [ ] Tester avec deux comptes que chacun peut consulter et commenter ses analyses et que l’API bloque l’accès aux analyses de l’autre.

### 7. Évaluer la version retenue

- [ ] Figer la configuration et exécuter les méthodes à comparer sur le lot de test réservé.
- [ ] Mesurer la précision et le rappel de l’extraction, le rang des preuves retrouvées et la qualité des statuts. Vérifier manuellement que les citations justifient les résultats.
- [ ] Mesurer le temps de réponse de bout en bout et noter les conditions de mesure.
- [ ] Présenter les résultats avec les effectifs, des exemples d’erreurs et les limites du corpus.

### 8. Déployer, tester et préparer la démonstration

- [ ] Automatiser les tests du parcours principal, des erreurs d’entrée et des droits d’accès.
- [ ] Versionner le corpus, les modèles et les dépendances. Journaliser les erreurs sans exposer les secrets.
- [ ] Préparer Docker, documenter l’installation et reproduire le démarrage depuis un environnement propre.
- [ ] Déployer le prototype et vérifier l’analyse, les liens vers les sources et la persistance de l’historique sur l’instance déployée.
- [ ] Répéter une démonstration avec une affirmation appuyée, une contredite et une insuffisamment documentée, puis retrouver l’analyse dans l’historique.

### Stack retenue pour le prototype

FastAPI sert de backend et fournit la validation des entrées et une documentation interactive de l’API. Streamlit sert d’interface pour le formulaire de saisie et l’affichage des résultats en Python. [Documentation FastAPI](https://fastapi.tiangolo.com/features/) · [Documentation Streamlit](https://docs.streamlit.io/)

### Premier exercice

Le [mini-corpus RGPH et ses trois cas annotés](data/mini-corpus-rgph.md) sont prêts pour le premier essai de recherche par mots-clés.

Le [script BM25](experiments/bm25_rgph.py) s’exécute avec `python experiments/bm25_rgph.py` depuis la racine du projet. Il utilise la bibliothèque standard Python et affiche le classement des quatre passages pour chaque affirmation. Les paramètres sont `k1 = 1.2` et `b = 0.75`, avec la [pondération IDF documentée par Lucene](https://lucene.apache.org/core/9_12_1/core/org/apache/lucene/search/similarities/BM25Similarity.html).

| Cas | Premier passage | Score BM25 | Observation |
| --- | --- | --- | --- |
| A01 | P01 | 10,012 | Le passage attendu est au rang 1. |
| A02 | P04 | 11,681 | Le passage attendu est au rang 1. |
| A03 | P01 | 6,147 | Le passage porte sur 2024. L’affirmation porte sur 2023. |

Les deux preuves attendues ont été retrouvées au premier rang. Le troisième cas montre qu’un résultat de recherche peut partager des mots avec l’affirmation tout en laissant la question ouverte. Ces trois cas vérifient le fonctionnement du script. La comparaison avec E5 nécessitera un jeu d’évaluation plus large.

### Référence BM25 sur le corpus élargi

Exécuter `python experiments/bm25_rgph.py --development` depuis la racine du projet. Les 9 requêtes reprennent le texte exact des affirmations annotées. Les références pronominales et temporelles restent donc présentes, comme dans A09 avec « Sur cette période ». Le script affiche les 16 passages classés pour chaque requête et les rangs des preuves attendues. [Classements complets](experiments/bm25_developpement.txt)

| Cas | Premier résultat | Rangs des preuves attendues | Temps médian |
| --- | --- | --- | ---: |
| A01 | P01 | P01 au rang 1 | 0,121 ms |
| A02 | P04 | P04 au rang 1 | 0,172 ms |
| A03 | P01 | Aucune preuve annotée | 0,110 ms |
| A04 | P01 | P01 au rang 1 | 0,067 ms |
| A05 | P06 | P05 au rang 2 | 0,052 ms |
| A08 | P16 | P09 au rang 2 | 0,089 ms |
| A09 | P08 | P09 au rang 5 et P10 au rang 6 | 0,091 ms |
| A15 | P01 | Aucune preuve annotée | 0,056 ms |
| A16 | P14 | Aucune preuve annotée | 0,053 ms |

Tous les passages attendus figurent dans les trois premiers résultats pour **5 des 6 cas documentés**. A05 illustre une confusion d’année. Le premier résultat reprend la valeur citée, mais concerne 2004 alors que l’affirmation parle de 2014. A09 demande deux preuves et dépend du contexte de la phrase précédente pour préciser la période. Les trois cas sans preuve annotée sont examinés séparément, car BM25 leur renvoie aussi des passages.

Chaque temps est la médiane de 101 recherches sur cet ordinateur sous Python 3.12. La mesure inclut la tokenisation de la requête, le calcul des scores et le tri. Elle commence après la préparation de l’index et se termine avant l’affichage des résultats.

### Premier essai d’extraction

Exécuter `python experiments/extraire_rgph.py` pour évaluer les trois textes du lot de développement. Pour analyser un fichier texte UTF-8, utiliser `python experiments/extraire_rgph.py chemin/vers/article.txt`. [Script d’extraction](experiments/extraire_rgph.py)

Cette référence découpe le texte en phrases et conserve celles qui contiennent un chiffre, après avoir filtré les questions terminées par « ? » et quelques débuts de phrase exprimant une opinion. Chaque résultat reprend la formulation d’origine.

| Texte | Affirmations attendues | Extraits exacts retrouvés | Phrases retenues à tort |
| --- | ---: | ---: | ---: |
| T01 | 2 | 2 | 0 |
| T03 | 2 | 1 | 0 |
| T06 | 2 | 2 | 0 |
| Total | 6 | 5 | 0 |

La précision est de 5/5 et le rappel de 5/6 sur ces trois textes. L’opinion de T01 est écartée. A09 est omise parce que sa comparaison ne contient aucun chiffre et renvoie à la période citée dans la phrase précédente. Ce premier essai couvre les affirmations chiffrées et sert de référence pour évaluer une extraction capable de traiter les comparaisons implicites.

### Comparaison E5 et BM25

Depuis la racine du projet, créer un environnement Python 3.12 et lancer l’expérience. Le premier lancement télécharge le tokenizer et les poids ONNX quantifiés en 8 bits de `intfloat/multilingual-e5-small`. [Fiche E5](https://huggingface.co/intfloat/multilingual-e5-small) · [Fichiers de la révision utilisée](https://huggingface.co/intfloat/multilingual-e5-small/tree/ccc66d3bcd826f577e26b9a4072cc5fe3a7ad6a3/onnx)

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe numpy==2.2.6 onnxruntime==1.22.1 tokenizers==0.21.4 huggingface-hub==0.34.4
& .venv/Scripts/python.exe experiments/comparer_e5_bm25.py
```

Les deux méthodes classent les 16 passages pour les mêmes neuf requêtes de développement. Pour E5, les passages sont encodés une fois, puis classés par similarité cosinus avec chaque requête encodée. Le script mesure la médiane de 21 recherches par requête et méthode sur CPU, après chargement du modèle et préparation de l’index. La mesure inclut le traitement de la requête et le classement. [Script de comparaison](experiments/comparer_e5_bm25.py)

| Cas | Méthode | Top 3 | Rangs des preuves | Temps médian (ms) |
| --- | --- | --- | --- | ---: |
| A01 | BM25 | P01, P15, P07 | P01 (1) | 0.157 |
| A01 | E5 | P01, P15, P03 | P01 (1) | 19.541 |
| A02 | BM25 | P04, P09, P10 | P04 (1) | 0.276 |
| A02 | E5 | P04, P09, P10 | P04 (1) | 23.780 |
| A03 | BM25 | P01, P07, P08 | — | 0.122 |
| A03 | E5 | P01, P05, P03 | — | 18.038 |
| A04 | BM25 | P01, P07, P08 | P01 (1) | 0.088 |
| A04 | E5 | P01, P15, P03 | P01 (1) | 20.735 |
| A05 | BM25 | P06, P05, P14 | P05 (2) | 0.105 |
| A05 | E5 | P05, P06, P02 | P05 (1) | 14.492 |
| A08 | BM25 | P16, P09, P01 | P09 (2) | 0.304 |
| A08 | E5 | P09, P04, P16 | P09 (1) | 22.547 |
| A09 | BM25 | P08, P16, P03 | P09 (5), P10 (6) | 0.252 |
| A09 | E5 | P10, P09, P04 | P09 (2), P10 (1) | 18.511 |
| A15 | BM25 | P01, P07, P08 | — | 0.195 |
| A15 | E5 | P01, P05, P03 | — | 18.531 |
| A16 | BM25 | P14, P16, P03 | — | 0.115 |
| A16 | E5 | P14, P15, P16 | — | 17.859 |

E5 retrouve tous les passages annotés dans les trois premiers résultats pour **6 cas sur 6**, contre **5 sur 6** pour BM25. Pour A09, les deux preuves passent des rangs 5 et 6 aux rangs 2 et 1. Les trois cas sans preuve annotée sont exclus de ce calcul. Les deux méthodes proposent aussi des passages pour ces cas, dont il faudra évaluer le contenu avant d’attribuer un statut.

La médiane des temps par requête est de **18,531 ms pour E5** et **0,157 ms pour BM25** sur cet ordinateur. On retient E5 pour le prototype parce qu’il couvre les deux preuves d’A09 dans les trois premiers résultats, avec un temps médian inférieur à 24 ms pour chacune des neuf requêtes. BM25 reste la référence de comparaison. Ce choix repose sur neuf cas de développement, dont deux reprises d’affirmations, et sera réévalué sur le lot de test réservé.

### Évaluation des passages avec mDeBERTa

Depuis la racine du projet, lancer `& .venv/Scripts/python.exe experiments/evaluer_mdeberta.py` avec l’environnement ONNX de l’essai E5. Le premier lancement récupère les poids quantifiés, le tokenizer et la configuration de classes. [Fiche de mDeBERTa](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli) · [Révision utilisée](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli/tree/704310ca0bb8eb15bca150fc1e11083cd423dd02)

Le modèle reçoit les passages en premier et l’affirmation en second. Il prédit une relation d’appui, de contradiction ou de neutralité. L’essai utilise des passages sélectionnés à partir des cas de développement et des variantes contrôlées pour les dates, les quantités et les négations. Pour A05 et A09, le territoire ou la période sont explicités dans la phrase. Le lot de test final reste réservé.

| Cas | Passages | Attendu | Prédit | Score de la classe prédite |
| --- | --- | --- | --- | ---: |
| A01 | P01 | appui | appui | 0.982 |
| A02 | P04 | contradiction | neutre | 0.742 |
| A03 | P01 | neutre | neutre | 0.847 |
| A04 | P01 | appui | appui | 0.920 |
| A05, année correspondante | P05 | contradiction | neutre | 0.648 |
| A05, autre année | P06 | neutre | neutre | 0.624 |
| A08 | P09 | appui | appui | 0.861 |
| A09, deux passages | P09, P10 | contradiction | neutre | 0.758 |
| A09, un seul passage | P09 | neutre | neutre | 0.885 |
| Quantité modifiée | P01 | contradiction | appui | 0.861 |
| Négation du total | P01 | contradiction | contradiction | 0.679 |
| Négation d'une baisse | P09 | appui | neutre | 0.745 |
| A16 | P14 | neutre | neutre | 0.990 |

L’essai donne **8 relations correctes sur 13**. Le modèle reconnaît 3 des 4 appuis, 1 des 5 contradictions et les 4 cas neutres. Les passages d’une autre année sont classés neutres dans A03 et A05. Le chiffre de 2014 dans A05 contredit pourtant l’affirmation, que le modèle classe aussi neutre. Les deux taux de A09 suffisent à réfuter la comparaison annotée, que le modèle classe neutre même avec les deux passages.

La quantité modifiée de 36 828 330 à 36 828 331 est prédite comme un appui avec un score de 0,861. Le modèle détecte la négation directe du total et rate l’appui à la phrase « n’a pas diminué ». Ce petit essai mesure le classement de paires construites à la main. Les scores indiquent la préférence du modèle parmi trois classes. Pour l’attribution des statuts, ces résultats motivent une vérification explicite de la période, des quantités et de la couverture des preuves.

### Règles d’attribution des statuts

Pour chaque affirmation, il faut vérifier la concordance du territoire, de la population concernée, de la période et de l’indicateur. Quand des chiffres interviennent, il faut aussi comparer leurs valeurs, unités et niveaux de précision. Des passages compatibles peuvent être examinés ensemble. Pour appuyer une affirmation, les preuves doivent couvrir tous ses éléments nécessaires. Pour la contredire, une preuve qui réfute un élément nécessaire peut suffire.

| Situation | Statut |
| --- | --- |
| La vérification reste à faire ou a été interrompue. | Non vérifiée |
| Des preuves suffisantes et de même périmètre appuient l’affirmation. | Appuyée par les sources |
| Des preuves suffisantes et de même périmètre la réfutent. | Contredite |
| La vérification est terminée et les preuves manquent, sont partielles, hors périmètre, neutres ou divergent de façon décisive. | Insuffisamment documentée |

La divergence entre preuves suffisantes prime sur les deux décisions conclusives. Dans ce cas, l’explication signale explicitement le désaccord. Par exemple, le chiffre de 2024 dans P01 laisse le cas A03 sur 2023 insuffisamment documenté. Pour A09, les passages P09 et P10 doivent être lus ensemble pour vérifier la comparaison entre les taux rural et urbain.

Le module Python applique ces règles à des évaluations de preuve déjà renseignées. La validation du périmètre et des valeurs intervient en amont. Un score de mDeBERTa est un signal à examiner avant de renseigner ces évaluations. Les huit tests couvrent les quatre statuts, les preuves partielles, les passages hors période et les sources qui divergent. La commande est `& .venv/Scripts/python.exe -m unittest discover -s tests -v`. [Module de décision](app/verdict.py) · [Tests](tests/test_verdict_rgph.py)

### Démonstration de bout en bout

Depuis la racine du projet, utiliser l’environnement de l’essai E5 et lancer `& .venv/Scripts/python.exe -m experiments.analyser_rgph data/demo-rgph.txt`. La commande accepte aussi un autre fichier texte UTF-8. Elle renvoie en JSON les phrases d’origine, les statuts, les explications et les passages du corpus avec les liens HCP. Les passages qui justifient un statut figurent dans `preuves`. [Analyse du texte](experiments/analyser_rgph.py) · [Texte de démonstration](data/demo-rgph.txt)

| Affirmation de la démo | Statut obtenu | Explication et preuve |
| --- | --- | --- |
| Le Maroc comptait 36 828 330 habitants au 1er septembre 2024. | Appuyée par les sources | P01 donne le même total à la même date. |
| Le Maroc comptait 10 000 000 ménages en 2024. | Contredite | P15 donne 9 275 038 ménages pour le même territoire et la même année. |
| Le Maroc comptait 36 828 330 habitants au 1er septembre 2023. | Insuffisamment documentée | Le passage le plus proche concerne 2024. |

L’avis ajouté au texte est écarté par l’extracteur. E5 fournit les trois passages les mieux classés. Les règles comparent des valeurs exactes pour les formulations reconnues sur la population nationale datée, le nombre national de ménages et le taux national d’urbanisation. Les reformulations complexes, comparaisons et indicateurs hors de ces formats exigent un traitement supplémentaire. Les scores mDeBERTa restent des résultats expérimentaux, car l’essai a montré des erreurs sur les quantités.

Les tests de l’analyse vérifient notamment la conservation du texte d’origine, le renvoi aux sources et la détection d’un écart d’un habitant. La commande de démonstration a également été vérifiée avec le modèle E5 local. [Tests de l’analyse](tests/test_analyser_rgph.py)
