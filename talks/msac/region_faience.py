import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
select 
    region,
    count(amulet_id) as total_amulets,
    SUM(CASE WHEN material = 'faience' THEN 1 ELSE 0 END) AS faience_count,
    ROUND(SUM(CASE WHEN material = 'faience' THEN 1 ELSE 0 END) * 100.0 / COUNT(amulet_id), 0) AS faience_percentage
from burials b
join amulets a on a.burial_id = b.burial_id
join sites s on s.site_id = b.site_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10) and social_group = 'non-elite'
group by 1
"""

df = pd.read_sql(query, engine)

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

df = df.sort_values('region')

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x='region',
    y='faience_percentage',
    text='faience_percentage',
    barmode='group',
    title='Percentage of faience amulets by region (in %)',
    template="plotly_white",
    color_discrete_sequence=custom_colors
)

fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.50),
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

fig.update_traces(textposition='outside', textfont_size=8)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/msac/region_faience.png',scale=3, width=550, height=500)