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
    ROUND(SUM(stairs) * 100.0 / COUNT(*), 0) AS stairs,
    ROUND(SUM(chapel) * 100.0 / COUNT(*), 0) AS chapel,
    ROUND(SUM(decorated) * 100.0 / COUNT(*), 0) AS decoration,
    ROUND(SUM(bench) * 100.0 / COUNT(*), 0) AS "coffin bench",
    ROUND(SUM(bed_holes) * 100.0 / COUNT(*), 0) AS "bed holes",
    COUNT(*) AS total_burials
FROM burials
WHERE social_group = 'elite' and dating = 'napatan'
GROUP BY 1
ORDER BY 1;
"""

df = pd.read_sql(query, engine)

custom_colors = ['#e9724d', '#92cad1', '#d6d727', '#79ccb3', '#C0C0C0']

df_melted = df.melt(id_vars=['temp', 'total_burials'],  # Include total_burials in id_vars
                    value_vars=['stairs', 'chapel', 'decoration',
                    'coffin bench', 'bed holes'],
                    var_name='feature', value_name='percentage')


df_melted['label_text'] = df_melted['percentage'].round(0)

phase_order = ["pre-25th", "25th", "25th-EN", "25th-MN", "EN", "EN-MN", "EN-LN", "MN", "MN-LN", "LN"]
df_melted['temp'] = pd.Categorical(df_melted['temp'], categories=phase_order, ordered=True)
df_melted = df_melted.sort_values('temp')

df_filtered = df_melted[df_melted['percentage'] > 0]

grey_smooth = [
    [0.0, '#e0e0e0'],  # Light grey
    [0.3, '#c8c8c8'],   # Medium light grey
    [0.5, '#a0a0a0'],   # Medium grey
    [0.7, '#787878'],   # Medium dark grey
    [0.85, '#505050'],  # Dark grey
    [1.0, '#282828']    # Very dark grey
]

fig = px.scatter(
    df_filtered,
    x="temp",
    y="feature",
    color='percentage',
    text='percentage',
    size_max=20,
    title="Percentage of elite tombs with certain features (%)",
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
fig.update_xaxes(title_text='', categoryorder='array', categoryarray=phase_order)
fig.update_yaxes(title_text='')
fig.update_coloraxes(showscale=False)

pio.write_image(fig, 'images/chapter5/elite_features.png',scale=3, width=500, height=190)