import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
select 
	temp,
    artifact_type,
    count(artifact_id) as total
from burials b
join artifacts a on a.burial_id = b.burial_id
where dating = 'napatan' and b.site_id in (8,4,5) 
    AND (super = 'pyramid' OR sub IN ('chambers', 'cave tomb'))
group by 1,2
"""

df = pd.read_sql(query, engine)

phase_order = [
    "25th", "25th-EN", "25th-MN", "EN",
    "EN-MN", "MN", "MN-LN", "LN"
]

pivot_df = df.pivot(index='artifact_type', columns='temp', values='total').fillna(0)
df_stacked = pivot_df.reset_index().melt(id_vars='artifact_type', var_name='temp', value_name='total')

grey_smooth = [
    [0.0, '#e0e0e0'],  # Light grey
    [0.3, '#c8c8c8'],   # Medium light grey
    [0.5, '#a0a0a0'],   # Medium grey
    [0.7, '#787878'],   # Medium dark grey
    [0.85, '#505050'],  # Dark grey
    [1.0, '#282828']    # Very dark grey
]

fig = px.scatter(
    df,
    x="artifact_type",
    y="temp",
    color="total",                   
    color_continuous_scale='Sunset',
    title="Elite object types by chronological phase",
    labels={"total": "Total"},
    size_max=20,
    template='plotly_white'                     
)

fig.update_layout(
    xaxis={'categoryorder': 'total descending'},
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.15,
        xanchor="center",
        x=0.50,
        traceorder='reversed'
    ),
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8),
    coloraxis=dict(
        colorbar=dict(
            tickfont=dict(size=7),
            title_font=dict(size=7)
        )
    )
)

fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', categoryorder='array', categoryarray=phase_order[::-1])

pio.write_image(fig, 'images/chapter5/elite_objects_temp.png',scale=4, width=450, height=250)