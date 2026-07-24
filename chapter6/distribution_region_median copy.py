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
    b.social_group,
    COUNT(DISTINCT b.burial_id) as total_graves,
    COUNT(CASE WHEN b.contains_amulet = 1 THEN 1 END) as graves_with_amulets
FROM burials b
JOIN sites s ON s.site_id = b.site_id
WHERE b.dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#C0C0C0']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df_grouped = df.groupby(['region', 'social_group'], as_index=False).agg({
    'total_graves': 'sum',
    'graves_with_amulets': 'sum'
})

# percentage
df_grouped['percentage'] = round(df_grouped['graves_with_amulets'] * 100.0 / df_grouped['total_graves'], 1)

# put in correct order
df_grouped['region'] = pd.Categorical(df_grouped['region'], categories=region_order, ordered=True)

# sort by region and then type
df_grouped = df_grouped.sort_values(['region', 'social_group'])

fig = px.bar(
    df_grouped,
    x='region',
    y='percentage',
    text=df_grouped['percentage'].round(0),
    barmode='group',
    facet_col='social_group',
    template="plotly_white",
    title='Percentage of tombs containing amulets by social group and region',
    color_discrete_sequence=custom_colors,
    category_orders={"region": region_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(
    legend=dict(
        orientation='h',
        yanchor="middle",
        y=-0.13,
        xanchor="center",
        x=0.40),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=40, b=0),
    title_font=dict(size=8)
)

for annotation in fig.layout.annotations:
    if annotation.text.startswith("social_group="):
        annotation.text = annotation.text.replace("social_group=", "")

fig.update_traces(textposition='auto', textfont_size=5)
fig.update_yaxes(title='')
fig.update_xaxes(title='', matches=None)

pio.write_image(fig, 'images/chapter6/distribution_median_region2.png',scale=3, width=550, height=250)