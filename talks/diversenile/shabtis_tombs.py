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
    a.artifact_type AS type,
    b.sub,
    b.super,
    COUNT(b.burial_id) AS total
FROM burials b
JOIN artifacts a ON a.burial_id = b.burial_id
WHERE dating = 'napatan' 
    AND sub != 'deposit'
    AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    AND artifact_type IN ('shabtis')
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

fig = px.scatter(
    df,
    x='sub',
    y='super',
    color='total',
    size='total',
    #text='total',
    title='<b>Distribution of shabtis by tomb structure</b>',
    color_continuous_scale='Sunset',
    template="plotly_white",
)

#fig.update_traces(textposition='outside')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

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
    margin=dict(l=0, r=10, t=50, b=0),
    autosize=True,
    title_font=dict(size=8)
    )

pio.write_image(fig, 'diversenile/images/shabtis_tombs.png',scale=4, width=400, height=280)