import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

rest_query = """
WITH expanded_forms AS (
    SELECT
        a.amulet_id,
        b.temp_early, 
        b.temp_late,
        b.social_group,
        a.form as form
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
        AND a.type NOT IN ('deity', 'symbol', 'animal', 'nature', 'human')
        AND a.form IS NOT NULL
        AND b.social_group IS NOT NULL

    UNION ALL

    SELECT
        a.amulet_id,
        b.temp_early, 
        b.temp_late,
        b.social_group,
        a.form2 as form
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
        AND a.form2 IS NOT NULL
        AND b.social_group IS NOT NULL

    UNION ALL

    SELECT
        a.amulet_id,
        b.temp_early, 
        b.temp_late,
        b.social_group,
        a.form3 as form
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
        AND a.form3 IS NOT NULL
        AND b.social_group IS NOT NULL
)

SELECT
    temp_early, 
    temp_late,
    social_group,
    CASE
        WHEN form IN ('vase', 'libation bucket', 'jar') THEN 'vessels'
        WHEN form IN ('headrest', 'offering table') THEN 'funerary objects'
        WHEN form IN ('amulet case') THEN 'amulet cases'
        WHEN form IN ('axe head', 'dovetail', 'sistrum', 'harpoon') THEN 'professional objects'
        WHEN form IN ('cartouche') THEN 'written motifs'
        WHEN form IN ('nugget', 'pillar', 'tablet', 'incised cylinder', 'pebble') THEN 'non-figurative motifs'
        ELSE form
    END AS form,
    COUNT(amulet_id) as total
FROM expanded_forms
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

df_rest = pd.read_sql(rest_query, engine)
df_total = pd.read_sql(total_amulets_query, engine)

custom_colors = ['#8A9A5B', # sage green
                '#7393B3', # blue grey
                '#A95C68', # puce (red)
                '#40E0D0', # turquoise
                '#4169E1', # royal blue
                '#CCCCFF', # periwinkle (light purple)
                '#F28C28', # cadmium orange
                '#FF69B4', # hot pink
                '#BF40BF', # bright purple
                '#FFD700', # gold
]

phase_order = ["pre-25th", "25th", "EN", "MN", "LN"]

expanded_rows = []

# iterate over rows to find same phases (one row) or two phases (one row for each) then split evenly -- rest
for _, row in df_rest.iterrows():
    if row['temp_early'] == row['temp_late']:
        # single phase
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'form': row['form'],
            'total': row['total']
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'form': row['form'],
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

# aggregate rest by phase, social group, and form
df_rest_grouped = df_expanded.groupby(['phase', 'social_group', 'form'], as_index=False)['total'].sum()

# merge both counts - rest and total amulets
df_final = df_rest_grouped.merge(df_total_grouped, on=['phase', 'social_group'])

# calculate percentage of rest relative to ALL amulets
df_final['percentage'] = round(df_final['total'] * 100.0 / df_final['total_amulets'], 3)

form_name_mapping = {
    'vessels': 'vessels',
    'funerary objects': 'funerary objects',
    'amulet cases': 'amulet cases',
    'professional objects': 'professional objects',
    'written motifs': 'written motifs',
    'non-figurative motifs': 'non-figurative motifs',
}

df_final['form'] = df_final['form'].map(form_name_mapping)

df_final['phase'] = pd.Categorical(df_final['phase'], categories=phase_order, ordered=True)

df_final = df_final.sort_values('phase')

fig = px.bar(
    df_final,
    x='percentage',
    y='phase',
    color='form',
    #text=df_final['percentage'].round(2),
    facet_row='social_group',
    template="plotly_white",
    barmode='stack',
    title='Distribution of object and miscellaneous amulets by social group and chronological phase (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"phase": phase_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=6),
    legend_title_text='',
    title_font=dict(size=6),
    margin=dict(l=0, r=10, t=20, b=0),
    legend=dict(
        traceorder='reversed')
)

fig.update_traces(textposition='outside', textfont_size=4)
fig.update_yaxes(title='', matches=None)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/motifs_phase_obj-others.png',scale=3, width=550, height=250)