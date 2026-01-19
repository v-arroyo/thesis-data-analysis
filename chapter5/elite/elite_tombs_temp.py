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
    super,
    sub,
    count(burial_id) as total
from burials b
join sites s on s.site_id = b.site_id
where dating = 'napatan' and b.site_id in (8,4,5) 
    AND (super = 'pyramid' OR sub IN ('chambers', 'cave tomb'))
group by 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

phase_order = [
    "pre-25th", "25th", "25th-EN", "25th-MN", "EN",
    "EN-MN", "EN-LN", "MN", "MN-LN", "LN"
]

sub_order = ["cave tomb", "pit", "chambers"]

fig = px.bar(
    df,
    x="temp",
    y="total",
    color='super',
    facet_row="sub",
    text="total",
    title="Elite tomb structures by chronological phase",
    color_discrete_sequence=custom_colors,
    category_orders={"temp": phase_order, "sub": sub_order},
    template="plotly_white"
)

fig.update_layout(
    xaxis={'categoryorder': 'total descending'},
    legend=dict(
        #orientation="h",
        yanchor="bottom",
        y=0.30,
        xanchor="center",
        x=1.10,
        traceorder='reversed'
    ),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8
    ),
    legend_title_text='',
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='auto', textfont_size=6)
fig.update_xaxes(title_text='', categoryorder='array', categoryarray=phase_order)
fig.update_yaxes(title_text='', matches=None)

pio.write_image(fig, 'images/chapter5/elite_tombs_temp.png',scale=3, width=550, height=350)