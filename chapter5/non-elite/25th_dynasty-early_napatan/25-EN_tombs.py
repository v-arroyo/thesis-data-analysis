import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
select 
	site_name,
    super,
    sub,
    count(burial_id) as total_burials
from burials b
join sites s on s.site_id = b.site_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10) and temp = '25th-EN' and social_group = 'non-elite' and sub != 'deposit'
group by 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.scatter(
    df,
    x="super",
    y="site_name",
    color="total_burials",
    facet_col='sub',
    text="total_burials",
    title="25th Dynasty-Early Napatan non-elite tomb structures",
    labels={"total_burials": "Total"},
    color_discrete_sequence='Sunset',
    template="plotly_white"
)

fig.update_layout(xaxis={'categoryorder': 'total descending'}, 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.12,
        xanchor="center",
        x=0.50),
        #traceorder='reversed'),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=50, b=0),
    autosize=True,
    title_font=dict(size=8),
    scattermode="group", 
    scattergap=0.1
)

fig.update_traces(textposition='middle right', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', categoryorder='category descending')

pio.write_image(fig, 'images/chapter5/25-EN_tombs.png',scale=3, width=550, height=250)