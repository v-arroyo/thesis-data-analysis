import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio
import plotly.graph_objects as go

engine = create_engine(f'mysql+pymysql://{os.getenv"DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
SELECT 
    s.region,
    a.form
FROM amulets a
JOIN burials b ON a.burial_id = b.burial_id
JOIN sites s ON a.site_id = s.site_id
WHERE b.dating = 'napatan' 
    AND b.social_group = 'non-elite'
    AND a.form2 IS NULL
GROUP BY s.region, a.form
HAVING NOT EXISTS (
    SELECT 1
    FROM amulets a2
    JOIN burials b2 ON a2.burial_id = b2.burial_id
    JOIN sites s2 ON a2.site_id = s2.site_id
    WHERE a2.form = a.form
        AND s2.region != s.region
        AND b2.dating = 'napatan' 
        AND b2.social_group = 'non-elite'
        AND a2.form2 IS NULL
)
ORDER BY 1,2
"""

df = pd.read_sql(query, engine)

custom_colors = ['#C0C0C0']

region_order = ["lower nubia", "north upper nubia", "4th cataract", "meroe region"]

df['region'] = pd.Categorical(df['region'], categories=region_order, ordered=True)

df = df.sort_values('region')

df = df.reset_index(drop=True)

pivot_df = df.groupby(['form', 'region']).size().unstack(fill_value=0)

fig = px.imshow(
    pivot_df,
    #x='dummy',
    #y='region',
    #color='form',
    title='Average number of amulets per tomb by region and phase',
    #color_discrete_sequence=custom_colors,
    template="plotly_white",
    aspect='auto')

fig.update_layout( 
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    margin=dict(l=0, r=10, t=50, b=0),
    title_font=dict(size=8)
)

#fig.update_traces(textposition='top right', textfont_size=7)
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/chapter5/region_forms.png',scale=3, width=400, height=300)