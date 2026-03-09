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
        WHEN m.material_local = 1 THEN 'local'
        WHEN m.material_imported = 1 THEN 'imported'
    END as material_type,
    tc.group_total,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / tc.group_total, 5) as percentage
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
JOIN materials m ON m.material_name = a.material
JOIN sites s ON s.site_id = b.site_id
JOIN total_counts tc ON tc.social_group = b.social_group AND tc.region = s.region
WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686',
                 '#8b4513', '#2f4f4f', '#ff6b4a', '#20b2aa', '#daa520',
                 '#cd5c5c', '#4682b4', '#e8ea7a', '#98fb98', '#696969']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

df = df.sort_values('region')

fig = px.line(
    df,
    x='region',
    y='percentage',
    color='social_group',
    facet_row='material_type',
    text=df['percentage'].round(0),
    markers=True,
    template="plotly_white",
    title='Distribution of local and imported amulet materials by social group and region (in %)',
    color_discrete_sequence=custom_colors,
    labels={"material_type" : "material"},
    category_orders={"region": region_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=50, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='middle right', textfont_size=4)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/material_region_imp-exp.png',scale=3, width=550, height=300)