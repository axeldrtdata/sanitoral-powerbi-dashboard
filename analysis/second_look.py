"""Recompute the dashboard's key figures from the exported tables, and the three checks of the second look.

Run from the repository root:  python analysis/second_look.py
"""
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

DATA = Path(__file__).resolve().parent.parent / 'data'
KEY = 'Project ID - Phase'

plans = pd.read_csv(DATA / 'Projects_plans.csv')
costs = pd.read_csv(DATA / 'Actual_Costs.csv')
durations = pd.read_csv(DATA / 'Actual_Duration.csv')
deliverables = pd.read_csv(DATA / 'Actual_Delivrable.csv')
types = pd.read_csv(DATA / 'Project_type.csv')
locations = pd.read_csv(DATA / 'Projects_Locations.csv')
countries = pd.read_csv(DATA / 'Country_Profiles.csv')

# One row per project and phase, plan next to reality (the 1:1 relationships of the model)
phases = (
    plans.merge(costs[[KEY, 'Actual_Cost']], on=KEY)
    .merge(durations[[KEY, 'Actual_Duration']], on=KEY)
    .merge(deliverables[[KEY, 'Actual_Deliverables']], on=KEY)
    .merge(types, on='Project ID')
    .merge(locations, on='Project ID')
    .merge(countries, on='Country')
)
phases['Type'] = phases['Project Type'].str.split(' - ').str[0]

# Gaps are ratios of sums, as in the DAX measures
projects = phases.groupby('Project ID').agg(
    type=('Type', 'first'), country=('Country', 'first'), region=('Region', 'first'),
    planned_cost=('Planned_Cost', 'sum'), actual_cost=('Actual_Cost', 'sum'),
    planned_days=('Planned_Duration', 'sum'), actual_days=('Actual_Duration', 'sum'),
    planned_deliv=('Planned_Delivrable', 'sum'), actual_deliv=('Actual_Deliverables', 'sum'),
)
projects['cost_gap'] = projects.actual_cost / projects.planned_cost - 1
projects['delay_gap'] = projects.actual_days / projects.planned_days - 1
projects['deliv_gap'] = projects.actual_deliv / projects.planned_deliv - 1

print('== Portfolio')
planned, actual = phases.Planned_Cost.sum(), phases.Actual_Cost.sum()
print(f'{len(projects)} projects, {phases.Country.nunique()} countries, {phases.Region.nunique()} regions')
print(f'Cost: planned €{planned:,.0f}, actual €{actual:,.0f}, gap €{actual - planned:,.0f} ({actual / planned - 1:+.2%})')
c = projects.cost_gap
print(f'Cost status: {(c >= .15).sum()} critical, {((c >= 0) & (c < .15)).sum()} to watch, {(c < 0).sum()} under plan')
d = projects.delay_gap
print(f'Delay status: {(d >= .15).sum()} critical, {((d >= 0) & (d < .15)).sum()} to watch, {(d < 0).sum()} ahead')
v = projects.deliv_gap
print(f'Deliverable status: {(v <= -.15).sum()} critical, {((v > -.15) & (v < 0)).sum()} to watch, {(v >= 0).sum()} complete')
print(f'Deliverables delivered: {phases.Actual_Deliverables.sum() / phases.Planned_Delivrable.sum():.2%}')

print('\n== By region')
by_region = projects.groupby('region').agg(
    projects=('type', 'size'), planned=('planned_cost', 'sum'), actual=('actual_cost', 'sum'),
    critical=('cost_gap', lambda s: (s >= .15).sum()),
)
by_region['gap_%'] = (by_region.actual / by_region.planned - 1).round(3)
by_region['overrun_€'] = by_region.actual - by_region.planned
print(by_region[['projects', 'gap_%', 'overrun_€', 'critical']])

print('\n== Second look 1: percent against euros')
projects['overrun'] = projects.actual_cost - projects.planned_cost
print('Five worst in %:\n', projects.nlargest(5, 'cost_gap')[['type', 'country', 'cost_gap', 'overrun']])
print('Five worst in €:\n', projects.nlargest(5, 'overrun')[['type', 'country', 'cost_gap', 'overrun']])

print('\n== Second look 2: IT phases')
it = phases[phases.Type == 'IT']
it_phases = it.groupby('Phase')[['Planned_Cost', 'Actual_Cost']].sum()
it_phases['gap'] = it_phases.Actual_Cost / it_phases.Planned_Cost - 1
print(it_phases)
testing = it[it.Phase == 'Phase D - Testing']
deployment = it[it.Phase == 'Phase E - Deployment']
print(f'Testing over plan in {(testing.Actual_Cost > testing.Planned_Cost).sum()} of {len(testing)} IT projects')
print(f'Deployment under plan in {(deployment.Actual_Cost < deployment.Planned_Cost).sum()} of {len(deployment)} IT projects')
rest = it[it.Phase != 'Phase E - Deployment']
print(f'IT without Deployment: {rest.Actual_Cost.sum() / rest.Planned_Cost.sum() - 1:+.0%}')

print('\n== Second look 3: delays and costs')
late = projects.delay_gap >= .15
print(f'Critically late projects over budget: {(projects[late].cost_gap > 0).sum()} of {late.sum()}')
print(f'Other projects over budget: {(projects[~late].cost_gap > 0).sum()} of {(~late).sum()}')
rho, p = spearmanr(projects.cost_gap, projects.delay_gap)
print(f'Spearman correlation between cost gap and delay gap: rho = {rho:.2f} (p = {p:.2f})')
