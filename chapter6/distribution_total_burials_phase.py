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
    	COUNT(burial_id) as total_burials
    FROM burials b
	WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
	GROUP BY 1,2,3
)
SELECT
	b.temp_early,
    b.temp_late,
    b.social_group,
    tc.total_burials,
    COUNT(a.amulet_id) as total_amulets
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
JOIN total_counts tc ON tc.social_group = b.social_group AND tc.temp_early = b.temp_early AND tc.temp_late = b.temp_late
GROUP BY 1,2,3,4
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
            'total_burials': row['total_burials'],
            'total_amulets': row['total_amulets']  # same count
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'total_burials': row['total_burials'] / len(phases),
                'total_amulets': row['total_amulets'] / len(phases)  # splits count evenly
            })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# aggregate by phase and social group
df_grouped = df_expanded.groupby(['phase', 'social_group'], as_index=False).agg({
    'total_burials': 'sum',
    'total_amulets': 'sum'
})

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

df_grouped = df_grouped.sort_values('phase')

fig = px.bar(
    df_grouped,
    x='phase',
    y=['total_burials', 'total_amulets'],
    barmode='group',
    facet_row='social_group',
    template="plotly_white",
    title='Correlation of number of tombs and amulets per social group and chronological phase',
    color_discrete_sequence=custom_colors,
    category_orders={"phase": phase_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_traces(
    texttemplate='%{y:.0f}',
    textposition='auto'
)

fig.update_traces(name='Total amulets', selector={'name': 'total_amulets'})
fig.update_traces(name='Total tombs', selector={'name': 'total_burials'})

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='auto', textfont_size=4)
fig.update_yaxes(title='', matches=None)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/distribution_total_burials_phase.png',scale=3, width=550, height=350)