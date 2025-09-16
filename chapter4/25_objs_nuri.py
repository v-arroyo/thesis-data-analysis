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
WHERE temp = '25th' AND b.site_id IN (2) AND artifact_type NOT IN ('beads', 'shabtis')
GROUP BY 1,2,3
"""

df = pd.read_sql(query, engine)

custom_colors = ['#92cad1', '#e9724d', '#d6d727', '#79ccb3', '#868686']

fig = px.bar(
    df,
    x="artifact_type",
    y="count",
    color="owner",
    facet_col="site_name",
    #text='count',
    barmode='stack',
    title="25th Dynasty object types",
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
        x=0.93,
        traceorder='reversed'),
        #bgcolor='rgba(0,0,0,0)',
        #bordercolor='rgba(0,0,0,0)',
        #borderwidth=0)
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8),
    legend_title_text='',
    #yaxis=dict(
        #tickmode='linear',
        #dtick=1),
    margin=dict(l=0, r=10, t=30, b=0),
    autosize=True,
    title_font=dict(size=8)
)

fig.update_traces(textposition='outside')
fig.update_xaxes(title_text='', tickangle=45)
fig.update_yaxes(title_text='')

pio.write_image(fig, 'images/25_objs_nuri.png',scale=3, width=500, height=260)