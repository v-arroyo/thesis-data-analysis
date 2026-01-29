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
    type,
    count(amulet_id) as total
from burials b
join amulets a on a.burial_id = b.burial_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10)
group by 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#79ccb3','#e9724d', '#92cad1', '#d6d727', '#868686', '#be8a60', '#beb7a4', '#537a5a', '#b4656f']

# Define your phase order for chronological sorting
phase_order = ["pre-25th", "25th", "25th-EN", "EN", "25th-MN", "EN-MN", "EN-LN", "MN", "MN-LN", "LN"]

# Convert 'phase' to ordered categorical for correct x-axis order
df['phase'] = pd.Categorical(df['phase'], categories=phase_order, ordered=True)

# Sort by phase
df = df.sort_values('phase')

# Plot line chart with Plotly Express, one line per amulet type
fig = px.line(
    df,
    x='phase',
    y='total',
    color='type',
    markers=True,
    title='Total Amulets per Type over Chronological Phases'
)

pio.write_image(fig, 'images/chapter5/test2.png',scale=3, width=500, height=500)