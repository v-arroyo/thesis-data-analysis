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
    	b.temp_early,
    	b.temp_late,
    	b.social_group,
    	COUNT(amulet_id) as group_total
    FROM amulets a
	JOIN burials b ON b.burial_id = a.burial_id
	JOIN sites s ON s.site_id = b.site_id
	WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
	GROUP BY 1,2,3
)
SELECT
	b.temp_early,
    b.temp_late,
    b.social_group,
    material,
    tc.group_total,
    COUNT(*) as faience_total
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
JOIN total_counts tc ON tc.social_group = b.social_group AND tc.temp_early = b.temp_early AND tc.temp_late = b.temp_late
WHERE dating = 'napatan' AND b.site_id in (1,2,4,5,6,7,8,9,10) AND material = 'faience'
GROUP BY 1,2,3,4,5
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
        # single phase
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'material': row['material'],
            'group_total': row['group_total'],
            'faience_total': row['faience_total']  # same count
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'material': row['material'],
                'group_total': row['group_total'] / len(phases),
                'faience_total': row['faience_total'] / len(phases)  # splits count evenly
            })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# aggregate by phase and social group
df_grouped = df_expanded.groupby(['phase', 'social_group', 'material'], as_index=False).agg({
    'faience_total': 'sum',
    'group_total': 'sum'
})

# percentage of faience amulets
df_grouped['percentage'] = round(df_grouped['faience_total'] * 100.0 / df_grouped['group_total'], 1)

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

df_grouped = df_grouped.sort_values('phase')

fig = px.line(
    df_grouped,
    x='phase',
    y='percentage',
    text=df_grouped['percentage'].round(1),
    color='social_group',
    facet_col='material',
    template="plotly_white",
    title='Distribution of faience amulets by social group and chronological phase (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"phase": phase_order, "social_group": ["royal", "elite", "non-elite"]}
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

fig.update_traces(textposition='top right', textfont_size=5)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/material_phase_faience.png',scale=3, width=550, height=300)