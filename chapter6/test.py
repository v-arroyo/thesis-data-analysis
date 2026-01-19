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
	temp,
    type,
    count(amulet_id) as total
from burials b
join amulets a on a.burial_id = b.burial_id
where dating = 'napatan' and b.site_id in (4,5,6,7,8,9,10)
group by 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#79ccb3','#e9724d', '#92cad1', '#d6d727', '#868686', '#be8a60', '#beb7a4', '#537a5a', '#b4656f']

phase_order = [
    "pre-25th",
    "25th",
    "25th-EN",  
    "EN",
    "25th-MN",
    "EN-MN",
    "EN-LN", 
    "MN",
    "MN-LN",
    "LN"
]


fig = px.sunburst(
    df,
    path=["temp", "type", "total"],
    color="temp",  # Optional: color by temp/phase for distinction
    color_discrete_sequence=custom_colors  # Use your custom palette]
)

fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
fig.update_traces(insidetextorientation='radial')

pio.write_image(fig, 'images/chapter5/test.png',scale=3, width=500, height=500)