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
SELECT 
    s.region,
    a.form
FROM amulets a
JOIN burials b ON a.burial_id = b.burial_id
JOIN sites s ON a.site_id = s.site_id
WHERE b.dating = 'napatan' 
    AND b.social_group = 'non-elite'
    AND a.form2 IS NULL
GROUP BY s.region, a.form
HAVING NOT EXISTS (
    SELECT 1
    FROM amulets a2
    JOIN burials b2 ON a2.burial_id = b2.burial_id
    JOIN sites s2 ON a2.site_id = s2.site_id
    WHERE a2.form = a.form
        AND s2.region != s.region
        AND b2.dating = 'napatan' 
        AND b2.social_group = 'non-elite'
        AND a2.form2 IS NULL
)
ORDER BY 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#E4C8B8', '#E8D8B8', '#B8C8B4', '#D8D8F0']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]
df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)
df_sorted = df.sort_values(['region', 'form'])

df_count = df_sorted.groupby(['region', 'form']).size().reset_index(name='count')

fig = px.sunburst(
    df_count,
    path=['region', 'form'],
    values='count',
    color='region',
    color_discrete_sequence=custom_colors,
    title='Exclusive non-elite amulet motifs by region',
    template="plotly_white"
)

fig.update_layout( 
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=10),
    margin=dict(l=0, r=10, t=50, b=0),
    title_font=dict(size=10)
)

fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/region_forms.png',scale=4, width=300, height=300)