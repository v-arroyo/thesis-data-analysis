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
    b.social_group,
    a.type,
    COUNT(*) AS type_count
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
WHERE b.dating = 'napatan' 
    AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    AND b.social_group IS NOT NULL
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#f27c8a',
                 '#e6f598',
                '#dcd8ff',
                '#e0aa82',
                '#65f3c6',
                '#92cef3',
                '#d3d3d3',
                '#e59fe2',
                '#aec6cf',
                '#ffb347']

df['percentage'] = df.groupby('social_group')['type_count'].transform(lambda x: (x / x.sum() * 100).round(1))

fig = px.bar(
    df,
    x='social_group',
    y='percentage',
    text=df['percentage'],
    color='type',
    barmode='group',
    template="plotly_white",
    title='Distribution of amulet categories (in %)',
    color_discrete_sequence=custom_colors,
)

fig.update_layout(xaxis={'categoryorder': 'total descending'},
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=10),
    legend_title_text='',
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=10)
)

fig.update_traces(textposition='outside', textfont_size=8)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'talks/comparisons/images/categories.png',scale=3, width=550, height=450)