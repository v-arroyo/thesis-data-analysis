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
WHERE temp = '25th' AND b.site_id IN (1)
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.scatter(
    df,
    x="owner",
    y="artifact_type",
    color="count",
    text="count",
    facet_col="site_name",
    title="25th Dynasty royal object types",
    labels={"count": "Total", "site_name": "site"},
    color_continuous_scale='Sunset',
    template="plotly_white"
)

fig.update_layout( 
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    margin=dict(l=0, r=10, t=40, b=0),
    title_font=dict(size=8),
)

fig.update_xaxes(
    title_text='',
    categoryorder='category ascending',
    range=[-0.2, len(df['owner'].unique())-0.1],  # Tight range
    showgrid=True
)

fig.update_coloraxes(showscale=False)

fig.update_traces(textposition='middle right', textfont_size=6)
fig.update_xaxes(title_text='', categoryorder='category ascending')
fig.update_yaxes(title_text='', categoryorder='category descending')

pio.write_image(fig, 'images/chapter4/25_objs_kurru.png',scale=3, width=300, height=400)