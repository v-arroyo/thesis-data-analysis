import pandas as pd
import plotly.express as px
import plotly.io as pio
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
SELECT
    b.sub,
    b.super,
    COUNT(b.burial_id) AS total
FROM burials b
WHERE dating = 'napatan' 
AND sub != 'deposit'
AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

fig = px.scatter(
    df,
    x='sub',
    y='super',
    text='total',
    title='<b>Correlation of tomb super- and substructures</b>',
    color_discrete_sequence=['#C0C0C0'],
    template="plotly_white",
)

fig.update_xaxes(title_text='substructures', title_font=dict(size=8))
fig.update_yaxes(title_text='superstructures', title_font=dict(size=8))

fig.update_layout(
    yaxis={'categoryorder': 'total ascending'}, 
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.10,
        xanchor="center",
        x=0.50),
        #traceorder='reversed'),
    font=dict(
        family="Verdana, sans-serif",
        color="black",
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=10)
    )

fig.update_traces(textposition='top right', textfont_size=6)

pio.write_image(fig, 'diversenile/images/tombs.png',scale=4, width=450, height=250)