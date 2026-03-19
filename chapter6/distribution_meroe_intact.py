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
    	COUNT(burial_id) as intact_total
    FROM burials b
	WHERE dating = 'napatan' AND b.site_id IN (4,5) AND b.disturbed = 0
	GROUP BY 1,2,3
)
SELECT
	b.temp_early,
    b.temp_late,
    b.social_group,
    tc.intact_total,
    COUNT(*) as intact_amulet_total
FROM burials b
JOIN total_counts tc ON tc.social_group = b.social_group AND tc.temp_early = b.temp_early AND tc.temp_late = b.temp_late
WHERE dating = 'napatan' 
	AND b.site_id in (4,5)
	AND b.disturbed = 0
	AND b.contains_amulet = 1
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
            'intact_amulet_total': row['intact_amulet_total'],
            'intact_total': row['intact_total']  # same count
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'intact_amulet_total': row['intact_amulet_total'] / len(phases),
                'intact_total': row['intact_total'] / len(phases)  # splits count evenly
            })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# aggregate by phase and social group
df_grouped = df_expanded.groupby(['phase', 'social_group'], as_index=False).agg({
    'intact_total': 'sum',
    'intact_amulet_total': 'sum'
})

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

df_grouped = df_grouped.sort_values('phase')

fig = px.bar(
    df_grouped,
    x=['intact_amulet_total', 'intact_total'],
    y='phase',
    barmode='group',
    facet_row='social_group',
    template="plotly_white",
    title='Distribution of amulets in intact tombs from Meroe West and South by social group and chronological phase',
    color_discrete_sequence=custom_colors,
    category_orders={"phase": phase_order, "social_group": ["elite", "non-elite"]}
)

fig.update_traces(
    texttemplate='%{x:.0f}',
    textposition='auto'
)

fig.update_traces(name='Intact tombs with amulets', selector={'name': 'intact_amulet_total'})
fig.update_traces(name='Total intact tombs', selector={'name': 'intact_total'})

fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.22,
        xanchor="center",
        x=0.45,
        traceorder='reversed',
    ),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='outside', textfont_size=5)
fig.update_yaxes(title='', matches=None)
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/distribution_meroe_intact.png',scale=3, width=550, height=250)