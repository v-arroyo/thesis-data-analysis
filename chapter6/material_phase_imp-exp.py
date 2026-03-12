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
SELECT
	temp_early,
    temp_late,
    social_group,
    CASE 
        WHEN m.material_local = 1 THEN 'local'
        WHEN m.material_imported = 1 THEN 'imported'
    END AS material_type,
    COUNT(*) AS total
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
JOIN materials m ON m.material_name = a.material
WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2,3,4
"""

df = pd.read_sql(query, engine)

custom_colors = ['#f27c8a',
                 '#e6f598',
                '#dcd8ff',
                '#e0aa82',
                '#65f3c6',
                '#92cef3',
                '#d3d3d3',
                '#e59fe2']

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
            'material_type': row['material_type'],
            'total': row['total']  # same count
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'material_type': row['material_type'],
                'total': row['total'] / len(phases)  # splits count evenly
            })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# calculate totals per (joined) phase and social group
phase_group_totals = df_expanded.groupby(['phase', 'social_group'])['total'].sum().reset_index()
phase_group_totals.rename(columns={'total': 'phase_group_total'}, inplace=True)

# merge phase totals and aggregate per material_type
df_grouped = df_expanded.merge(phase_group_totals, on=['phase', 'social_group'])
df_grouped = df_grouped.groupby(['phase', 'social_group', 'material_type', 'phase_group_total'], as_index=False)['total'].sum()

# percentages based on phase totals
df_grouped['percentage'] = round(df_grouped['total'] * 100.0 / df_grouped['phase_group_total'], 0)

# drop unneeded columns
df_grouped = df_grouped.drop(['total', 'phase_group_total'], axis=1)

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

# sort by phase and then type
df_grouped = df_grouped.sort_values(['phase', 'social_group', 'material_type'])

fig = px.line(
    df_grouped,
    x='phase',
    y='percentage',
    color='social_group',
    facet_row='material_type',
    text='percentage',
    markers=True,
    template="plotly_white",
    title='Distribution of local and imported amulet materials by social group and chronological phase (in %)',
    color_discrete_sequence=custom_colors,
    labels={"material_type" : "material"},
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

fig.update_traces(textposition='middle left', textfont_size=4)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/material_phase_imp-exp.png',scale=3, width=550, height=300)