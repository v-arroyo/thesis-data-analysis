import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
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
    a.material,
    COUNT(a.amulet_id) as total,
    ROUND(COUNT(*) * 100.0 / tc.group_total, 5) as percentage_of_all_materials
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
JOIN sites s ON s.site_id = b.site_id
JOIN total_counts tc ON tc.social_group = b.social_group AND tc.region = s.region
WHERE dating = 'napatan' 
    AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    AND a.material IN ('obsidian', 'ivory', 'gold', 'lapis', 'electrum', 'silver')
GROUP BY s.region, b.social_group, a.material, tc.group_total
"""

df = pd.read_sql(query, engine)

custom_colors = ['#f27c8a',
                 '#e6f598',
                '#dcd8ff',
                '#e0aa82',
                '#65f3c6',
                '#92cef3',
                '#d3d3d3',
                '#e59fe2']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

df = df.sort_values('region')

fig = px.line(
    df,
    x="region",
    y="percentage_of_all_materials",
    facet_row="social_group",
    color='material',
    markers=True,
    title="Distribution of selected materials by social group and region (in %)",
    color_discrete_sequence=custom_colors,
    template="plotly_white",
    category_orders={"region": region_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(yaxis={'categoryorder': 'total ascending'}, 
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=30, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', matches=None)

pio.write_image(fig, 'images/chapter6/material_region_special.png',scale=3, width=550, height=350)