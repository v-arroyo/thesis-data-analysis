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
select
	region,
    social_group,
    CASE 
        WHEN m.material_local = 1 THEN 'local'
        WHEN m.material_imported = 1 THEN 'imported'
    END as material_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY social_group), 0) as percentage
from burials b
join amulets a ON a.burial_id = b.burial_id
JOIN materials m ON m.material_name = a.material
JOIN sites s ON s.site_id = b.site_id
where dating = 'napatan' and b.site_id in (1,2,4,5,6,7,8,9,10)
group by 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686',
                 '#8b4513', '#2f4f4f', '#ff6b4a', '#20b2aa', '#daa520',
                 '#cd5c5c', '#4682b4', '#e8ea7a', '#98fb98', '#696969']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

df = df.sort_values('region')

fig = px.line(
    df,
    x='region',
    y='percentage',
    #text='percentage',
    color='social_group',
    facet_row='material_type',
    #facet_col_wrap=2,
    markers=True,
    template="plotly_white",
    title='Distribution of local and imported amulet materials by social group and region',
    color_discrete_sequence=custom_colors,
    labels={"material_type" : "material"}
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=50, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='bottom center', textfont_size=5)
fig.update_yaxes(title='', dtick=20)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/material_region_type.png',scale=3, width=550, height=370)