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
    temp,
    material,
    count(amulet_id) as total
from burials b
join amulets a on a.burial_id = b.burial_id
join sites s on s.site_id = b.site_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10) and social_group = 'non-elite' and material != 'faience'
group by 1,2
"""

df = pd.read_sql(query, engine)

temp_order = ["pre-25th", "25th", "25th-EN", "25th-MN", "EN", "MN"]

df['temp'] = pd.Categorical(df['temp'], categories=temp_order, ordered=True)

df = df.sort_values('temp')

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x='material',
    y='total',
    text='total',
    color='temp',
    barmode='stack',
    title='Distribution of amulet materials by chronological phase (except faience)',
    template="plotly_white",
    color_discrete_sequence=custom_colors
)

fig.update_layout(xaxis={'categoryorder': 'total descending'},
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.17,
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

fig.update_traces(textposition='auto', textfont_size=5)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', matches=None)

pio.write_image(fig, 'images/msac/temp_mat.png',scale=3, width=650, height=500)