import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

deities_query = """
WITH forms AS (
    SELECT
        a.amulet_id,
        b.temp_early, 
        b.temp_late,
        b.social_group,
        COALESCE(a.form2, a.form) AS form
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
        AND a.type = 'deity' 
        AND b.social_group IS NOT NULL
        AND (a.form IS NOT NULL OR a.form2 IS NOT NULL)
)

SELECT 
    temp_early, 
    temp_late,
    social_group,
    CASE 
        WHEN form IN ('aker', 'amun', 'amun/isis/horus', 'amun/khonsu/monthu', 'amun/mut/khonsu', 'anubis', 'bastet', 'bes', 'duamutef', 'hapi', 
        'hapi, nile god', 'hathor', 'heh', 'horus', 'horus child', 'imsety', 'isis', 'isis and horus', 'khonsu', 'maat', 'min', 'mut', 'nefertum', 'neith', 
        'nephthys', 'onuris', 'osiris', 'pataikos', 'ptah', 'qebehsenuef', 'ra', 'ra-horakhty', 'sekhmet', 'shu', 'taweret', 'thoth', 'tefnut') 
            THEN 'deities from the egyptian pantheon'
    	WHEN form IN ('crocodile-headed deity', 'double hawk-headed deity', 'hawk-headed deity', 'hawk-headed dwarf', 'isis nursing a queen', 'lion-headed deity',
        'lion-headed goddess', 'lion-headed goddess nursing horus', 'ram-headed deity', 'ram-headed dwarf', 'snake-headed deity', 'winged goddess',
        'winged lion-headed goddess', 'winged pataikos', 'winged ram-headed dwarf') THEN 'local deities and/or adaptations'
        ELSE form
    END AS form,
    COUNT(amulet_id) AS total
FROM forms
WHERE form NOT IN ('deity', 'deities')
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
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
GROUP BY 1,2,3
"""

df_deities = pd.read_sql(deities_query, engine)
df_total = pd.read_sql(total_amulets_query, engine)

custom_colors = [ '#7393B3', # blue grey 
                '#F28C28', # cadmium orange,
                '#8A9A5B', # sage green
                '#FFD700', # gold
                '#A95C68', # puce (red)
                '#40E0D0', # turquoise
                '#4169E1', # royal blue
                '#CCCCFF', # periwinkle (light purple)
                '#F28C28', # cadmium orange
                '#FF69B4', # hot pink
                '#BF40BF', # bright purple
]

phase_order = ["pre-25th", "25th", "EN", "MN", "LN"]

expanded_rows = []

# iterate over rows to find same phases (one row) or two phases (one row for each) then split evenly -- deities
for _, row in df_deities.iterrows():
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

# aggregate deities by phase, social group, and form
df_deities_grouped = df_expanded.groupby(['phase', 'social_group', 'form'], as_index=False)['total'].sum()

# merge both counts - deities and total amulets
df_final = df_deities_grouped.merge(df_total_grouped, on=['phase', 'social_group'])

# calculate percentage of deities relative to ALL amulets
df_final['percentage'] = round(df_final['total'] * 100.0 / df_final['total_amulets'], 2)

form_name_mapping = {
    'local deities and/or adaptations': 'local deities and/or adaptations',
    'deities from the egyptian pantheon': 'deities from the egyptian pantheon'
}

df_final['form'] = df_final['form'].map(form_name_mapping)

df_final['phase'] = pd.Categorical(df_final['phase'], categories=phase_order, ordered=True)

df_final = df_final.sort_values('phase')

print(df_final)

fig = px.bar(
    df_final,
    x='percentage',
    y='phase',
    color='form',
    #text='percentage',
    facet_row='social_group',
    template="plotly_white",
    barmode='stack',
    title='Distribution of deity amulets by social group and chronological phase (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"phase": phase_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(
    legend=dict(
        orientation='h',
        yanchor="middle",
        y=-0.13,
        xanchor="center",
        x=0.40),
        #traceorder='reversed'),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    title_font=dict(size=8),
    margin=dict(l=0, r=10, t=20, b=0)
)

for annotation in fig.layout.annotations:
    if annotation.text.startswith("social_group="):
        annotation.text = annotation.text.replace("social_group=", "")

fig.update_yaxes(title='', matches=None)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/motifs_phase_deities2.png',scale=3, width=550, height=250)