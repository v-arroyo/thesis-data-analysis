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
    form,
    COUNT(amulet_id) AS total
FROM burials b
JOIN sites s ON s.site_id = b.site_id
JOIN amulets a ON a.burial_id = b.burial_id
WHERE dating = 'napatan' 
    AND b.site_id in (1,2,4,5,6,7,8,9,10) 
    AND type = 'animal'
GROUP by 1,2
"""

df = pd.read_sql(query, engine)

social_order = ['royal', 'elite', 'non-elite']

df_sorted = df.sort_values('form', ascending=False)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.scatter(
    df_sorted,
    x="social_group",
    y="form",
    color="total",
    text="total",
    title="",
    color_continuous_scale='Sunset',
    template="plotly_white",
    category_orders={'social_group': social_order}
)

fig.update_layout(#xaxis={'categoryorder': 'total ascending'}, 
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
        size=7),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=0, t=20, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='middle right', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter6/check_forms_animals.png',scale=4, width=550, height=550)