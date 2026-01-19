import pandas as pd
import plotly.express as px
import plotly.io as pio
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
WITH inscribed_items AS (
    -- Get inscribed artifacts
    SELECT
        a.artifact_id AS item_id,
        b.sub,
        b.super
    FROM artifacts a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE b.dating = 'napatan' 
        AND b.sub != 'deposit'
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
        AND a.artifact_inscribed = 1
    
    UNION ALL
    
    -- Get inscribed amulets
    SELECT
        am.amulet_id AS item_id,
        b.sub,
        b.super
    FROM amulets am
    JOIN burials b ON b.burial_id = am.burial_id
    WHERE b.dating = 'napatan' 
        AND b.sub != 'deposit'
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
        AND am.inscribed = 1
)

SELECT
    sub,
    super,
    COUNT(item_id) AS total
FROM inscribed_items
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

fig = px.scatter(
    df,
    x='sub',
    y='super',
    size='total',
    #text='total',
    title='<b>Distribution of inscribed objects by tomb structure</b>',
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

pio.write_image(fig, 'diversenile/images/inscribed_tomb.png',scale=4, width=450, height=250)