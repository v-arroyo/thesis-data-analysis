import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

mat_query = """
SELECT
    s.region,
    b.social_group,
    a.material,
    COUNT(a.amulet_id) as total
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
JOIN sites s ON s.site_id = b.site_id
WHERE dating = 'napatan' 
    AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    AND a.material IN ('obsidian', 'ivory', 'gold', 'lapis', 'electrum', 'silver')
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

# aggregate TOTAL amulets by region and social group
df_total_grouped = df_total.groupby(['region', 'social_group'])['total_amulets'].sum().reset_index()

# aggregate materials by region and social group
df_mat_grouped = df_mat.groupby(['region', 'social_group', 'material'], as_index=False)['total'].sum()

# merge both counts - materials and total amulets
df_final = df_mat_grouped.merge(df_total_grouped, on=['region', 'social_group'])

# calculate percentage of materials relative to ALL amulets
df_final['percentage'] = round(df_final['total'] * 100.0 / df_final['total_amulets'], 2)

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df_final['region'] = pd.Categorical(df_final['region'], categories=region_order, ordered=True)

df_final = df_final.sort_values('region')

fig = px.line(
    df_final,
    x="region",
    y="percentage",
    facet_row="social_group",
    color='material',
    markers=True,
    title="Distribution of selected materials by social group and region (in %)",
    color_discrete_sequence=custom_colors,
    template="plotly_white",
    category_orders={"region": region_order, "social_group": ["royal", "elite", "non-elite"]}
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

fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', matches=None)

pio.write_image(fig, 'images/chapter6/material_region_special.png',scale=3, width=550, height=350)