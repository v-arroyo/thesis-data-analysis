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
WITH amulet_counts AS (
    SELECT 
        s.region,
        b.social_group,
        b.burial_id,
        COUNT(a.amulet_id) as amulet_count
    FROM burials b
    JOIN sites s ON b.site_id = s.site_id
    LEFT JOIN amulets a ON b.burial_id = a.burial_id
    WHERE b.dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    GROUP BY b.burial_id, s.region, b.social_group
),
ranked_counts AS (
    SELECT 
        region,
        social_group,
        amulet_count,
        ROW_NUMBER() OVER (PARTITION BY region, social_group ORDER BY amulet_count) as row_num,
        COUNT(*) OVER (PARTITION BY region, social_group) as total_count
    FROM amulet_counts
),
group_stats AS (
    SELECT 
        region,
        social_group,
        AVG(amulet_count) as mean_amulets,
        MIN(amulet_count) as min_amulets,
        MAX(amulet_count) as max_amulets,
        SUM(CASE WHEN amulet_count = 0 THEN 1 ELSE 0 END) as zero_amulet_graves,
        COUNT(*) as total_graves
    FROM amulet_counts
    GROUP BY region, social_group
),
median_calc AS (
    SELECT 
        region,
        social_group,
        AVG(amulet_count) as median_amulets
    FROM ranked_counts
    WHERE row_num IN (
        FLOOR((total_count + 1) / 2),
        CEIL((total_count + 1) / 2)
    )
    GROUP BY region, social_group
)
SELECT 
    gs.region,
    gs.social_group,
    mc.median_amulets,
    gs.mean_amulets,
    gs.min_amulets,
    gs.max_amulets,
    gs.zero_amulet_graves,
    gs.total_graves,
    ROUND(gs.zero_amulet_graves * 100.0 / gs.total_graves, 1) as percent_with_zero
FROM group_stats gs
LEFT JOIN median_calc mc ON gs.region = mc.region AND gs.social_group = mc.social_group
"""

df = pd.read_sql(query, engine)

custom_colors = ['#C0C0C0']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

# df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

# df = df.sort_values('phase')

fig = px.bar(
    df,
    x='region',
    y='percent_with_zero',
    text=df['percent_with_zero'].round(0),
    barmode='group',
    facet_col='social_group',
    template="plotly_white",
    title='Percentage of tombs without amulets by social group and region (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"region": region_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=40, b=0),
    title_font=dict(size=8)
)

fig.update_traces(textposition='auto', textfont_size=6)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/distribution_median_region.png',scale=3, width=550, height=250)