# Data model

A star schema centred on the plan. `Projects_plans` holds one row per project and phase (520 rows): what was planned. Three tables hold what actually happened, three tables describe the projects.

| From (many) | To (one) | Key | Cardinality | Cross-filter |
| ----------- | -------- | --- | ----------- | ------------ |
| Projects_plans | Actual_Costs | `Project ID - Phase` | 1:1 | Both |
| Projects_plans | Actual_Duration | `Project ID - Phase` | 1:1 | Both |
| Projects_plans | Actual_Delivrable | `Project ID - Phase` | 1:1 | Both |
| Projects_plans | Project type | `Project ID` | many to one | Both |
| Projects_plans | Projects_Locations | `Project ID` | many to one | Both |
| Projects_Locations | Country_Profiles | `Country` | many to one | Both |

`cout_livra_delai_select` (three rows: Coûts, Délais, Livrables) has no relationship: it only feeds the KPI slicer of the map page.

## The composite key

A plan row and its actual row only match on a project **and** a phase, so Power Query adds the same column to the four tables:

```m
Table.AddColumn(#"Colonnes renommées", "Project ID - Phase", each Text.From([Project ID]) & "-" & [Phase])
```

Each of the 520 keys exists once in each table, so the plan-to-actual relationships are one-to-one.

## Cross-filtering

All relationships filter both ways, so that every slicer updates the others: choosing a project ID narrows the region, country and type slicers, and the other way round. On a larger model, I would keep the dimension relationships one-way (from the dimension to the plan) and use the bidirectional setting only where it is needed, to avoid ambiguous filter paths.

## Row-Level Security

| Role | Filter on `Country_Profiles` |
| ---- | ---------------------------- |
| Directeur Régional WE | `[Region] == "Western Europe"` |
| Directeur Régional CEMEA | `[Region] == "Central/Eastern Europe-Middle East-Africa"` |
| Directeur Régional NLA | `[Region] == "North and Latin America"` |
| Directeur Régional AP | `[Region] == "Asia Pacific"` |
| Directeur Pays France | `[Country] == "France"` |
| Directeur Pays Japon | `[Country] == "Japon"` |
| Directeur Pays Canada | `[Country] == "Canada"` |

The CEO has no role, so no filter: they see the 104 projects. Three country roles are set up as examples; the same pattern extends to the 52 countries. To test a role in Power BI Desktop: *Modeling → View as → choose the role*.
