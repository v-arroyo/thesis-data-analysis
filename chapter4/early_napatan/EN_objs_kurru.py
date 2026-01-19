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
    a.artifact_type,
    COUNT(artifact_id) as count
FROM burials b
JOIN sites s
ON s.site_id = b.site_id
JOIN artifacts a
ON a.burial_id = b.burial_id
WHERE temp = 'EN' AND b.site_id IN (1)
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#92cad1', '#e9724d','#d6d727', '#79ccb3', '#868686']

fig = px.scatter(
    df,
    x="owner",
    y="artifact_type",
    color="count",
    text="count",
    facet_col="site_name",
    title="Early Napatan royal object types",
    labels={"count": "Total", "site_name": "Site"},
    color_continuous_scale='Sunset',
    template="plotly_white"
)

fig.update_layout( 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.70,
        xanchor="center",
        x=0.45,
        traceorder='reversed'),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=10, t=40, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='middle right', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', categoryorder='category descending')
fig.update_coloraxes(showscale=False)

pio.write_image(fig, 'images/chapter4/early_objs_kurru.png',scale=3, width=250, height=350)