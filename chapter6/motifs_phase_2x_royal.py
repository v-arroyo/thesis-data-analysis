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
	b.temp_early, 
	b.temp_late,
    b.temp,
	b.social_group,
	form,
    form2,
	COUNT(amulet_id) AS total
FROM amulets a
JOIN burials b ON b.burial_id = a.burial_id
WHERE dating = 'napatan' 
	AND b.site_id IN (1,2)
	AND a.form IS NOT NULL
    AND a.form2 IS NOT NULL
    AND a.type = 'deity'
GROUP BY 1,2,3,4,5,6
"""

df = pd.read_sql(query, engine)

custom_colors = ['#C0C0C0']

temp_order = ["pre-25th", "25th"]

# aggregate animals by phase, social group, and forms
df_grouped = df.groupby(['temp', 'social_group', 'form', 'form2'], as_index=False)['total'].sum()

df_grouped = df_grouped.sort_values(['temp', 'form'])

fig = px.scatter(
    df_grouped,
    x='form',
    y='form2',
    color='temp',
    text='total',
    facet_col='temp',
    facet_row='social_group',
    template="plotly_white",
    title='Distribution of amulets combining two deities by social group and chronological phase',
    color_discrete_sequence=custom_colors,
    category_orders={"temp": temp_order, "social_group": ["royal"]}
)

fig.update_layout(xaxis=dict(automargin=True, title_standoff=0),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=4),
    legend_title_text='',
    title_font=dict(size=4),
    autosize=True,
    margin=dict(l=0, r=0, t=20, b=0),
    showlegend=False
)

fig.update_traces(textposition='top right', textfont_size=4)
fig.update_yaxes(title='', nticks=20)
fig.update_xaxes(title='', matches=None)

pio.write_image(fig, 'images/chapter6/motifs_phase_2x-royal.png',scale=3, width=300, height=200)