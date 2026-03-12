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
WITH expanded_forms AS (
    SELECT
        a.amulet_id,
        b.temp_early, 
        b.temp_late,
        b.social_group,
        a.form as form
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
        AND a.type = 'animal' 
        AND a.form IS NOT NULL

    UNION ALL

    SELECT
        a.amulet_id,
        b.temp_early, 
        b.temp_late,
        b.social_group,
        a.form2 as form
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
        AND a.type = 'animal' 
        AND a.form2 IS NOT NULL

    UNION ALL

    SELECT
        a.amulet_id,
        b.temp_early, 
        b.temp_late,
        b.social_group,
        a.form3 as form
    FROM amulets a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE dating = 'napatan' 
        AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
        AND a.type = 'animal' 
        AND a.form3 IS NOT NULL
)

SELECT 
    temp_early, 
    temp_late,
    social_group,
    CASE 
        WHEN form IN ('double frog', 'double ram') THEN 'double animals'
        WHEN form IN ('hawk-headed crocodile', 'lion-headed fly', 'ram-headed scarab') THEN 'combination of animals'
        WHEN form IN ('four apes', 'four-headed ram') THEN 'quadruple animals'
        WHEN form IN ('cat', 'jackal', 'ibis', 'ape', 'crocodile', 'hippo', 'scarab', 
            'vulture', 'hawk', 'bull', 'cow', 'lion', 'ram', 'snake', 'falcon') THEN 'animals associated with common egyptian deities'
        ELSE 'common animals'
    END AS form,
    COUNT(amulet_id) AS total
FROM expanded_forms
WHERE form NOT IN ('udjat', 'uraei', 'uraeus')
GROUP BY 1,2,3,4;
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
            'form': row['form'],
            'total': row['total']
        })
    else:
        # multi-phase: split the percentage evenly
        phases = [row['temp_early'], row['temp_late']]
        for phase in phases:
            expanded_rows.append({
                'phase': phase,
                'social_group': row['social_group'],
                'form': row['form'],
                'total': row['total'] / len(phases)
            })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# calculate totals per (joined) phase AND social group
phase_group_totals = df_expanded.groupby(['phase', 'social_group'])['total'].sum().reset_index()
phase_group_totals.rename(columns={'total': 'phase_group_total'}, inplace=True)

# merge totals back to aggregate by form
df_grouped = df_expanded.merge(phase_group_totals, on=['phase', 'social_group'])
df_grouped = df_grouped.groupby(['phase', 'social_group', 'form', 'phase_group_total'], as_index=False)['total'].sum()

# percentage based on phase
df_grouped['percentage'] = round(df_grouped['total'] * 100.0 / df_grouped['phase_group_total'], 2)

# drop unneeded columns
df_grouped = df_grouped.drop(['total', 'phase_group_total'], axis=1)

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

# sort by phase and then type
df_grouped = df_grouped.sort_values(['phase', 'social_group', 'form'])

fig = px.bar(
    df_grouped,
    x='percentage',
    y='phase',
    #text=df_grouped['percentage'].round(1),
    color='form',
    facet_row='social_group',
    template="plotly_white",
    barmode='stack',
    title='Distribution of animal amulets by social group and chronological phase (in %)',
    color_discrete_sequence=custom_colors,
    category_orders={"phase": phase_order, "social_group": ["royal", "elite", "non-elite"]}
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=6),
    legend_title_text='',
    title_font=dict(size=6),
    margin=dict(l=0, r=10, t=20, b=0),
    legend=dict(traceorder='grouped')
)

fig.update_traces(textposition='auto', textfont_size=3)
fig.update_yaxes(title='')
fig.update_xaxes(title='')

pio.write_image(fig, 'images/chapter6/motifs_phase_animals.png',scale=3, width=550, height=250)