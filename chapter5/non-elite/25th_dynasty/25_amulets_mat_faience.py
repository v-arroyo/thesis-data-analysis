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
where dating = 'napatan' 
    and b.site_id in (4,5,6,7,8,9,10) 
    and social_group = 'non-elite'
    and material = 'faience'
    and temp = '25th'
group by 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x="material",
    y="total",
    color="site_name",
    text="total",
    barmode='group',
    title="25th Dynasty non-elite faience amulets",
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(yaxis=dict(categoryorder='total descending', automargin=True, title_standoff=0), 
    legend=dict(
        #orientation="h",
        yanchor="bottom",
        y=0.40,
        xanchor="center",
        x=0.80,
        traceorder='reversed'),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=6),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=0, t=15, b=0),
    autosize=True,
    title_font=dict(size=6)
)

fig.update_traces(textposition='outside', textfont_size=6, width=0.2)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/25_amulets_mat_faience.png',scale=4, width=200, height=250)