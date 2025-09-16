import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio

engine = create_engine(f'mysql+pymysql://{os.getenv"DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
SELECT 
    s.site_name,
    super,
    sub,
    COUNT(burial_id) as total_burials
FROM burials b
JOIN sites s
ON s.site_id = b.site_id
WHERE dating = 'napatan' AND b.site_id = 7 AND sub != 'deposit'
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#D3D3D3']

fig = px.bar(
    df,
    x="super",
    y="total_burials",
    facet_col="site_name",
    facet_row="sub",
    text="total_burials",
    title="Mirgissa tomb structures",
    labels={"super": "superstructure", "sub": "substructure", "site_name": "site"},
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(xaxis={'categoryorder': 'total descending'}, 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.20,
        xanchor="center",
        x=0.50,
        traceorder='reversed'),
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=10),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=10, t=50, b=0),
    autosize=True,
    title_font=dict(size=10)
)

fig.update_traces(textposition='auto')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='', matches=None)

pio.write_image(fig, 'images/chapter5/mirgissa_tomb.png',scale=3, width=450, height=400)