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
    a.form,
    COUNT(a.amulet_id) as count
FROM amulets a
WHERE a.site_id IN (6,7,8,9,10)
AND NOT EXISTS (
    SELECT 1
    FROM amulets a2
    WHERE a2.form = a.form
    AND a2.site_id NOT IN (6,7,8,9,10,3,4,5,11)
    AND a2.site_id IS NOT NULL
)
GROUP BY 1
"""

df = pd.read_sql(query, engine)

custom_colors = ['#92cad1', '#e9724d', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x="form",
    y="count",
    #color="category",
    text='count',
    barmode='group',
    title="Distribuição de motivos de amuletos da não-elite",
    labels={"owner": "owner", "artifact_type": "obj. type", "site_name": "site"},
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(xaxis={'categoryorder': 'total descending'}, 
    legend=dict(
        #orientation="h",
        yanchor="top",
        y=0.80,
        xanchor="right",
        x=0.93),
        #traceorder='reversed'),
        #bgcolor='rgba(0,0,0,0)',
        #bordercolor='rgba(0,0,0,0)',
        #borderwidth=0)
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=10),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=10, t=30, b=0),
    autosize=True,
    title_font=dict(size=10)
)

fig.update_traces(textposition='outside')
fig.update_xaxes(title_text='', tickangle=90)
fig.update_yaxes(title_text='')

pio.write_image(fig, 'cijie2025/exclusivo_naoelite.png',scale=3, width=750, height=450)