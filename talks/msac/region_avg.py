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
    region,
    COUNT(DISTINCT b.burial_id) as tomb_count,
    COUNT(amulet_id) as total_amulets,
    ROUND(COUNT(amulet_id) * 1.0 / COUNT(DISTINCT b.burial_id), 0) as avg_amulets_per_tomb
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
JOIN sites s ON s.site_id = b.site_id
WHERE dating = 'napatan' 
    AND b.site_id IN (4,5,6,7,8,9,10) 
    AND social_group = 'non-elite'
GROUP BY 1
"""

df = pd.read_sql(query, engine)

custom_colors = ['#C0C0C0']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

df = df.sort_values('region')

fig = px.bar(
    df,
    x='region',
    y='avg_amulets_per_tomb',
    barmode='stack',
    text='avg_amulets_per_tomb',
    title='Average number of amulets per tomb by region',
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout( 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.10,
        xanchor="center",
        x=0.50,
        traceorder='reversed'),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=10, t=50, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='outside', textfont_size=7)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', matches=None)

pio.write_image(fig, 'images/msac/region_avg.png',scale=3, width=400, height=300)