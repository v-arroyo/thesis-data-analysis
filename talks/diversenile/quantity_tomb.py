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
    SELECT b.sub, b.super, b.burial_id, a.artifact_id AS item_id
    FROM artifacts a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE b.dating = 'napatan' 
        AND b.sub != 'deposit'
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    UNION ALL
    SELECT b.sub, b.super, b.burial_id, am.amulet_id AS item_id
    FROM amulets am
    JOIN burials b ON b.burial_id = am.burial_id
    WHERE b.dating = 'napatan' 
        AND b.sub != 'deposit'
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
),
burial_totals AS (
    SELECT sub, super, burial_id, COUNT(item_id) as total_items
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

custom_colors = ['#92cad1','#e9724d', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x='super',
    y='median_total_items',
    color='sub',
    text='median_total_items',
    barmode='group',
    title='<b>Median number of objects by tomb structure</b>',
    color_discrete_sequence=custom_colors,
    template="plotly_white",
    labels={"total": "Total"},
)

fig.update_xaxes(title_text='substructures', title_font=dict(size=8))
fig.update_yaxes(title_text='superstructures', title_font=dict(size=8))

fig.update_layout(
    xaxis={'categoryorder': 'total descending'}, 
    # legend=dict(
    #     orientation="h",
    #     yanchor="top",
    #     y=-0.10,
    #     xanchor="center",
    #     x=0.50),
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

fig.update_traces(textposition='auto', textfont_size=6)

pio.write_image(fig, 'diversenile/images/quantity_tomb.png',scale=4, width=480, height=190)