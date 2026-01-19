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
    a.form,
    CASE
        WHEN a.site_id IN (1,2) THEN 'Realeza'
        WHEN a.site_id IN (6,7,8,9,10) THEN 'Não-elite'
    END AS category,
    COUNT(a.amulet_id) as count
FROM amulets a
WHERE a.site_id IN (1,2,6,7,8,9,10) AND a.form NOT IN ('deities', 'deity', 'unknown')
AND EXISTS (
    SELECT 1 FROM amulets a2 
    WHERE a2.form = a.form AND a2.site_id IN (1,2)
)
AND EXISTS (
    SELECT 1 FROM amulets a3 
    WHERE a3.form = a.form AND a3.site_id IN (6,7,8,9,10)
)
GROUP BY 1, 
    CASE
        WHEN a.site_id IN (1,2) THEN 'Realeza'
        WHEN a.site_id IN (6,7,8,9,10) THEN 'Não-elite'
    END
"""

df = pd.read_sql(query, engine)

pivot_df = df.pivot(index='form', columns='category', values='count').reset_index()
pivot_df = pivot_df.fillna(0)

custom_colors = ['#92cad1', '#e9724d', '#d6d727', '#79ccb3', '#868686']

column_names = pivot_df.columns.tolist()
header_display_names = ["<b>Motivos</b>", "<b>Realeza</b>", "<b>Não-elite</b>"]

fig = go.Figure(data=[go.Table(
    header=dict(
        values=header_display_names,  # Use display names that match your data
        fill_color='#E8E8E8',
        font=dict(color='black', size=8, family='Verdana, sans-serif'),
        align='center',  # Single value applies to all columns
        line=dict(color='gray', width=0.5),
        height=18
    ),
    cells=dict(
        values=[pivot_df[col] for col in column_names],  # Use actual column names
        line=dict(color='gray', width=0.5),
        fill_color='white',  # Single color for all cells, or use alternating pattern
        font=dict(color='black', size=8, family='Verdana, sans-serif'),
        height=18,
        align='center'  # Single value applies to all columns
    )
)])

fig.update_layout(
    margin=dict(l=5, r=5, t=5, b=5),
    paper_bgcolor='white'
)

fig.update_traces(
    columnwidth=[0.2, 0.2, 0.2],  # Adjust widths for 3 columns
    selector=dict(type='table')
)

pio.write_image(fig, 'cijie2025/compartilhados.png',scale=3, width=400, height=680)