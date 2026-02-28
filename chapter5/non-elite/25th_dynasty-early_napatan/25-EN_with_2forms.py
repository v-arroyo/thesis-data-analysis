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
    form,
    form2,
    COUNT(amulet_id) AS total
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
WHERE temp = '25th-EN'
    AND dating = 'napatan' 
    AND form2 IS NOT NULL
    AND form3 IS NULL
    AND b.site_id IN (4,5,6,7,8,9,10) 
    AND social_group = 'non-elite'
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

fig = px.scatter(
    df,
    x="form",
    y="form2",
    text='total',                 
    color_discrete_sequence=['#cccccc'],
    title="25th Dynasty-Early Napatan non-elite amulets combining two motifs",
    labels={"total": "Total"},
    size_max=20,
    template='plotly_white',
    category_orders={'form': sorted(df['form'].unique())}             
)

fig.update_layout(
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

fig.update_traces(textposition='top right', textfont_size=6)
fig.update_xaxes(title_text='', tickangle=45)
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/25-EN_with_2forms.png',scale=3, width=550, height=400)