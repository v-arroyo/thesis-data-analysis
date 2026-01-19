import pandas as pd
import plotly.express as px
import plotly.io as pio
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
WITH combined_data AS (
    SELECT b.sub, b.super, b.burial_id, a.artifact_id AS item_id, a.artifact_material AS material
    FROM artifacts a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE b.dating = 'napatan' 
        AND b.sub != 'deposit'
        AND a.artifact_type IN ('bead nets', 'burial containers', 'canopics', 'heart scarabs', 'mummy trappings', 'offering tables', 'offering vessels', 'stelae')
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
),
burial_totals AS (
    SELECT 
        sub, 
        super, 
        burial_id, 
        COUNT(item_id) as total_items
    FROM combined_data
    GROUP BY sub, super, burial_id
)
SELECT 
    sub, 
    super, 
    AVG(total_items) as median_total_items
FROM (
    SELECT
        sub,
        super,
        burial_id,
        total_items,
        ROW_NUMBER() OVER (PARTITION BY sub, super ORDER BY total_items) as row_num,
        COUNT(*) OVER (PARTITION BY sub, super) as total_count
    FROM burial_totals
) AS ranked
WHERE row_num IN (FLOOR((total_count + 1) / 2), CEIL((total_count + 1) / 2))
GROUP BY sub, super
ORDER BY sub, super;
"""

df = pd.read_sql(query, engine)

fig = px.scatter(
    df,
    x='sub',
    y='super',
    color='type',
    size='total',
    #text='total',
    title='<b>Distribution of burial-specific objects by tomb structure</b>',
    color_discrete_sequence=px.colors.qualitative.Plotly,
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
        x=0.40),
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

pio.write_image(fig, 'diversenile/images/burial_tombs.png',scale=4, width=550, height=250)