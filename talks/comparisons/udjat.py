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
WITH all_amulets AS (
    SELECT 
        b.social_group,
        a.form,
        COUNT(*) AS form_count,
        SUM(COUNT(*)) OVER (PARTITION BY b.social_group) AS total_amulets
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
        AND b.social_group IS NOT NULL
    GROUP BY 1,2
)
SELECT 
    social_group,
    form,
    form_count AS udjat_count,
    total_amulets
FROM all_amulets
WHERE form = 'udjat'
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

df['percentage'] = round(df['udjat_count'] / df['total_amulets'] * 100, 1)

fig = px.bar(
    df,
    x='social_group',
    y='percentage',
    color='form',
    barmode='group',
    text=df['percentage'],
    template="plotly_white",
    title='Distribution of human amulets (in %)',
    color_discrete_sequence=custom_colors
)

fig.update_layout(xaxis={'categoryorder': 'total descending'},
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=10),
    legend_title_text='',
    title_font=dict(size=10),
    margin=dict(l=0, r=10, t=20, b=0)
)

fig.update_traces(textposition='outside', textfont_size=8)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'talks/comparisons/images/udjat.png',scale=3, width=550, height=550)