import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
import numpy as np

engine = create_engine(f'mysql+pymysql://{os.getenv"DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
select 
	temp,
    artifact_type,
    count(artifact_id) as total
from burials b
join sites s on s.site_id = b.site_id
join artifacts a on a.burial_id = b.burial_id
where dating = 'napatan' and b.site_id in (8,4,5) 
    AND (super = 'pyramid' OR sub IN ('chambers', 'cave tomb'))
    and artifact_type != 'beads'
group by 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686', '#2c3e50', '#a85d3a', '#9b8fd4', '#8a9a5b', '#d4a5a5', '#4a4a4a']

phase_order = [
    "pre-25th", "25th", "25th-EN", "25th-MN", "EN",
    "EN-MN", "EN-LN", "MN", "MN-LN", "LN"
]

pivot_df = df.pivot(index='artifact_type', columns='temp', values='total').fillna(0)
df_stacked = pivot_df.reset_index().melt(id_vars='artifact_type', var_name='temp', value_name='total')

fig = px.scatter(
    df,
    x="artifact_type",
    y="temp",
    color="total",                   
    color_continuous_scale='Sunset',
    title="Artifact Counts by Category",
    size_max=20,
    template='plotly_white'                     
)

fig.update_layout(
    xaxis={'categoryorder': 'total descending'},
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.15,
        xanchor="center",
        x=0.50,
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

fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', categoryorder='array', categoryarray=phase_order[::-1])

pio.write_image(fig, 'images/chapter5/elite_objects_temp.png',scale=3, width=450, height=250)