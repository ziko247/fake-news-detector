# Textes annotés pour la vérification RGPH

Ces six textes ont été rédigés pour l’évaluation. Les statuts sont établis à partir des 16 passages du [corpus RGPH](corpus-rgph.md). Chaque extrait attendu reprend la phrase du texte à l’identique. Le tiret dans la colonne des preuves indique qu’aucun passage du corpus ne suffit pour trancher.

## Textes

### T01 · Population nationale

> D’après le recensement, le Royaume comptait 36 828 330 habitants au 1er septembre 2024. En 2014, sa population légale était d’environ 29,892 millions. À mon avis, ces chiffres méritent une discussion.

### T02 · Urbanisation

> La part de la population marocaine vivant en ville atteignait 62,8 % en 2024. Elle était déjà de 62,8 % en 2014. Qu’en sera-t-il dans dix ans ?

### T03 · Croissance par milieu

> De 2014 à 2024, le nombre d’habitants des villes marocaines a progressé de 1,24 % par an en moyenne. Sur cette période, le rythme annuel moyen en milieu rural était supérieur à celui des villes.

### T04 · Populations régionales

> En 2024, Rabat-Salé-Kénitra comptait environ 5,133 millions d’habitants. La même année, Marrakech-Safi comptait plus d’habitants que Rabat-Salé-Kénitra.

### T05 · Ménages

> Le Maroc comptait 9 275 038 ménages en 2024. En moyenne, chaque ménage regroupait 3,9 personnes cette année-là. Il y avait exactement un million de ménages constitués d’une seule personne en 2024.

### T06 · Données manquantes

> Au 1er septembre 2023, le Maroc comptait exactement 36 millions d’habitants. En 2024, 45 % des ménages de Marrakech-Safi vivaient en milieu rural.

## Annotations attendues

| Texte | ID | Extrait à relever | Statut attendu | Preuves | Justification |
| --- | --- | --- | --- | --- | --- |
| T01 | A04 | D’après le recensement, le Royaume comptait 36 828 330 habitants au 1er septembre 2024. | Appuyée par les sources | P01 | Le total et la date concordent. |
| T01 | A05 | En 2014, sa population légale était d’environ 29,892 millions. | Contredite | P05 | Le Maroc comptait environ 33,848 millions d’habitants en 2014. La valeur citée correspond à 2004 selon P06. |
| T02 | A06 | La part de la population marocaine vivant en ville atteignait 62,8 % en 2024. | Appuyée par les sources | P12 | La part de population vivant en ville correspond au taux d’urbanisation. |
| T02 | A07 | Elle était déjà de 62,8 % en 2014. | Contredite | P11 | « Elle » renvoie à la part urbaine du Maroc. Celle-ci était de 60,4 % en 2014. |
| T03 | A08 | De 2014 à 2024, le nombre d’habitants des villes marocaines a progressé de 1,24 % par an en moyenne. | Appuyée par les sources | P09 | Le chiffre concerne la croissance annuelle moyenne de la population urbaine. |
| T03 | A09 | Sur cette période, le rythme annuel moyen en milieu rural était supérieur à celui des villes. | Contredite | P09, P10 | Entre 2014 et 2024, le rythme rural de 0,22 % était inférieur au rythme urbain de 1,24 %. |
| T04 | A10 | En 2024, Rabat-Salé-Kénitra comptait environ 5,133 millions d’habitants. | Appuyée par les sources | P13 | Le territoire, l’année et la valeur concordent. |
| T04 | A11 | La même année, Marrakech-Safi comptait plus d’habitants que Rabat-Salé-Kénitra. | Contredite | P13, P14 | En 2024, Marrakech-Safi comptait environ 4,892 millions d’habitants contre 5,133 millions à Rabat-Salé-Kénitra. |
| T05 | A12 | Le Maroc comptait 9 275 038 ménages en 2024. | Appuyée par les sources | P15 | Le total national des ménages concorde. |
| T05 | A13 | En moyenne, chaque ménage regroupait 3,9 personnes cette année-là. | Appuyée par les sources | P16 | « Cette année-là » renvoie à 2024. |
| T05 | A14 | Il y avait exactement un million de ménages constitués d’une seule personne en 2024. | Insuffisamment documentée | — | Le total et la taille moyenne ne permettent pas de déterminer le nombre de ménages d’une personne. |
| T06 | A15 | Au 1er septembre 2023, le Maroc comptait exactement 36 millions d’habitants. | Insuffisamment documentée | — | Le corpus ne donne aucun décompte pour cette date. |
| T06 | A16 | En 2024, 45 % des ménages de Marrakech-Safi vivaient en milieu rural. | Insuffisamment documentée | — | Le corpus ne donne aucune répartition des ménages de cette région par milieu de résidence. |

La dernière phrase de T01 exprime une opinion. Celle de T02 pose une question. Ces deux phrases sont à écarter lors de l’extraction.

## Répartition pour l’évaluation

| Lot | Entrée | Affirmations |
| --- | --- | --- |
| Développement | [Mini-corpus et premier essai BM25](mini-corpus-rgph.md) | A01, A02, A03 |
| Développement | T01 | A04, A05 |
| Développement | T03 | A08, A09 |
| Développement | T06 | A15, A16 |
| Test final | T02 | A06, A07 |
| Test final | T04 | A10, A11 |
| Test final | T05 | A12, A13, A14 |

Les trois affirmations du premier essai restent dans le lot de développement, avec leurs reprises A01/A04 et A03/A15. Les textes restent entiers pour conserver le contexte des phrases. Les deux lots utilisent les mêmes 16 passages comme index de recherche. Le lot de test final est réservé à l’évaluation après le choix des réglages et des modèles.

| Lot | Appuyées | Contredites | Insuffisamment documentées | Total |
| --- | ---: | ---: | ---: | ---: |
| Développement | 3 | 3 | 3 | 9 |
| Test final | 4 | 2 | 1 | 7 |

Les 9 cas de développement correspondent à 7 affirmations distinctes une fois les deux reprises regroupées. Les 7 cas de test final proviennent de trois textes rédigés pour le projet, sur un seul thème et en français. Avec un seul cas insuffisamment documenté dans ce lot, les résultats sur ce statut devront être lus cas par cas.
