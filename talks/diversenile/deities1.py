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
WITH total_deities AS (
    SELECT 
        COUNT(amulet_id) AS total_count
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
        AND a.type = 'deity'
        AND a.form NOT IN ('deity', 'deities')
        AND social_group = 'non-elite'
)
SELECT
    b.social_group,
    CASE 
        WHEN form IN ('aker', 'amun', 'amun/isis/horus', 'amun/khonsu/monthu', 'amun/mut/khonsu', 'anubis', 'bastet', 'bes', 'duamutef', 'hapi', 
        'hapi, nile god', 'hathor', 'heh', 'horus', 'horus child', 'imsety', 'isis', 'isis and horus', 'khonsu', 'maat', 'min', 'mut', 'nefertum', 'neith', 
        'nephthys', 'onuris', 'osiris', 'pataikos', 'ptah', 'qebehsenuef', 'ra', 'ra-horakhty', 'sekhmet', 'shu', 'taweret', 'thoth', 'tefnut') 
            THEN 'deities from the egyptian pantheon'
    	WHEN form IN ('crocodile-headed deity', 'double hawk-headed deity', 'hawk-headed deity', 'isis nursing a queen', 'lion-headed deity',
        'lion-headed goddess', 'lion-headed goddess nursing horus', 'ram-headed deity', 'ram-headed dwarf', 'snake-headed deity', 'winged goddess',
        'winged lion-headed goddess', 'winged pataikos', 'winged ram-headed dwarf', 'hawk-headed dwarf') THEN 'local deities and/or adaptations'
        ELSE form
    END AS form,
    COUNT(amulet_id) AS deity_count,
    (SELECT total_count FROM total_deities) AS total_deities
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
WHERE dating = 'napatan' 
    AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
    AND a.type = 'deity'
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

# calculate percentage of deities relative to ALL amulets
df['percentage'] = round(df['deity_count'] * 100.0 / df['total_deities'], 2)

form_name_mapping = {
    'local deities and/or adaptations': 'local deities and/or<br>adaptations',
    'deities from the egyptian pantheon': 'deities from the<br>egyptian pantheon'
}

df['form'] = df['form'].map(form_name_mapping)

fig = px.bar(
    df,
    x='form',
    y='percentage',
    color='form',
    text=df['percentage'].round(1),
    template="plotly_white",
    title='Distribution of deity amulets (in %)',
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

pio.write_image(fig, 'talks/diversenile/images/deities1.png',scale=3, width=280, height=350)