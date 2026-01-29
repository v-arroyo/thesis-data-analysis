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
select
	temp_early,
    temp_late,
    social_group,
    a.form,
    count(amulet_id) as total
from burials b
join amulets a on a.burial_id = b.burial_id
where dating = 'napatan' and b.site_id in (1,2,4,5,6,7,8,9,10) and type = 'deity'
group by 1,2,3,4
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
            'form': row['form'],
            'total': row['total']
        })
    else:
        # Multi-phase burial: count in BOTH phases
        expanded_rows.append({
            'phase': row['temp_early'],
            'social_group': row['social_group'],
            'form': row['form'],
            'total': row['total']
        })
        expanded_rows.append({
            'phase': row['temp_late'],
            'social_group': row['social_group'],
            'form': row['form'],
            'total': row['total']
        })

# transform list into df
df_expanded = pd.DataFrame(expanded_rows)

# aggregation by phase and type
df_grouped = df_expanded.groupby(['phase', 'social_group', 'form'], as_index=False)['total'].sum()

# put in correct order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

# sort by phase and then type
df_grouped = df_grouped.sort_values(['form'], ascending=False)

df_grouped = df_grouped.sort_values(['phase', 'form'], ascending=[True, False])

fig = px.scatter(
    df_grouped,
    x="phase",
    y="form",
    color="total",
    facet_col='social_group',
    title="",
    color_continuous_scale='Sunset',
    template="plotly_white",
    labels={"social_group": "status"}
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=6),
    legend_title_text='',
    title_font=dict(size=6),
    margin=dict(l=0, r=0, t=20, b=0),
    autosize=True
)

fig.update_traces(textposition='top right', textfont_size=5)
fig.update_yaxes(title='')
fig.update_xaxes(title='', matches=True)

pio.write_image(fig, 'images/chapter6/phase_motif_deity.png',scale=3, width=500, height=500)