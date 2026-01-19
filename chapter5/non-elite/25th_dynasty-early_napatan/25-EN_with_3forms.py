import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
SELECT 
    site_name,
    form,
    form2,
    form3,
    COUNT(amulet_id) AS total
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
join sites s on s.site_id = b.site_id
WHERE temp = '25th-EN'
    AND dating = 'napatan' 
    AND form2 IS NOT NULL
    AND form3 IS NOT NULL
    AND b.site_id IN (4,5,6,7,8,9,10) 
    AND social_group = 'non-elite'
GROUP BY 1,2,3,4
"""

df = pd.read_sql(query, engine)

fig = px.treemap(df, 
                path=['form', 'form2', 'form3'], 
                values='total',
                title="25th Dynasty-Early Napatan non-elite amulets combining three motifs",
                template='plotly_white'
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
        size=6
    ),
    legend_title_text='',
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8),
    treemapcolorway=px.colors.qualitative.Pastel
)

fig.update_traces(marker=dict(cornerradius=5))
fig.update_traces(textposition='top left', textfont_size=6)

pio.write_image(fig, 'images/chapter5/25-EN_with_3forms.png',scale=4, width=450, height=300)