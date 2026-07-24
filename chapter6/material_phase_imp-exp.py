import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import math
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

mat_query = """
    SELECT
        b.temp_early,
        b.temp_late,
        b.social_group,
        m.material_source1 AS source,
        COUNT(*) AS total
    FROM burials b
    JOIN amulets a ON a.burial_id = b.burial_id
    JOIN materials m ON m.material_name = a.material
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
        AND material != 'faience'
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

custom_colors = ['#C0C0C0']

phase_order = ["pre-25th", "25th", "EN", "MN", "LN"]

source_order = ["upper egypt", "eastern desert", "nile valley", "lower nubia", "eastern sudan", "red sea",
    "sub-saharan africa", "asia", "manufacturing"]

expanded_rows = []

# iterate over rows to find same phases (one row) or two phases (one row for each) then split evenly
for _, row in df_mat.iterrows():
    if row['temp_early'] == row['temp_late']:
        # single phase
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'source': row['source'],
            'total': row['total']
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'source': row['source'],
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
df_mat_grouped = df_expanded.groupby(['phase', 'social_group', 'source'], as_index=False)['total'].sum()

# merge both counts - materials and total amulets
df_final = df_mat_grouped.merge(df_total_grouped, on=['phase', 'social_group'])

# calculate percentage of materials relative to ALL amulets
df_final['percentage'] = round(df_final['total'] * 100.0 / df_final['total_amulets'], 2)

df_final['phase'] = pd.Categorical(df_final['phase'], categories=phase_order, ordered=True)

df_final['source'] = pd.Categorical(df_final['source'], categories=source_order, ordered=True)

df_final = df_final.sort_values(['phase', 'source'])

fig = px.scatter(
    df_final,
    x='source',
    y='phase',
    facet_row='social_group',
    text=df_final['percentage'].round(2),
    template="plotly_white",
    title='Distribution of local and imported amulet materials by social group and chronological phase (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"phase": phase_order, "social_group": ["royal", "elite", "non-elite"], "source": source_order}
)

fig.update_layout(
    legend=dict(
        orientation='h',
        yanchor="middle",
        y=-0.08,
        xanchor="center",
        x=0.40),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8)
)

for annotation in fig.layout.annotations:
    if annotation.text.startswith("social_group="):
        annotation.text = annotation.text.replace("social_group=", "")

fig.update_traces(textposition='middle right', textfont_size=5)
fig.update_yaxes(title='', matches=None)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/material_phase_imp-exp.png',scale=3, width=550, height=340)