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
SELECT 
    social_group,
    CASE 
        WHEN form = 'deity' THEN 'unknown deity'
        WHEN form = 'deities' THEN 'group of deities'
        ELSE form
    END AS form,
    CASE 
        WHEN form2 = 'deity' THEN 'unknown deity'
        WHEN form2 = 'deities' THEN 'group of deities'
        ELSE form2
    END AS form2,
    COUNT(amulet_id) AS total
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
WHERE temp IN ('25th', '25th-EN') AND dating = 'napatan' AND form2 IS NOT NULL
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

social_order = ['royal', 'elite', 'non-elite']

pivot_df = df.pivot(index='form', columns='form2', values='total').fillna(0)

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
    x="form",
    y="form2",
    color="total",
    text='total',                 
    color_continuous_scale=grey_smooth,
    title="Correlation of forms",
    labels={"total": "Total"},
    size_max=20,
    template='plotly_white'   ,
    category_orders={'social_group': social_order}                  
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
    title_font=dict(size=8),
    coloraxis=dict(
        colorbar=dict(
            tickfont=dict(size=7),
            title_font=dict(size=7)
        )
    )
)

fig.update_traces(textposition='top center', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter6/forms.png',scale=4, width=550, height=550)