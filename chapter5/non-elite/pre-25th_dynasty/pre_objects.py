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
    artifact_type,
    count(artifact_id) as total
from burials b
join sites s on s.site_id = b.site_id
join artifacts a on a.burial_id = b.burial_id
where dating = 'napatan' 
    and b.site_id in (4,5,6,7,8,9,10) 
    and temp = 'pre-25th'
    and social_group = 'non-elite'
group by 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.scatter(
    df,
    x="site_name",
    y="artifact_type",
    color="total",
    text="total",
    title="Pre-25th Dynasty non-elite object types",
    labels={"total": "Total"},
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
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='top right', textfont_size=6)
fig.update_xaxes(title_text='', categoryorder='category ascending')
fig.update_yaxes(title_text='', categoryorder='category descending')

pio.write_image(fig, 'images/chapter5/pre_objects.png',scale=3, width=430, height=250)