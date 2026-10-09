# DAX measures

All 22 measures of the report, with their original (French) names. Every gap is a **ratio of sums**: actual total minus planned total, divided by the planned total, in the current filter context. A long phase therefore weighs more than a short one, and a phase planned for a single day cannot distort a whole project.

## Costs (table `Actual_Costs`)

| Measure | Formula | What it returns |
| ------- | ------- | --------------- |
| `ecart_couts_%` | `DIVIDE(SUM(Actual_Costs[Actual_Cost]) - SUM(Projects_plans[Planned_Cost]), SUM(Projects_plans[Planned_Cost]), 0)` | Cost gap in % |
| `ecart_cout_valeur` | `SUM(Actual_Costs[Actual_Cost]) - SUM(Projects_plans[Planned_Cost])` | Cost gap in euros |
| `nmb_projets` | `DISTINCTCOUNT(Projects_plans[Project ID])` | Number of projects |
| `couts+15%` | `0 + COUNTROWS(FILTER(VALUES(Projects_plans[Project ID]), [ecart_couts_%] >= 0.15))` | Critical projects (15% or more over budget) |
| `couts_a_surveiller` | `0 + COUNTROWS(FILTER(VALUES(Projects_plans[Project ID]), [ecart_couts_%] >= 0 && [ecart_couts_%] < 0.15))` | Projects to watch |
| `couts-15%` | `0 + COUNTROWS(FILTER(VALUES(Projects_plans[Project ID]), [ecart_couts_%] < 0))` | Projects under budget |
| `Top_5` | `VAR RANG = RANKX(ALL(Projects_plans[Project ID]), [ecart_couts_%], , DESC) RETURN IF(RANG <= 5, 1, 0)` | Flags the five largest gaps in % |
| `Flop_5` | `VAR RANG = RANKX(ALL(Projects_plans[Project ID]), [ecart_couts_%], , ASC) RETURN IF(RANG <= 5, 1, 0)` | Flags the five lowest gaps in % |

`Top_5` and `Flop_5` are used as visual-level filters (value = 1) on the two tables at the bottom of the Costs page. Note that the names are crossed with the titles: the table titled "Top 5" (most under budget) is filtered with `Flop_5`, and the table titled "Flop 5" (largest overruns) with `Top_5`.

## Delays (table `Actual_Duration`)

| Measure | Formula | What it returns |
| ------- | ------- | --------------- |
| `ecart_delais_%` | `DIVIDE(SUM(Actual_Duration[Actual_Duration]) - SUM(Projects_plans[Planned_Duration]), SUM(Projects_plans[Planned_Duration]), 0)` | Delay gap in % |
| `ecart_delais_jours` | `SUM(Actual_Duration[Actual_Duration]) - SUM(Projects_plans[Planned_Duration])` | Delay gap in days |
| `taux_completion_delai` | `DIVIDE(SUM(Actual_Duration[Actual_Duration]), SUM(Projects_plans[Planned_Duration]), 0)` | Actual days as a share of planned days |
| `delais+15%` | `0 + COUNTROWS(FILTER(VALUES(Projects_plans[Project ID]), [ecart_delais_%] >= 0.15))` | Critical projects (15% or more late) |
| `delais_a_surveiller` | `0 + COUNTROWS(FILTER(VALUES(Projects_plans[Project ID]), [ecart_delais_%] >= 0 && [ecart_delais_%] < 0.15))` | Projects slightly late |
| `delais-15%` | `0 + COUNTROWS(FILTER(VALUES(Projects_plans[Project ID]), [ecart_delais_%] < 0))` | Projects ahead of plan |

## Deliverables (table `Actual_Delivrable`)

| Measure | Formula | What it returns |
| ------- | ------- | --------------- |
| `ecart_livrable_%` | `DIVIDE(SUM(Actual_Delivrable[Actual_Deliverables]) - SUM(Projects_plans[Planned_Delivrable]), SUM(Projects_plans[Planned_Delivrable]), 0)` | Deliverable gap in % (negative = under-delivery) |
| `taux_livraison_livrable` | `DIVIDE(SUM(Actual_Delivrable[Actual_Deliverables]), SUM(Projects_plans[Planned_Delivrable]), 0)` | Share of planned deliverables delivered |
| `livrables-15%` | `0 + COUNTROWS(FILTER(VALUES(Projects_plans[Project ID]), [ecart_livrable_%] <= -0.15))` | Critical projects (15% or more under) |
| `livrable_a_surveiller` | `0 + COUNTROWS(FILTER(VALUES(Projects_plans[Project ID]), [ecart_livrable_%] > -0.15 && [ecart_livrable_%] < 0))` | Projects slightly under |
| `livrable_livré` | `0 + COUNTROWS(FILTER(VALUES(Projects_plans[Project ID]), [ecart_livrable_%] >= 0))` | Projects that delivered everything |

The deliverable logic is inverted: a negative gap is bad.

## Map (table `cout_livra_delai_select`)

| Measure | Formula | What it returns |
| ------- | ------- | --------------- |
| `Ecart_KPI` | `SWITCH(SELECTEDVALUE(cout_livra_delai_select[KPI]), "Coûts", [ecart_couts_%], "Délais", [ecart_delais_%], "Livrables", [ecart_livrable_%] * -1, BLANK())` | Gap of the KPI chosen in the slicer, oriented so that higher is always worse (drives the map colours) |
| `Ecart_affichage_ KPI` | `SWITCH(SELECTEDVALUE(cout_livra_delai_select[KPI]), "Coûts", [ecart_couts_%], "Livrables", [ecart_livrable_%], "Délais", [ecart_delais_%], BLANK())` | The same gap with its real sign, for tooltips |
| `liste_projet` | `CONCATENATEX(Projects_Locations, Projects_Locations[Project ID], ", ")` | List of the project IDs in a country, for tooltips |

`cout_livra_delai_select` is a disconnected table with three rows (Coûts, Délais, Livrables): it only feeds the KPI slicer of the map.

## Why `0 +`

`COUNTROWS` of an empty table returns BLANK, so a card would show "(Blank)" when a filter leaves no critical project. Adding 0 turns it into 0.
