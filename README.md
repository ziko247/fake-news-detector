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

La référence BM25 est mesurée sur 16 passages et 9 cas de développement. Les 7 cas de test final restent réservés. La prochaine étape consiste à extraire les affirmations vérifiables d’un texte.

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

- [ ] Extraire les affirmations vérifiables d’un article en conservant leur phrase d’origine. Vérifier les omissions, les opinions et les affirmations ajoutées à tort.
- [ ] Comparer la recherche sémantique proposée avec E5 à BM25 sur les mêmes passages et requêtes de développement. Justifier le choix selon les preuves retrouvées et le temps de réponse.
- [ ] Tester la comparaison entre une affirmation et un passage, par exemple avec mDeBERTa. Examiner les erreurs sur les dates, les quantités et les négations.
- [ ] Définir comment attribuer les quatre statuts, y compris lorsqu’une vérification reste à faire, que les sources divergent ou que les passages couvrent seulement une partie de l’affirmation.
- [ ] Faire passer un article complet dans le traitement et contrôler chaque statut, extrait, lien et explication. Consigner les modèles retenus et leurs limites.

### 5. Relier FastAPI et Streamlit

- [ ] Exposer l’analyse dans FastAPI, documenter les entrées et les réponses et tester un texte valide, une saisie vide et une erreur de traitement.
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
