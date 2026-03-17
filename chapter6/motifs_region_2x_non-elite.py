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
	s.region,
	b.social_group,
	form,
    form2,
	COUNT(amulet_id) AS total
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
JOIN sites s ON s.site_id = a.site_id
WHERE dating = 'napatan' 
	AND b.site_id IN (4,5,6,7,8,9,10)
	AND a.form NOT IN ('hathor')
    AND a.form2 NOT IN ('jackal', 'scorpion', 'lunar crescent')
    AND a.type = 'deity'
GROUP BY 1,2,3,4
"""

df = pd.read_sql(query, engine)

region_order = ["north upper nubia", "4th cataract", "meroe region"]

custom_colors = ['#C0C0C0']

# aggregate animals by phase, social group, and forms
df_grouped = df.groupby(['region', 'social_group', 'form', 'form2'], as_index=False)['total'].sum()

df_grouped = df_grouped.sort_values(['region', 'form'])

fig = px.scatter(
    df_grouped,
    x='form',
    y='form2',
    color='region',
    text='total',
    facet_col='region',
    facet_row='social_group',
    template="plotly_white",
    #title='Distribution of amulets combining two deities by social group and region',
    color_discrete_sequence=custom_colors,
    category_orders={"region": region_order, "social_group": ["non-elite"]}
)

fig.update_layout(xaxis=dict(automargin=True, title_standoff=0),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=4),
    legend_title_text='',
    title_font=dict(size=4),
    autosize=True,
    margin=dict(l=0, r=0, t=40, b=0),
    showlegend=False
)

fig.update_traces(textposition='middle right', textfont_size=4)
fig.update_yaxes(title='', nticks=20)
fig.update_xaxes(title='', matches=None, tickangle=45)

pio.write_image(fig, 'images/chapter6/motifs_region_2x-non-elite.png',scale=3, width=350, height=200)