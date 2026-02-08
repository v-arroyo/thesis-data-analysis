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
	region,
    social_group,
    CASE 
        WHEN a.form IN ("aker", "amun", "amun/isis/horus", "amun/khonsu/monthu", "amun/mut/khonsu",
            "anubis", "bastet", "bes", "duamutef", "hapi", "hapi, nile god", "hathor", "heh", "horus", "horus child", "imsety", "isis", "isis and horus", "khonsu",
            "maat", "min", "mut", "nefertum", "neith", "nephthys", "onuris", "osiris", "pataikos", "ptah", "qebehsenuef", "ra", "ra-horakhty", "sekhmet", "shu",
            "taweret", "thoth") THEN 'egyptian deities'
        ELSE "local deities/adaptations"
    END AS form_source,
    COUNT(*) AS count
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
JOIN sites s ON s.site_id = b.site_id
WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686',
                 '#8b4513', '#2f4f4f', '#ff6b4a', '#20b2aa', '#daa520',
                 '#cd5c5c', '#4682b4', '#e8ea7a', '#98fb98', '#696969']

phase_order = ["pre-25th", "25th", "EN", "MN", "LN"]

# aggregate counts by phase, social_group, and form_source
df_grouped = df.groupby(['region', 'social_group', 'form_source'], as_index=False)['count'].sum()

# calculate percentages within each phase and social_group
df_grouped['percentage'] = df_grouped.groupby(['region', 'social_group'])['count'].transform(
    lambda x: round(x / x.sum() * 100, 0) if x.sum() > 0 else 0
)

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"] 

# order phases and group
df_grouped['region'] = pd.Categorical(df_grouped['region'], categories=region_order, ordered=True)

df_grouped = df_grouped.sort_values(['region', 'social_group', 'form_source'])

# drop count column
df_grouped = df_grouped.drop('count', axis=1)

fig = px.bar(
    df_grouped,
    x='region',
    y='percentage',
    text='percentage',
    color='form_source',
    facet_row='social_group',
    barmode="group",
    template="plotly_white",
    title='Source of deity amulets by social group and region',
    color_discrete_sequence=custom_colors,
    labels={"social_group": "social group"},
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

fig.update_traces(textposition='auto', textfont_size=5)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/motifs_region_deities.png',scale=3, width=550, height=250)