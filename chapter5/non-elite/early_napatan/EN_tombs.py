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
    temp,
    super,
    sub,
    count(burial_id) as total
from burials b
join sites s on s.site_id = b.site_id
where dating = 'napatan' 
    and b.site_id in (4,5,6,7,8,9,10) 
    and temp IN ('EN', 'EN-MN')
    and social_group = 'non-elite'
group by 1,2,3,4
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

custom_order = ['EN', 'EN-MN']

order_mapping = {temp: idx for idx, temp in enumerate(custom_order)}
df['temp_order'] = df['temp'].map(order_mapping)

df_sorted = df.sort_values('temp_order')

fig = px.bar(
    df_sorted,
    x="super",
    y="total",
    color="site_name",
    barmode='group',
    facet_col='sub',
    facet_row='temp',
    text="total",
    title="Early Napatan and Early-Middle Napatan non-elite tomb structures",
    labels={"site_name": "site", "temp": "phase"},
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(xaxis={'categoryorder': 'total descending'}, 
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
    margin=dict(l=0, r=10, t=40, b=0),
    autosize=True,
    title_font=dict(size=8),
)

fig.update_traces(textposition='auto', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', matches=None)

pio.write_image(fig, 'images/chapter5/EN_tombs.png',scale=3, width=550, height=250)