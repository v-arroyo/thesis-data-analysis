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
    type,
    temp,
    count(amulet_id) as total
from burials b
join sites s on s.site_id = b.site_id
join amulets a on a.burial_id = b.burial_id
where dating = 'napatan' 
    and b.site_id in (4,5,6,7,8,9,10) 
    and temp in ('EN', 'EN-MN')
    and social_group = 'non-elite'
group by 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#C0C0C0']

custom_order = ['EN', 'EN-MN']

order_mapping = {temp: idx for idx, temp in enumerate(custom_order)}
df['temp_order'] = df['temp'].map(order_mapping)

df_sorted = df.sort_values('temp_order')

fig = px.scatter(
    df_sorted,
    x="temp",
    y="type",
    color="total",
    text="total",
    facet_col='site_name',
    title="Early Napatan and Early-Middle Napatan non-elite amulet types",
    labels={"site_name": "site", "temp": "phase", "total": "Total"},
    color_continuous_scale='Sunset',
    template="plotly_white"
)

fig.update_layout(
    legend=dict(
        #orientation="h",
        yanchor="middle",
        y=0.60,
        xanchor="center",
        x=0.75,
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

fig.update_traces(textposition='middle right', textfont_size=6)
fig.update_xaxes(title_text='', matches=None)
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/EN_amulets_type.png',scale=3, width=350, height=200)