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
where dating = 'napatan' and b.site_id in (1,2,4,5,6,7,8,9,10) and form IN ("aker", "amun", "amun/isis/horus", "amun/khonsu/monthu", "amun/mut/khonsu",
    "anubis", "bastet", "bes", "duamutef", "hapi", "hapi, nile god", "hathor", "heh", "horus", "horus child", "imsety", "isis", "isis and horus", "khonsu",
    "maat", "min", "mut", "nefertum", "neith", "nephthys", "onuris", "osiris", "pataikos", "ptah", "qebehsenuef", "ra", "ra-horakhty", "sekhmet", "shu",
    "taweret", "thoth") AND social_group = "royal"
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

df_grouped = df_grouped.sort_values(['phase', 'form'], ascending=[True, True])

fig = px.scatter(
    df_grouped,
    x='phase',
    y='form',
    color='total',
    text='total',
    title="Distribution of amulets representing Egyptian deities<br>by social group and chronological phase",
    facet_col='social_group',
    template="plotly_white",
    color_continuous_scale='Sunset'
)

fig.update_layout(
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=6),
    legend_title_text='',
    title_font=dict(size=6),
    margin=dict(l=0, r=10, t=50, b=0),
)

fig.update_traces(textposition='top right', textfont_size=5)
fig.update_yaxes(title='', categoryorder='category descending')
fig.update_xaxes(title='')
fig.update_coloraxes(showscale=False)

pio.write_image(fig, 'images/chapter6/forms_egyptian_deities_phase_royal.png',scale=4, width=250, height=300)