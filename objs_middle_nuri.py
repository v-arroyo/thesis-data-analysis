import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import plotly.io as pio

engine = create_engine(f'mysql+pymysql://{os.getenv"DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/{os.getenv("DB_NAME")}')

query = """
SELECT 
    s.site_name,
    b.owner,
    a.artifact_type,
    COUNT(artifact_id) as count
FROM burials b
JOIN sites s
ON s.site_id = b.site_id
JOIN artifacts a
ON a.burial_id = b.burial_id
WHERE temp = 'middle napatan' AND b.site_id IN (2) AND artifact_type NOT IN ('shabtis')
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x="count",
    y="artifact_type",
    color="owner",
    facet_col="site_name",
    #text='count',
    barmode='group',
    title="Middle Napatan object types",
    labels={"owner": "owner", "artifact_type": "obj. type", "site_name": "site"},
    color_discrete_sequence=custom_colors,
    template="plotly_white"
)

fig.update_layout(yaxis={'categoryorder': 'total ascending'}, 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.20,
        xanchor="center",
        x=0.40,
        traceorder='reversed'),
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

fig.update_traces(textposition='outside')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/objs_middle_nuri.png',scale=3, width=500, height=400)