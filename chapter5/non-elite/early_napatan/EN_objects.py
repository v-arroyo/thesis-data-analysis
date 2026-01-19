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
    artifact_type,
    count(artifact_id) as total
from burials b
join sites s on s.site_id = b.site_id
join artifacts a on a.burial_id = b.burial_id
where dating = 'napatan' 
    and b.site_id in (4,5,6,7,8,9,10) 
    and temp IN ('EN-MN')
    and social_group = 'non-elite'
group by 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

custom_order = ['EN', 'EN-MN']

order_mapping = {temp: idx for idx, temp in enumerate(custom_order)}
df['temp_order'] = df['temp'].map(order_mapping)

df_sorted = df.sort_values('temp_order')

fig = px.bar(
    df_sorted,
    x="total",
    y="artifact_type",
    color="site_name",
    text="total",
    facet_col='temp',
    title="Early Napatan and Early-Middle Napatan non-elite object types",
    labels={"site_name": "site", "temp": "phase", "total": "Total"},
    color_discrete_sequence=custom_colors,
    template="plotly_white")

fig.update_layout(yaxis={'categoryorder': 'total ascending'},
    legend=dict(
        #orientation="h",
        yanchor="middle",
        y=0.60,
        xanchor="center",
        x=1.10,
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
    title_font=dict(size=8),
    showlegend=False
)

fig.update_traces(textposition='outside', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/EN_objects_MN.png',scale=3, width=550, height=200)