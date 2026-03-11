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
    	b.temp_early,
        b.temp_late,
    	COUNT(amulet_id) as group_total
    FROM amulets a
	JOIN burials b ON b.burial_id = a.burial_id
	WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
	GROUP BY 1,2,3
)
SELECT
    b.temp_early,
    b.temp_late,
    b.social_group,
    form,
    tc.group_total,
    COUNT(a.amulet_id) as total
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
JOIN total_counts tc ON tc.social_group = b.social_group AND tc.temp_early = b.temp_early AND tc.temp_late = b.temp_late
WHERE dating = 'napatan' 
    AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    AND a.form IN ('udjat', 'quadruple udjat')
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
        # single phase
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'form': row['form'],
            'group_total': row['group_total'],
            'total': row['total']  # same count
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'form': row['form'],
                'group_total': row['group_total'] / len(phases),
                'total': row['total'] / len(phases)  # splits count evenly
            })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# aggregate by phase and social group
df_grouped = df_expanded.groupby(['phase', 'social_group', 'form'], as_index=False).agg({
    'total': 'sum',
    'group_total': 'sum'
})

# percentage of faience amulets
df_grouped['percentage'] = round(df_grouped['total'] * 100.0 / df_grouped['group_total'], 1)

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

# sort by phase and then type
df_grouped = df_grouped.sort_values(['phase', 'social_group', 'form'])

fig = px.line(
    df_grouped,
    x='phase',
    y='percentage',
    color='form',
    text=df_grouped['percentage'].round(0),
    markers=True,
    facet_row='social_group',
    template="plotly_white",
    title='Distribution of udjat and quadruple udjat amulets by social group and chronological phase (in %)',
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
    margin=dict(l=0, r=10, t=40, b=0)
)

fig.update_traces(textposition='bottom right', textfont_size=4)
fig.update_yaxes(title='', matches=None)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/motifs_phase_udjat.png',scale=3, width=550, height=330)