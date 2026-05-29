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
    COUNT(DISTINCT burial_id) as total_graves,
    COUNT(CASE WHEN contains_amulet = 1 THEN 1 END) as graves_with_amulets
FROM burials
WHERE dating = 'napatan' AND site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#C0C0C0']

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
            'total_graves': row['total_graves'],
            'graves_with_amulets': row['graves_with_amulets']
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'total_graves': row['total_graves'] / len(phases),
                'graves_with_amulets': row['graves_with_amulets'] / len(phases)
            })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

df_grouped = df_expanded.groupby(['phase', 'social_group'], as_index=False).agg({
    'total_graves': 'sum',
    'graves_with_amulets': 'sum'
})

# percentage of faience amulets
df_grouped['percentage'] = round(df_grouped['graves_with_amulets'] * 100.0 / df_grouped['total_graves'], 1)

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

# sort by phase and then type
df_grouped = df_grouped.sort_values(['phase', 'social_group'])

fig = px.bar(
    df_grouped,
    x='phase',
    y='percentage',
    text=df_grouped['percentage'].round(0),
    barmode='group',
    facet_col='social_group',
    template="plotly_white",
    title='Percentage of tombs with amulets by social group and chronological phase',
    color_discrete_sequence=custom_colors,
    category_orders={"phase": phase_order, "social_group": ["royal", "elite", "non-elite"]}
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

fig.update_traces(textposition='outside', textfont_size=5)
fig.update_yaxes(title='')
fig.update_xaxes(title='', matches=None)

pio.write_image(fig, 'images/chapter6/distribution_median_phase2.png',scale=3, width=550, height=250)