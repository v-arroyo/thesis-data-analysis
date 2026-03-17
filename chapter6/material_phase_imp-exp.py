import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

mat_query = """
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

total_amulets_query = """
SELECT 
    b.temp_early, 
    b.temp_late,
    b.social_group,
    COUNT(amulet_id) AS total_amulets
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
WHERE b.dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2,3
"""

df_mat = pd.read_sql(mat_query, engine)
df_total = pd.read_sql(total_amulets_query, engine)

custom_colors = ['#8A9A5B', # sage green
                '#7393B3', # blue grey
                '#FFD700', # gold
                '#A95C68', # puce (red)
                '#40E0D0', # turquoise
                '#FF69B4', # hot pink
                '#4169E1', # royal blue
                '#CCCCFF', # periwinkle (light purple)
                '#F28C28', # cadmium orange
                '#BF40BF', # bright purple
]

phase_order = ["pre-25th", "25th", "EN", "MN", "LN"]

expanded_rows = []

# iterate over rows to find same phases (one row) or two phases (one row for each) then split evenly
for _, row in df_mat.iterrows():
    if row['temp_early'] == row['temp_late']:
        # single phase
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'material_type': row['material_type'],
            'total': row['total']
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'material_type': row['material_type'],
                'total': row['total'] / len(phases)
            })

df_expanded = pd.DataFrame(expanded_rows)

# iterate over all amulets
total_expanded_rows = []

for _, row in df_total.iterrows():
    if row['temp_early'] == row['temp_late']:
        total_expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'total_amulets': row['total_amulets']
        })
    else:
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            total_expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'total_amulets': row['total_amulets'] / len(phases)
            })

df_total_expanded = pd.DataFrame(total_expanded_rows)

# aggregate TOTAL amulets by phase and social group
df_total_grouped = df_total_expanded.groupby(['phase', 'social_group'])['total_amulets'].sum().reset_index()

# aggregate materials by phase and social group
df_mat_grouped = df_expanded.groupby(['phase', 'social_group', 'material_type'], as_index=False)['total'].sum()

# merge both counts - materials and total amulets
df_final = df_mat_grouped.merge(df_total_grouped, on=['phase', 'social_group'])

# calculate percentage of materials relative to ALL amulets
df_final['percentage'] = round(df_final['total'] * 100.0 / df_final['total_amulets'], 2)

df_final['phase'] = pd.Categorical(df_final['phase'], categories=phase_order, ordered=True)

df_final = df_final.sort_values(['phase', 'social_group', 'material_type'])

fig = px.line(
    df_final,
    x='phase',
    y='percentage',
    color='social_group',
    facet_row='material_type',
    #text=df_final['percentage'].round(0),
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

pio.write_image(fig, 'images/chapter6/material_phase_imp-exp.png',scale=3, width=550, height=250)