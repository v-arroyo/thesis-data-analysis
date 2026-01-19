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
    temp,
    type,
    COUNT(DISTINCT form) as exclusive_forms_count
FROM (
    SELECT 
        b.temp,
        a.form,
        a.type
    FROM amulets a
    JOIN burials b ON a.burial_id = b.burial_id
    WHERE b.dating = 'napatan' 
        AND b.social_group = 'non-elite'
    GROUP BY b.temp, a.form, a.type
    HAVING NOT EXISTS (
        SELECT 1
        FROM amulets a2
        JOIN burials b2 ON a2.burial_id = b2.burial_id
        WHERE a2.form = a.form
            AND b2.temp != b.temp
            AND b2.dating = 'napatan' 
            AND b2.social_group = 'non-elite'
    )
) exclusive_motifs
GROUP BY temp, type
ORDER BY temp, type;
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686',
                 '#8b4513', '#2f4f4f', '#ff6b4a', '#20b2aa', '#daa520',
                 '#cd5c5c', '#4682b4', '#e8ea7a', '#98fb98', '#696969']

temp_order = ["pre-25th", "25th", "25th-EN", "25th-MN", "EN", "MN"]

df['temp'] = pd.Categorical(df['temp'], categories=temp_order, ordered=True)

df = df.sort_values('temp')

fig = px.bar(
    df,
    x='temp',
    y='exclusive_forms_count',
    text='exclusive_forms_count',
    color='type',
    barmode='group',
    title='Exclusive amulets motifs by type and chronological phase',
    template="plotly_white",
    color_discrete_sequence=custom_colors
)

fig.update_layout( 
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=10, t=50, b=0),
    title_font=dict(size=8),
)

fig.update_traces(textposition='outside', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/msac/temp_form.png',scale=3, width=450, height=300)