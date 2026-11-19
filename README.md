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

## État du projet

Le projet est au stade du cadrage. Le premier objectif proposé est de tester le parcours sur un texte collé, depuis l’extraction des affirmations jusqu’à l’affichage des passages sourcés. Les choix techniques restent à valider.
