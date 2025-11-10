import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go

engine = create_engine(f'mysql+pymysql://{os.getenv"DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
select 
    region,
    type,
    count(amulet_id) as total
from burials b
join amulets a on a.burial_id = b.burial_id
join sites s on s.site_id = b.site_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10) and social_group = 'non-elite'
group by 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#79ccb3','#e9724d', '#92cad1', '#d6d727', '#868686', '#be8a60', '#beb7a4', '#537a5a', '#b4656f']

# Define your phase order for chronological sorting
region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

# Convert 'phase' to ordered categorical for correct x-axis order
df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

# Sort by phase
df = df.sort_values('region')

# Plot line chart with Plotly Express, one line per amulet type
fig = px.line(
    df,
    x='region',
    y='total',
    color='type',
    markers=True,
    title='Total Amulets per Type over Chronological Phases'
)

pio.write_image(fig, 'images/chapter5/region_type.png',scale=3, width=500, height=500)