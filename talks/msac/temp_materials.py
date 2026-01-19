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
    b.temp,
    CASE 
        WHEN m.material_local = 1 THEN 'local'
        WHEN m.material_imported = 1 THEN 'imported'
    END as material_type,
    COUNT(*) as count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY b.temp),
        0
    ) as percentage
FROM amulets a
JOIN materials m ON m.material_name = a.material
JOIN burials b ON b.burial_id = a.burial_id
WHERE dating = 'napatan' 
    AND b.site_id IN (4,5,6,7,8,9,10) 
    AND social_group = 'non-elite'
    AND (m.material_local = 1 OR m.material_imported = 1)
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686',
                 '#8b4513', '#2f4f4f', '#ff6b4a', '#20b2aa', '#daa520',
                 '#cd5c5c', '#4682b4', '#e8ea7a', '#98fb98', '#696969']

temp_order = ["MN", "EN", "25th-MN", "25th-EN", "25th", "pre-25th"]

df['temp'] = pd.Categorical(df['temp'], categories=temp_order, ordered=True)

df = df.sort_values('temp')

fig = px.bar(
    df,
    x='percentage',
    y='temp',
    text='percentage',
    color='material_type',
    barmode='group',
    title='Distribution of imported and local materials by chronological phase (in %)',
    template="plotly_white",
    color_discrete_sequence=custom_colors
)

fig.update_layout(
    legend=dict(
        traceorder='reversed'), 
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=10, t=50, b=0),
    title_font=dict(size=8),
)

fig.update_traces(textposition='outside', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/msac/temp_materials.png',scale=3, width=550, height=300)