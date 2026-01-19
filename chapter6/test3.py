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
    count(amulet_id) as total
from burials b
join amulets a on a.burial_id = b.burial_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10)
group by 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#79ccb3','#e9724d', '#92cad1', '#d6d727', '#868686', '#be8a60', '#beb7a4', '#537a5a', '#b4656f']


# Expand rows so each amulet count appears once for early and once for late phase
df_early = df[['temp_early', 'total']].rename(columns={'temp_early': 'phase'})
df_late = df[['temp_late', 'total']].rename(columns={'temp_late': 'phase'})

df_expanded = pd.concat([df_early, df_late])

# Aggregate totals per type and phase
df_grouped = df_expanded.groupby(['phase'])['total'].sum().reset_index()

# Define your phase order for chronological sorting
phase_order = ["pre-25th", "25th", "25th-EN", "EN", "25th-MN", "EN-MN", "EN-LN", "MN", "MN-LN", "LN"]

# Convert 'phase' to ordered categorical for correct x-axis order
df_grouped['phase'] = pd.Categorical(df_grouped['phase'], categories=phase_order, ordered=True)

# Sort by phase
df_grouped = df_grouped.sort_values('phase')

# Plot line chart with Plotly Express, one line per amulet type
fig = px.line(
    df_grouped,
    x='phase',
    y='total',
    text='total',
    markers=True,
    title='Total Amulets per Type over Chronological Phases'
)

fig.update_traces(textposition='bottom left')

pio.write_image(fig, 'images/chapter5/test3.png',scale=3, width=500, height=500)