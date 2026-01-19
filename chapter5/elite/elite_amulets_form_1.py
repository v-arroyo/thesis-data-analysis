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
WITH expanded_forms AS (
    SELECT 
        b.temp,
        a.form AS form,
        a.amulet_id
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE 
        dating = 'napatan'
        AND b.site_id IN (4,5,8)
        AND a.form IS NOT NULL
        AND (super = 'pyramid' OR sub IN ('chambers', 'cave tomb'))
        AND type IN ('deity', 'symbol')

    UNION ALL

    SELECT 
        b.temp,
        a.form2 AS form,
        a.amulet_id
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE 
        dating = 'napatan'
        AND b.site_id IN (4,5,8)
        AND a.form2 IS NOT NULL
        AND (super = 'pyramid' OR sub IN ('chambers', 'cave tomb'))
        AND type IN ('deity', 'symbol')

    UNION ALL

    SELECT 
        b.temp,
        a.form3 AS form,
        a.amulet_id
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE 
        dating = 'napatan'
        AND b.site_id IN (4,5,8)
        AND a.form3 IS NOT NULL
        AND (super = 'pyramid' OR sub IN ('chambers', 'cave tomb'))
        AND type IN ('deity', 'symbol')
)
SELECT 
    temp,
    CASE 
        WHEN form = 'deity' THEN 'unknown deity'
        WHEN form = 'deities' THEN 'group of deities'
        ELSE form
    END AS form,
    COUNT(amulet_id) AS total
FROM expanded_forms
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

grey_smooth = [
    [0.0, '#e0e0e0'],  # Light grey
    [0.3, '#c8c8c8'],   # Medium light grey
    [0.5, '#a0a0a0'],   # Medium grey
    [0.7, '#787878'],   # Medium dark grey
    [0.85, '#505050'],  # Dark grey
    [1.0, '#282828']    # Very dark grey
]

phase_order = [
    "25th", "25th-EN", "EN",
    "EN-MN", "MN", "MN-LN", "LN"
]

pivot_df = df.pivot(index='form', columns='temp', values='total').fillna(0)
df_stacked = pivot_df.reset_index().melt(id_vars='form', var_name='temp', value_name='total')

fig = px.scatter(
    df,
    x="form",
    y="temp",
    color="total",
    text='total',                 
    color_continuous_scale='Sunset',
    title="Elite amulet types by chronological phase (deities and symbols)",
    labels={"total": "Total"},
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
fig.update_yaxes(title_text='', categoryorder='array', categoryarray=phase_order[::-1])

pio.write_image(fig, 'images/chapter5/elite_amulets_form_temp_1.png',scale=4, width=550, height=260)