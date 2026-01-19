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
    social_group,
    COUNT(amulet_id) AS total_amulets,
    SUM(CASE WHEN material = 'gold' THEN 1 ELSE 0 END) AS faience_count,
    ROUND(SUM(CASE WHEN material = 'gold' THEN 1 ELSE 0 END) * 100.0 / COUNT(amulet_id), 0) AS faience_percentage
FROM burials b
JOIN sites s ON s.site_id = b.site_id
JOIN amulets a ON a.burial_id = b.burial_id
WHERE dating = 'napatan' 
    AND b.site_id IN (1,2,4,5,6,7,8,9,10)
    AND temp IN ('25th', '25th-EN')
GROUP BY 1
"""

df = pd.read_sql(query, engine)

social_order = ['royal', 'elite', 'non-elite']

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x="social_group",
    y="faience_percentage",
    text="faience_percentage",
    title="Percentage of gold amulets by social group (in %)",
    color_continuous_scale='Sunset',
    template="plotly_white",
    category_orders={'social_group': social_order}
)

fig.update_layout(#yaxis={'categoryorder': 'total descending'}, 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.45,
        traceorder='reversed'),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=0, t=40, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='outside', textfont_size=8)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'diversenile/images/amulets_gold.png',scale=4, width=450, height=300)