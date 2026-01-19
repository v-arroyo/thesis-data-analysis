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
    site_name,
    ROUND(SUM(stairs) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 1) AS stairs,
    ROUND(SUM(slope) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 1) AS slope,
    ROUND(SUM(bricks) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 1) AS bricks,
    ROUND(SUM(bed_holes) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 1) AS "bed holes",
    ROUND(SUM(trenches) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 1) AS trenches,
    ROUND(SUM(niches) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 1) AS niches,
    ROUND(SUM(roof) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 1) AS roofing,
    COUNT(*) AS site_burials,
    SUM(COUNT(*)) OVER() AS total_burials
FROM burials b
JOIN sites s ON s.site_id = b.site_id
WHERE social_group = 'non-elite' 
  AND dating = 'napatan' 
  AND temp = '25th-EN'
GROUP BY 1;
"""

df = pd.read_sql(query, engine)

df_melted = df.melt(id_vars=['site_name', 'total_burials'],  # Include total_burials in id_vars
                    value_vars=['stairs', 'slope', 'bricks', 'bed holes', 'trenches', 'niches', 'roofing'],
                    var_name='feature', value_name='percentage')


df_melted['label_text'] = df_melted['percentage'].round(1)

df_filtered = df_melted[df_melted['percentage'] > 0]

fig = px.scatter(
    df_filtered,
    x="site_name",
    y="feature",
    color='percentage',
    text='percentage',
    size_max=20,
    title="Percentage of 25th Dynasty-Early Napatan non-elite tombs with certain features (%)",
    labels={"percentage": "Percentage"},
    color_continuous_scale='Sunset',
    template="plotly_white"
)

fig.update_layout(
    xaxis={'categoryorder': 'total descending'},
    font=dict(
        family="Verdana, sans-serif",
        color='black',
        size=8
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.50,
        traceorder='reversed'
    ),
    margin=dict(l=0, r=10, t=20, b=0),
    autosize=True,
    title_font=dict(size=8),
    coloraxis=dict(
        colorbar=dict(
            tickfont=dict(size=7),
            title_font=dict(size=7)
        )
    )
)

fig.update_traces(textposition='top right', textfont_size=6)
fig.update_xaxes(title_text='', categoryorder='category ascending')
fig.update_yaxes(title_text='', categoryorder='category descending')
fig.update_coloraxes(showscale=False)

pio.write_image(fig, 'images/chapter5/25-EN_features.png',scale=3, width=550, height=190)