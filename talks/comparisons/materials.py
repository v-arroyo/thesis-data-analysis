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
WITH total_amulets AS (
    SELECT 
        b.social_group,
        COUNT(amulet_id) AS total_count
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    GROUP BY 1
)
SELECT
    b.social_group,
    m.material_source1 AS source,
    COUNT(amulet_id) AS materials_count,
    t.total_count AS total_amulets
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
JOIN materials m ON m.material_name = a.material
JOIN total_amulets t ON t.social_group = b.social_group
WHERE dating = 'napatan' 
    AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
    AND a.material != 'faience' 
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = [ '#F28C28', # cadmium orange,
                '#8A9A5B', # sage green
                '#7393B3', # blue grey
                '#FFD700', # gold
                '#A95C68', # puce (red)
                '#40E0D0', # turquoise
                '#4169E1', # royal blue
                '#CCCCFF', # periwinkle (light purple)
                '#F28C28', # cadmium orange
                '#FF69B4', # hot pink
                '#BF40BF', # bright purple
]

# calculate percentage of materials relative to ALL amulets
df['percentage'] = round(df['materials_count'] * 100.0 / df['total_amulets'], 1)

source_order = ["upper egypt", "eastern desert", "nile valley", "lower nubia", "eastern sudan", "red sea", "sub-saharan africa", "asia", "manufacturing"]

fig = px.bar(
    df,
    x='social_group',
    y='percentage',
    text=df['percentage'],
    color='source',
    barmode='group',
    template="plotly_white",
    title='Distribution of materials by source (excl. faience) (in %)',
    subtitle='n=660',
    color_discrete_sequence=custom_colors,
    category_orders={"source": source_order}
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=10),
    legend_title_text='',
    title_font=dict(size=10),
    margin=dict(l=0, r=10, t=30, b=0)
)

fig.update_traces(textposition='outside', textfont_size=8)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'talks/comparisons/images/materials.png',scale=3, width=550, height=550)