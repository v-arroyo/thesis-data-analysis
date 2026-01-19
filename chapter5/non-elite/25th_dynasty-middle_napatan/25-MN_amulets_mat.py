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
    material,
    count(amulet_id) as total
from burials b
join sites s on s.site_id = b.site_id
join amulets a on a.burial_id = b.burial_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10) and material IS NOT NULL and temp = '25th-MN'
    and super != 'pyramid' and sub not in ('chambers', 'cave tomb')
group by 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#C0C0C0']

fig = px.bar(
    df,
    x="total",
    y="material",
    color="site_name",
    text="total",
    barmode='stack',
    title="25th Dynasty-Middle Napatan non-elite amulet materials",
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(yaxis=dict(categoryorder='total ascending', automargin=True, title_standoff=0), 
    legend=dict(
        #orientation="h",
        yanchor="bottom",
        y=0.43,
        xanchor="center",
        x=0.80,
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

fig.update_traces(textposition='outside', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/25-MN_amulets_mat.png',scale=3, width=550, height=150)