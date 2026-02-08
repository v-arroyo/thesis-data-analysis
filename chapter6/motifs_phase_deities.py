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
	temp_early,
    temp_late,
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
WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2,3,4
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686',
                 '#8b4513', '#2f4f4f', '#ff6b4a', '#20b2aa', '#daa520',
                 '#cd5c5c', '#4682b4', '#e8ea7a', '#98fb98', '#696969']

phase_order = ["pre-25th", "25th", "EN", "MN", "LN"]

# empty list to store
expanded_rows = []

# iterate over rows to find same phases (one row) or two phases (one row for each)
for _, row in df.iterrows():
    if row['temp_early'] == row['temp_late']:
        # Count only once for that phase
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'form_source': row['form_source'],
            'count': row['count']
        })
    else:
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'form_source': row['form_source'],
            'count': row['count']
        })
        expanded_rows.append({
            'phase': row['temp_late'],
            'social_group': row['social_group'],
            'form_source': row['form_source'],
            'count': row['count']
        })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# aggregate counts by phase, social_group, and form_source
df_grouped = df_expanded.groupby(['phase', 'social_group', 'form_source'], as_index=False)['count'].sum()

# calculate percentages within each phase and social_group
df_grouped['percentage'] = df_grouped.groupby(['phase', 'social_group'])['count'].transform(
    lambda x: round(x / x.sum() * 100, 0) if x.sum() > 0 else 0
)

# order phases and group
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

df_grouped = df_grouped.sort_values(['phase', 'social_group', 'form_source'])

# drop count column
df_grouped = df_grouped.drop('count', axis=1)

fig = px.bar(
    df_grouped,
    x='percentage',
    y='phase',
    text='percentage',
    color='form_source',
    facet_row='social_group',
    template="plotly_white",
    title='Distribution of amulet types by social group and chronological phase',
    color_discrete_sequence=custom_colors,
    labels={"social_group": "social group"},
    category_orders={"phase": phase_order, "social_group": ["royal", "elite", "non-elite"]}
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

fig.update_traces(textposition='inside', textfont_size=4)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/motifs_phase_deities.png',scale=3, width=550, height=260)