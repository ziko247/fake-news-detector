# Mini-corpus de vérification sur le recensement marocain

Ce corpus de démarrage porte sur la population légale du Maroc et son évolution entre deux recensements. Les quatre passages ci-dessous sont les seules entrées du corpus. Les trois affirmations servent à vérifier le fonctionnement du parcours.

## Sources et préparation

| Source | Publication | Passage à consulter |
| --- | --- | --- |
| S1 | [HCP, Population légale du Royaume du Maroc selon le RGPH 2024](https://www.hcp.ma/Population-legale-du-Royaume-du-Maroc-repartie-par-regions-provinces-et-prefectures-et-communes-selon-les-resultats-du_a3975.html) | Un accroissement démographique en baisse |
| S2 | [HCP, Indicateurs sociaux, p. 15](https://www.hcp.ma/file/244142/#page=15) | Population, tendance intercensitaire |

Le HCP autorise la réutilisation de ses indicateurs selon les conditions de la licence CC BY 4.0, sauf indication contraire. Les passages ci-dessous reformulent les indicateurs en phrases courtes et normalisent l’écriture des nombres sans changer les valeurs, les unités ou les périodes. [Conditions d’utilisation du HCP, section 3](https://www.hcp.ma/Conditions-generales-d-utilisation-Version-1-0_a2194.html) · [Licence CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Passages à indexer

| ID | Texte | Source |
| --- | --- | --- |
| P01 | Le recensement de 2024 a établi la population légale du Maroc à 36 828 330 habitants au 1er septembre 2024. | S1 |
| P02 | Entre les recensements de 2014 et de 2024, la population légale du Maroc a augmenté de 2 980 088 habitants. | S1 |
| P03 | En 2024, la population du Maroc comptait 23 110 108 habitants en milieu urbain et 13 718 222 en milieu rural. | S1 |
| P04 | Le taux d’accroissement démographique annuel moyen du Maroc était de 1,25 % entre 2004 et 2014 et de 0,85 % entre 2014 et 2024. | S2 |

## Cas annotés à la main

| ID | Affirmation à vérifier | Statut attendu | Passage et extrait source | Justification |
| --- | --- | --- | --- | --- |
| A01 | Au 1er septembre 2024, le Maroc comptait 36 828 330 habitants selon le recensement. | Appuyée par les sources | P01 · « la population légale du Royaume a atteint 36.828.330 habitants au 1er septembre 2024 » · [S1](https://www.hcp.ma/Population-legale-du-Royaume-du-Maroc-repartie-par-regions-provinces-et-prefectures-et-communes-selon-les-resultats-du_a3975.html) | La source donne le même chiffre à la même date. |
| A02 | Le taux d’accroissement annuel moyen de la population du Maroc était plus élevé entre 2014 et 2024 qu’entre 2004 et 2014. | Contredite | P04 · « 0,85% entre 2014 et 2024 nettement inférieur au taux de 1,25% enregistré entre 2004 et 2014 » · [S2, p. 15](https://www.hcp.ma/file/244142/#page=15) | Le taux a diminué de 1,25 % à 0,85 %. |
| A03 | Au 1er septembre 2023, le Maroc comptait exactement 36 millions d’habitants. | Insuffisamment documentée | Aucun passage probant parmi P01 à P04. | Les passages donnent des valeurs de recensement et une moyenne sur dix ans. Il manque une estimation ou un dénombrement daté du 1er septembre 2023. |

Pour le premier essai BM25, indexer uniquement P01 à P04 et utiliser les affirmations comme requêtes. Sur quatre passages, examiner surtout le premier résultat et le rang de P01 ou P04 pour les deux cas documentés. Pour A03, un résultat proche sur le plan lexical ne suffit pas à justifier un statut positif ou négatif. Ces trois cas servent de test de fonctionnement avant une évaluation sur un corpus plus large.
