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
    region,
    form,
    count(amulet_id) as total
from burials b
join amulets a on a.burial_id = b.burial_id
join sites s on s.site_id = b.site_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10) and social_group = 'non-elite' and form in ('udjat', 'quadruple udjat')
group by 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686',
                 '#8b4513', '#2f4f4f', '#ff6b4a', '#20b2aa', '#daa520',
                 '#cd5c5c', '#4682b4', '#e8ea7a', '#98fb98', '#696969']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

df = df.sort_values('region')

fig = px.line(
    df,
    x='region',
    y='total',
    text='total',
    color='form',
    markers=True,
    title='Distribution of non-elite udjat and quadruple udjat amulets per region',
    template="plotly_white"
)

forms = df['form'].unique()
text_positions = ['top center', 'bottom center', 'top left', 'bottom right', 'middle right']

for i, form in enumerate(forms):
    fig.update_traces(
        textposition=text_positions[i % len(text_positions)],
        selector=dict(name=form)
    )

fig.update_layout( 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.50,
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

fig.update_traces(textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/region_udjat.png',scale=3, width=550, height=250)