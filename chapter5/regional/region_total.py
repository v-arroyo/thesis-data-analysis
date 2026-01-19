import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
SELECT 
    region,
    COUNT(DISTINCT b.burial_id) as tomb_count,
    COUNT(amulet_id) as total_amulets
FROM burials b
LEFT JOIN amulets a ON a.burial_id = b.burial_id
JOIN sites s ON s.site_id = b.site_id
WHERE dating = 'napatan' 
    AND b.site_id IN (4,5,6,7,8,9,10) 
    AND social_group = 'non-elite'
GROUP BY 1
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686',
                 '#8b4513', '#2f4f4f', '#ff6b4a', '#20b2aa', '#daa520',
                 '#cd5c5c', '#4682b4', '#e8ea7a', '#98fb98', '#696969']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

df = df.sort_values('region')

df_melted = df.melt(id_vars=['region'], 
                    value_vars=['tomb_count', 'total_amulets'],
                    var_name='metric', 
                    value_name='count')

# Create custom names for the metrics
df_melted['metric'] = df_melted['metric'].replace({
    'tomb_count': 'total tombs',
    'total_amulets': 'total amulets'
})

fig = px.bar(df_melted, 
             x='region', 
             y='count', 
             color='metric',
             barmode='group',
             text='count',
             title='Total number of tombs and amulets by region',
             template="plotly_white",
             color_discrete_sequence=custom_colors)


fig.update_layout(
    legend=dict(
        #orientation="h",
        yanchor="bottom",
        y=0.30,
        xanchor="center",
        x=1.10),
        #traceorder='reversed'),
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

fig.update_traces(textposition='outside', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/region_total.png',scale=3, width=550, height=250)