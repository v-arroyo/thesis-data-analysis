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
WITH total_counts AS (
    SELECT 
    	b.social_group, 
    	s.region, 
    	COUNT(amulet_id) as group_total
    FROM amulets a
	JOIN burials b ON b.burial_id = a.burial_id
	JOIN sites s ON s.site_id = b.site_id
	WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
	GROUP BY 1,2
)
SELECT
    s.region,
    b.social_group,
    CASE 
        WHEN a.form IN ('aker', 'amun', 'amun/isis/horus', 'amun/khonsu/monthu', 'amun/mut/khonsu',
        'anubis', 'bastet', 'bes', 'duamutef', 'hapi', 'hapi, nile god', 'hathor', 'heh', 
        'horus', 'horus child', 'imsety', 'isis', 'isis and horus', 'khonsu',
        'maat', 'min', 'mut', 'nefertum', 'neith', 'nephthys', 'onuris', 'osiris', 
        'pataikos', 'ptah', 'qebehsenuef', 'ra', 'ra-horakhty', 'sekhmet', 'shu',
        'taweret', 'thoth') THEN 'deities with egyptian origin'
    	ELSE 'local deities and/or adaptations'
    END AS form_source,
    COUNT(a.amulet_id) as total,
    ROUND(COUNT(*) * 100.0 / tc.group_total, 5) as percentage
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
JOIN sites s ON s.site_id = b.site_id
JOIN total_counts tc ON tc.social_group = b.social_group AND tc.region = s.region
WHERE dating = 'napatan' 
    AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY s.region, b.social_group, form_source, tc.group_total
"""

df = pd.read_sql(query, engine)

custom_colors = ['#f27c8a',
                 '#e6f598',
                '#dcd8ff',
                '#e0aa82',
                '#65f3c6',
                '#92cef3',
                '#d3d3d3',
                '#e59fe2',
                '#aec6cf',
                '#ffb347']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

df = df.sort_values('region')

fig = px.bar(
    df,
    x='percentage',
    y='region',
    text=df['percentage'].round(1),
    color='form_source',
    facet_row='social_group',
    barmode="stack",
    template="plotly_white",
    title='Source of deity amulets by social group and region (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"region": region_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=6),
    legend_title_text='',
    title_font=dict(size=6),
    margin=dict(l=0, r=10, t=20, b=0)
)

fig.update_traces(textposition='auto', textfont_size=4)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/motifs_region_deities.png',scale=3, width=550, height=250)