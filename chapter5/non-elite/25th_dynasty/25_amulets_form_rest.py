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
    s.site_name,
    a.form AS form,
    COUNT(a.amulet_id) AS total
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
JOIN sites s ON s.site_id = b.site_id
WHERE 
    dating = 'napatan'
    AND temp = '25th'
    AND s.site_id IN (4,5,6,7,8,9,10)
    and social_group = 'non-elite'
    and type in ('human', 'other', 'object', 'nature')
    and form != 'unknown'
    and form2 is null
    and form3 is null
GROUP BY 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x="form",
    y="total",
    color="site_name",
    text="total",
    barmode='stack',
    title="25th Dynasty non-elite nature, object, human and other amulet motifs",
    labels={"super": "superstructure", "sub": "substructure", "site_name": "site"},
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(xaxis=dict(categoryorder='total descending', automargin=True, title_standoff=0), 
    legend=dict(
        #orientation="h",
        yanchor="bottom",
        y=0.30,
        xanchor="center",
        x=1.10,
        #traceorder='reversed'),
    ),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=6),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=0, t=15, b=0),
    autosize=True,
    title_font=dict(size=6)
)

fig.update_traces(textposition='outside', textfont_size=6)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/25_amulets_form_rest.png',scale=3, width=550, height=230)