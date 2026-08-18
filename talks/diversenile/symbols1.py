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
WITH total_symbols AS (
    SELECT 
        COUNT(amulet_id) AS total_count
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (4,5,6,7,8,9,10)
        AND social_group = 'non-elite'
        AND a.type = 'symbol'
)
SELECT
    b.social_group,
    CASE 
        WHEN form IN ('horned lunar disc', 'lunar crescent') THEN 'moon-related symbols'
        WHEN form IN ('ankh', 'nefer', 'sa sign', 'sema sign', 'nt sign', 'nb sign', 'basket', 'arms') THEN 'hieroglyphic signs'
        WHEN form IN ('crook', 'was scepter', 'whip', 'uraeus', 'double uraeus', 'hmhm crown', 'double feather') THEN 'royal symbols'
        WHEN form IN ('akhet', 'sun boat', 'sun disc', 'horned sun disc') THEN 'sun-related symbols'
        WHEN form IN ('ba bird', 'double ba bird') THEN 'single/double ba bird'
        WHEN form IN ('winged griffin', 'winged scarab', 'winged snake', 'winged uraeus') THEN 'winged motifs'
        WHEN form IN ('sphinx') THEN 'sphinx'
        WHEN form IN ('menat', 'heart', 'djed', 'isis knot') THEN 'common symbols'
        WHEN form IN ('lion-headed uraeus', 'ram-headed sphinx') THEN 'symbols with animal heads'
        ELSE form
    END AS form,
    COUNT(amulet_id) AS symbol_count,
    (SELECT total_count FROM total_symbols) AS total_symbols
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
WHERE dating = 'napatan' 
    AND b.site_id IN (4,5,6,7,8,9,10) 
    AND a.type = 'symbol' 
    AND social_group = 'non-elite'
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = [ '#F28C28', # cadmium orange,
                '#8A9A5B', # sage green
                '#7393B3', # blue grey
                '#FFD700', # gold
                '#A95C68', # puce (red)
                '#40E0D0', # turquoise
                '#4169E1', # royal blue
                '#CCCCFF', # periwinkle (light purple)
                '#F28C28', # cadmium orange
                '#FF69B4', # hot pink
                '#BF40BF', # bright purple
]

# calculate percentage of symbols relative to ALL amulets
df['percentage'] = round(df['symbol_count'] * 100.0 / df['total_symbols'], 2)

fig = px.bar(
    df,
    x='form',
    y='percentage',
    color='form',
    text=df['percentage'].round(2),
    template="plotly_white",
    title='Distribution of symbol amulets (in %)',
    color_discrete_sequence=custom_colors
)

fig.update_layout(xaxis={'categoryorder': 'total descending'},
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=10),
    legend_title_text='',
    title_font=dict(size=10),
    margin=dict(l=0, r=10, t=20, b=0),
    showlegend=False
)

fig.update_traces(textposition='outside', textfont_size=8)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'talks/diversenile/images/symbols1.png',scale=3, width=400, height=400)