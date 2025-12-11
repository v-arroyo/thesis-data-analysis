import pandas as pd
import plotly.express as px
import plotly.io as pio
from sqlalchemy import create_engine

engine = create_engine(f'mysql+pymysql://{os.getenv"DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
WITH combined_data AS (
    SELECT
        b.sub,
        b.super,
        a.artifact_id AS item_id,
        'artifact' AS item_type
    FROM artifacts a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND sub != 'deposit'
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    
    UNION ALL
    
    SELECT
        b.sub,
        b.super,
        am.amulet_id AS item_id,
        'amulet' AS item_type
    FROM amulets am
    JOIN burials b ON b.burial_id = am.burial_id
    WHERE dating = 'napatan' 
        AND sub != 'deposit'
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
)
SELECT
    sub,
    super,
    COUNT(DISTINCT item_id) AS total
FROM combined_data
GROUP BY 1, 2
"""

df = pd.read_sql(query, engine)

fig = px.scatter(
    df,
    x='sub',
    y='super',
    size='total',
    #text='total',
    title='<b>Distribution of quantity of objects by tomb structure</b>',
    color_discrete_sequence=['#C0C0C0'],
    template="plotly_white",
    labels={"total": "Total"},
)

#fig.update_traces(textposition='outside')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

fig.update_layout(
    xaxis={'categoryorder': 'total descending'}, 
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

pio.write_image(fig, 'diversenile/images/quantity_tomb.png',scale=3, width=400, height=280)