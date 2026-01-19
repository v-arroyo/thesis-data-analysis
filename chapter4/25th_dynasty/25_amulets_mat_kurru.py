import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
SELECT 
    s.site_name,
    b.owner,
    CASE
        WHEN a.material = 'lapis' THEN 'lapis lazuli'
        ELSE a.material
    END AS material,
    COUNT(amulet_id) as count
FROM burials b
JOIN sites s
ON s.site_id = b.site_id
JOIN amulets a
ON a.burial_id = b.burial_id
WHERE temp = '25th' AND b.site_id IN (1) AND a.material IS NOT NULL
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x="count",
    y="material",
    color="owner",
    facet_col="site_name",
    text='count',
    barmode='stack',
    title="25th Dynasty royal amulet materials",
    labels={"owner": "owner", "artifact_type": "obj. type", "site_name": "site"},
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(yaxis={'categoryorder': 'total ascending'}, 
    legend=dict(
        #orientation="h",
        yanchor="bottom",
        y=0.30,
        xanchor="center",
        x=1.10),
        #traceorder='reversed'),
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

fig.update_traces(textposition='outside', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter4/25_amulets_mat_kurru.png',scale=3, width=550, height=250)