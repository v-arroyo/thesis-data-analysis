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
        s.region,
        b.social_group,
        COALESCE(a.form2, a.form) AS form
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    JOIN sites s ON s.site_id = a.site_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
        AND a.type = 'deity' 
        AND b.social_group IS NOT NULL
)

SELECT 
    region,
    social_group,
    CASE 
        WHEN form IN ('aker', 'amun', 'amun/isis/horus', 'amun/khonsu/monthu', 'amun/mut/khonsu', 'anubis', 'bastet', 'bes', 'duamutef', 'hapi', 
        'hapi, nile god', 'hathor', 'heh', 'horus', 'horus child', 'imsety', 'isis', 'isis and horus', 'khonsu', 'maat', 'min', 'mut', 'nefertum', 'neith', 
        'nephthys', 'onuris', 'osiris', 'pataikos', 'ptah', 'qebehsenuef', 'ra', 'ra-horakhty', 'sekhmet', 'shu', 'taweret', 'thoth', 'tefnut') 
            THEN 'deities from the egyptian pantheon'
    	WHEN form IN ('crocodile-headed deity', 'double hawk-headed deity', 'hawk-headed deity', 'isis nursing a queen', 'lion-headed deity',
        'lion-headed goddess', 'lion-headed goddess nursing horus', 'ram-headed deity', 'ram-headed dwarf', 'snake-headed deity', 'winged goddess',
        'winged lion-headed goddess', 'winged pataikos', 'winged ram-headed dwarf') THEN 'local deities and/or adaptations'
        ELSE form
    END AS form,
    COUNT(amulet_id) AS total
FROM forms
GROUP BY 1,2,3
"""

total_amulets_query = """
SELECT 
    s.region,
    b.social_group,
    COUNT(amulet_id) AS total_amulets
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
JOIN sites s ON s.site_id = b.site_id
WHERE b.dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2
"""

df_deities = pd.read_sql(deities_query, engine)
df_total = pd.read_sql(total_amulets_query, engine)

custom_colors = [ '#F28C28', # cadmium orange
                '#8A9A5B', # sage green
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

# aggregate TOTAL amulets by region and social group
df_total_grouped = df_total.groupby(['region', 'social_group'])['total_amulets'].sum().reset_index()

# aggregate region by phase, social group, and form
df_deities_grouped = df_deities.groupby(['region', 'social_group', 'form'], as_index=False)['total'].sum()

# merge both counts - region and total amulets
df_final = df_deities_grouped.merge(df_total_grouped, on=['region', 'social_group'])

# calculate percentage of deities relative to ALL amulets
df_final['percentage'] = round(df_final['total'] * 100.0 / df_final['total_amulets'], 2)

form_name_mapping = {
    'deities from the egyptian pantheon': 'deities from the egyptian pantheon',
    'local deities and/or adaptations': 'local deities and/or adaptations'
}

df_final['form'] = df_final['form'].map(form_name_mapping)

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df_final['region'] = pd.Categorical(df_final['region'], categories=region_order, ordered=True)

df_final = df_final.sort_values('region')

print(df_final)

fig = px.bar(
    df_final,
    x='percentage',
    y='region',
    #text=df_final['percentage'].round(1),
    color='form',
    facet_row='social_group',
    template="plotly_white",
    barmode='stack',
    title='Distribution of deity amulets by social group and region (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"region": region_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(
    legend=dict(
        orientation='h',
        yanchor="middle",
        y=-0.15,
        xanchor="center",
        x=0.40),
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

fig.update_traces(textposition='auto', textfont_size=3)
fig.update_yaxes(title='', matches=None)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/motifs_region_deities.png',scale=3, width=550, height=250)