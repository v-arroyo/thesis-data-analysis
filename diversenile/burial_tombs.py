import pandas as pd
import plotly.express as px
import plotly.io as pio
from sqlalchemy import create_engine

engine = create_engine(f'mysql+pymysql://{os.getenv"DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

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
    AND artifact_type IN ('bead nets', 'burial containers', 'canopics', 'heart scarabs', 'mummy trappings', 'offering tables', 'offering vessels', 'stelae')
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

fig = px.scatter(
    df,
    x='sub',
    y='super',
    color='type',
    size='total',
    #text='total',
    title='<b>Distribution of objects for the burial by tomb structure</b>',
    color_discrete_sequence=px.colors.qualitative.Plotly,
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

pio.write_image(fig, 'diversenile/images/burial_tombs.png',scale=4, width=550, height=300)