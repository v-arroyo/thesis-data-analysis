import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
SELECT
    temp_early,
    temp_late,
    social_group,
    a.material,
    COUNT(amulet_id) as total
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
WHERE dating = 'napatan' and b.site_id in (1,2,4,5,6,7,8,9,10) AND a.material IN ('obsidian', 'ivory', 'gold', 'lapis', 'electrum', 'silver')
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
    # If single-phase burial (temp_early == temp_late)
    if row['temp_early'] == row['temp_late']:
        # Count only once for that phase
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'material': row['material'],
            'total': row['total']
        })
    else:
        # Multi-phase burial: count in BOTH phases
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'material': row['material'],
            'total': row['total']
        })
        expanded_rows.append({
            'phase': row['temp_late'],
            'social_group': row['social_group'],
            'material': row['material'],
            'total': row['total']
        })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# aggregation by phase and type
df_grouped = df_expanded.groupby(['phase', 'social_group', 'material'], as_index=False)['total'].sum()

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

# sort by phase and then type
df_grouped = df_grouped.sort_values(['phase', 'social_group', 'material'])

fig = px.line(
    df_grouped,
    x="phase",
    y="total",
    facet_row="social_group",
    color='material',
    #text='total',
    markers=True,
    title="Distribution of selected materials by chronological phase and social group",
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(yaxis={'categoryorder': 'total ascending'}, 
    legend=dict(
        yanchor="middle",
        y=0.50,
        xanchor="right",
        x=1.25),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=10),
    legend_title_text='',
    margin=dict(l=0, r=10, t=30, b=0),
    autosize=True,
    title_font=dict(size=10)
)

#fig.update_traces(textposition='outside')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter6/material_phase_special.png',scale=3, width=550, height=400)