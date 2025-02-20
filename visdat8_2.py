import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import sys
import os
from flask_caching import Cache

# Tambahkan path untuk modul eksternal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("C:/Users/armic/Downloads/streaming-ms-plot-main/streaming-ms-plot-main/inc_ms_fda"), 'inc_ms_fda')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("C:/Users/armic/Downloads/streaming-ms-plot-main/streaming-ms-plot-main/prog_ms_fda"), 'prog_ms_fda')))
from inc_ms_fda import IncFDO
from prog_ms_fda import ProgressiveFDA

# Membuat aplikasi Dash
app = dash.Dash(__name__)
cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})

# Fungsi untuk membaca data dengan caching selama 10 detik
@cache.memoize(timeout=10)
def read_data():
    df = pd.read_csv("./data_final4.csv")
    df['Time'] = pd.to_datetime(df['Time_Of_Day_Seconds'], unit='s') + timedelta(hours=7)
    return df

# Ambil data awal untuk mendapatkan daftar core
initial_df = read_data()
core_options = sorted(initial_df['Core'].unique())

# Layout aplikasi
app.layout = html.Div([
    # Dropdown untuk memilih metric (kolom) untuk grafik Time Series
    dcc.Dropdown(
        id='column-dropdown',
        options=[{'label': col, 'value': col} 
                 for col in read_data().columns 
                 if col not in ['Time', 'Time_Of_Day_Seconds', 'usec', 'Core', 'CPU']],
        multi=True,
        value=[],  # Default: kosong (tidak ada grafik)
        style={'width': '100%'},
        placeholder='Pilih kolom untuk Time Series'
    ),

    # Dropdown untuk filtering berdasarkan Core
    dcc.Dropdown(
        id='core-dropdown',
        options=[{'label': f"Core {core}", 'value': core} for core in core_options],
        multi=True,
        value=core_options,  # Default: semua core
        style={'width': '100%'},
        placeholder='Pilih Core (default: semua)'
    ),

    # Layout untuk menampilkan grafik
    html.Div([
        # Grafik Time Series
        dcc.Graph(
            id='time-series-graph',
            config={'scrollZoom': True},
        ),
        # Grafik MS Plot (FDA)
        dcc.Graph(id='ms-plot-graph'),
    ], style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}),

    # Interval untuk memperbarui data setiap 1 detik
    dcc.Interval(
        id='interval-update',
        interval=1000,  # setiap 1 detik
        n_intervals=0
    )
])

# Callback untuk memperbarui grafik
@app.callback(
    [Output('time-series-graph', 'figure'),
     Output('ms-plot-graph', 'figure')],
    [Input('column-dropdown', 'value'),
     Input('core-dropdown', 'value'),
     Input('time-series-graph', 'relayoutData'),
     Input('interval-update', 'n_intervals')]
)
def update_graph(selected_columns, selected_cores, relayout_data, n_intervals):
    # Baca data terbaru (data di-cache selama 10 detik)
    df = read_data()
    
    # Filter data berdasarkan pilihan Core
    if selected_cores is not None and len(selected_cores) > 0:
        df = df[df['Core'].isin(selected_cores)]
    
    # Filter data berdasarkan rentang waktu jika pengguna melakukan zoom (relayoutData)
    if relayout_data and 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
        start_time = pd.to_datetime(relayout_data['xaxis.range[0]'])
        end_time = pd.to_datetime(relayout_data['xaxis.range[1]'])
        df = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)]
    
    # Jika tidak ada kolom metric yang dipilih, tampilkan grafik kosong
    if not selected_columns:
        empty_ts = {
            'data': [],
            'layout': go.Layout(
                title='No Data Selected',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Value'}
            )
        }
        empty_ms = {
            'data': [],
            'layout': go.Layout(
                title='MS Plot - No Data Selected',
                xaxis={'title': 'MO'},
                yaxis={'title': 'VO'}
            )
        }
        return empty_ts, empty_ms

    # --- Bagian Grafik Time Series ---
    # Buat grafik untuk tiap kombinasi metric dan core menggunakan ScatterGL untuk performa optimal
    traces_time_series = []
    for column in selected_columns:
        for core in df['Core'].unique():
            df_core = df[df['Core'] == core]
            traces_time_series.append(go.Scattergl(
                x=df_core['Time'],
                y=df_core[column],
                mode='lines',
                name=f"{column} (Core {core})"
            ))
            
    time_series_fig = {
        'data': traces_time_series,
        'layout': go.Layout(
            title='Time Series Visualization',
            xaxis={'title': 'Time', 'showgrid': True},
            yaxis={'title': 'Value'},
            hovermode='closest'
        )
    }
    
    # --- Bagian Grafik MS Plot (FDA) ---
    # Gunakan salah satu metric (misalnya, metric pertama) untuk analisis FDA
    selected_metric = selected_columns[0]
    
    # Pivot data sehingga tiap kolom mewakili deret waktu untuk satu core
    pivot_df = df.pivot(index='Time', columns='Core', values=selected_metric)
    
    # Isi nilai yang hilang agar pivot_df lengkap (forward fill kemudian backward fill)
    pivot_df = pivot_df.fillna(method='ffill').fillna(method='bfill')
    
    # Jika setelah pengisian nilai hilang pivot_df masih kosong, tampilkan MS Plot kosong
    if pivot_df.empty:
        empty_ms = {
            'data': [],
            'layout': go.Layout(
                title='MS Plot - No Data Available after Filtering',
                xaxis={'title': 'MO'},
                yaxis={'title': 'VO'}
            )
        }
        return time_series_fig, empty_ms

    # Bentuk matriks X: setiap baris adalah deret waktu untuk satu core
    X = pivot_df.T.to_numpy()
    
    # Lakukan analisis FDA menggunakan IncFDO
    inc_fdo = IncFDO()
    inc_fdo.initial_fit(X)
    
    # Buat DataFrame untuk MS Plot (setiap baris mewakili satu core)
    ms_plot_data = pd.DataFrame({
        'MO': inc_fdo.MO,
        'VO': inc_fdo.VO,
        'Core': pivot_df.columns.astype(str)
    })
    
    ms_plot_fig = px.scatter(
        ms_plot_data,
        x='MO',
        y='VO',
        color='Core',  # Warna berbeda untuk tiap core
        title=f'IncMS Plot for Metric: {selected_metric}',
        labels={'MO': 'MO', 'VO': 'VO'},
        template='plotly'
    )
    
    return time_series_fig, ms_plot_fig

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run_server(debug=True)
