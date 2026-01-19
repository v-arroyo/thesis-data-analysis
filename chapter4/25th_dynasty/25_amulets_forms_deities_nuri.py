import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
WITH expanded_forms AS (
    SELECT 
        s.site_name,
        b.owner,
        a.form AS form,
        a.amulet_id,
        a.type
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    JOIN sites s ON s.site_id = b.site_id
    WHERE 
        b.temp = '25th' 
        AND s.site_id IN (2)
        AND a.form IS NOT NULL
        AND a.type = 'deity'

    UNION ALL

    SELECT 
        s.site_name,
        b.owner,
        a.form2 AS form,
        a.amulet_id,
        a.type
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    JOIN sites s ON s.site_id = b.site_id
    WHERE 
        b.temp = '25th' 
        AND s.site_id IN (2)
        AND a.form2 IS NOT NULL
        AND a.type = 'deity'

    UNION ALL

    SELECT 
        s.site_name,
        b.owner,
        a.form3 AS form,
        a.amulet_id,
        a.type
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    JOIN sites s ON s.site_id = b.site_id
    WHERE 
        b.temp = '25th' 
        AND s.site_id IN (2)
        AND a.form3 IS NOT NULL
        AND a.type = 'deity'
)
SELECT 
    site_name,
    owner,
    form,
    type,
    COUNT(amulet_id) AS total
FROM expanded_forms
GROUP BY 1,2,3,4
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d','#d6d727','#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x="form",
    y="total",
    color="owner",
    facet_col="site_name",
    text='total',
    barmode='stack',
    title="25th Dynasty royal deity amulets",
    labels={"owner": "owner", "artifact_type": "obj. type", "site_name": "site"},
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(xaxis={'categoryorder': 'total descending'}, 
    legend=dict(
        #orientation="h",
        yanchor="bottom",
        y=0.30,
        xanchor="center",
        x=01.15,
        traceorder='reversed'),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=10, t=50, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='inside', textfont_size=6)
fig.update_xaxes(title_text='', matches=None)
fig.update_yaxes(title_text='', dtick=1)

pio.write_image(fig, 'images/chapter4/25_amulets_forms_deities_nuri.png',scale=3, width=500, height=200)