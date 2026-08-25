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
    s.region,
    b.social_group,
    m.material_source1 AS source,
    COUNT(*) AS total
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
JOIN materials m ON m.material_name = a.material
JOIN sites s ON s.site_id = b.site_id
WHERE dating = 'napatan' 
    AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
    AND material != 'faience'
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

df_mat = pd.read_sql(mat_query, engine)
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

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

source_order = ["upper egypt", "eastern desert", "nile valley", "lower nubia", "eastern sudan", "red sea", "sub-saharan africa", "asia", "manufacturing"]

# aggregate TOTAL amulets by region and social group
df_total_grouped = df_total.groupby(['region', 'social_group'])['total_amulets'].sum().reset_index()

# aggregate materials by region and social group
df_mat_grouped = df_mat.groupby(['region', 'social_group', 'source'], as_index=False)['total'].sum()

# merge both counts - materials and total amulets
df_final = df_mat_grouped.merge(df_total_grouped, on=['region', 'social_group'])

# calculate percentage of materials relative to ALL amulets
df_final['percentage'] = round(df_final['total'] * 100.0 / df_final['total_amulets'], 1)

df_final['region'] = pd.Categorical(df_final['region'], categories=region_order, ordered=True)

df_final['source'] = pd.Categorical(df_final['source'], categories=source_order, ordered=True)

print(df_final)

fig = px.scatter(
    df_final,
    x='source',
    y='region',
    color='social_group',
    facet_row='social_group',
    text=df_final['percentage'],
    template="plotly_white",
    title='Distribution of local and imported amulet materials by social group and region (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"region": region_order, "social_group": ["royal", "elite", "non-elite"], "source": source_order}
)

fig.update_layout(
    legend=dict(
        orientation='h',
        yanchor="middle",
        y=-0.28,
        xanchor="center",
        x=0.45),
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

fig.update_traces(textposition='middle right', textfont_size=7, marker_size=10)
fig.update_yaxes(title='', matches=None)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/material_region_imp-exp.png',scale=3, width=550, height=280)