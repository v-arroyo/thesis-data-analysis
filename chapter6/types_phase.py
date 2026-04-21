import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
WITH total_counts AS (
    SELECT 
    	b.temp_early,
    	b.temp_late,
    	b.social_group,
    	COUNT(amulet_id) as group_total
    FROM amulets a
	JOIN burials b ON b.burial_id = a.burial_id
	WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
	GROUP BY 1,2,3
)
SELECT
	b.temp_early,
    b.temp_late,
    b.social_group,
    a.type,
    tc.group_total,
    COUNT(*) as type_total
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
JOIN total_counts tc ON tc.social_group = b.social_group AND tc.temp_early = b.temp_early AND tc.temp_late = b.temp_late
WHERE dating = 'napatan' AND b.site_id in (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2,3,4,5
"""

df = pd.read_sql(query, engine)

custom_colors = ['#f27c8a',
                 '#e6f598',
                '#dcd8ff',
                '#e0aa82',
                '#65f3c6',
                '#92cef3',
                '#d3d3d3',
                '#e59fe2',
                '#aec6cf',
                '#ffb347']

phase_order = ["pre-25th", "25th", "EN", "MN", "LN"]

# empty list to store
expanded_rows = []

# iterate over rows to find same phases (one row) or two phases (one row for each)
for _, row in df.iterrows():
    if row['temp_early'] == row['temp_late']:
        # single phase
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'type': row['type'],
            'group_total': row['group_total'],
            'type_total': row['type_total']  # same count
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'type': row['type'],
                'group_total': row['group_total'] / len(phases),
                'type_total': row['type_total'] / len(phases)  # splits count evenly
            })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# calculate totals per (joined) phase AND social group
phase_group_totals = df_expanded.groupby(['phase', 'social_group'])['type_total'].sum().reset_index()
phase_group_totals.rename(columns={'type_total': 'phase_group_total'}, inplace=True)

# merge totals back to aggregate by form_source
df_grouped = df_expanded.merge(phase_group_totals, on=['phase', 'social_group'])
df_grouped = df_grouped.groupby(['phase', 'social_group', 'type', 'phase_group_total'], as_index=False)['type_total'].sum()

# percentage based on phase
df_grouped['percentage'] = round(df_grouped['type_total'] * 100.0 / df_grouped['phase_group_total'], 2)

# drop unneeded columns
df_grouped = df_grouped.drop(['type_total', 'phase_group_total'], axis=1)

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

df_grouped = df_grouped.sort_values('phase')

print(df_grouped)

fig = px.bar(
    df_grouped,
    x='percentage',
    y='phase',
    color='type',
    facet_row='social_group',
    template="plotly_white",
    title='Distribution of amulet types by social group and chronological phase (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"phase": phase_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_yaxes(title='', matches=None)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/types_phase.png',scale=3, width=550, height=350)