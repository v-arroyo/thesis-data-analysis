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
    social_group,
    a.type,
    count(amulet_id) as total
from burials b
join amulets a on a.burial_id = b.burial_id
join sites s on s.site_id = b.site_id
where dating = 'napatan' and b.site_id in (1,2,4,5,6,7,8,9,10) and social_group = 'elite'
group by 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3',
                 '#cd5c5c', '#4682b4', '#98fb98', '#696969']


df['type'] = pd.Categorical(df['type'], ordered=True)

df = df.sort_values('type')

fig = px.bar(
    df,
    x='region',
    y='total',
    color='type',
    text='total',
    barmode='group',
    facet_col='social_group',
    template="plotly_white",
    color_discrete_sequence=custom_colors
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=20, b=0),
    title_font=dict(size=8)
)

fig.update_traces(textposition='outside', textfont_size=6)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/region_type_elite.png',scale=3, width=550, height=250)