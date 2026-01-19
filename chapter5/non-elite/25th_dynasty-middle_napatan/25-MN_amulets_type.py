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
    count(amulet_id) as total
from burials b
join sites s on s.site_id = b.site_id
join amulets a on a.burial_id = b.burial_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10) and temp = '25th-MN'
    and super != 'pyramid' 
    and sub not in ('chambers', 'cave tomb')
group by 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#C0C0C0']

fig = px.bar(
    df,
    x="type",
    y="total",
    color="site_name",
    text="total",
    barmode='stack',
    title="25th Dynasty-Middle Napatan non-elite amulet types",
    labels={"super": "superstructure", "sub": "substructure", "site_name": "site"},
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(xaxis={'categoryorder': 'total descending'}, 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=0.54,
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
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8),
    showlegend=False
)

fig.update_traces(textposition='auto', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/25-MN_amulets_type.png',scale=3, width=550, height=200)