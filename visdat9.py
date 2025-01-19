import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("C:/Users/armic/Downloads/streaming-ms-plot-main/streaming-ms-plot-main/inc_ms_fda"), 'inc_ms_fda')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("C:/Users/armic/Downloads/streaming-ms-plot-main/streaming-ms-plot-main/prog_ms_fda"), 'prog_ms_fda')))
from inc_ms_fda import IncFDO
from prog_ms_fda import ProgressiveFDA

# Membaca data dari file CSV
def read_data():
    df = pd.read_csv("./filtered_turbologv2.csv")
    df['Time'] = pd.to_datetime(df['Time_Of_Day_Seconds'], unit='s') + timedelta(hours=7)
    return df

# Membuat aplikasi Dash
app = dash.Dash(__name__)

# Layout aplikasi
app.layout = html.Div([
    html.H1('Time Series and MS Plot Visualization'),

    # Tombol untuk menghentikan atau memulai pembaruan data
    html.Button(
        id='toggle-button',
        children='Pause Realtime Update',
        n_clicks=0
    ),

    # Dropdown untuk memilih kolom yang ingin ditambahkan
    dcc.Dropdown(
        id='column-dropdown',
        options=[{'label': col, 'value': col} for col in read_data().columns if col not in ['Time', 'Time_Of_Day_Seconds']],
        multi=True,  # Memungkinkan pemilihan beberapa kolom
        value=[],  # Nilai default kosong (grafik awal kosong)
        style={'width': '100%'}
    ),

    # Layout untuk menampilkan grafik
    html.Div([
        # Time Series Graph
        dcc.Graph(id='time-series-graph', config={'scrollZoom': True},),

        # MS Plot Graph
        dcc.Graph(id='ms-plot-graph'),
    ], style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}),

    # Interval untuk memperbarui data
    dcc.Interval(
        id='interval-update',
        interval=1000,  # Perbarui data setiap 1 detik
        n_intervals=0
    )
])

# Callback untuk mengontrol interval berdasarkan tombol pause/resume
@app.callback(
    Output('interval-update', 'disabled'),
    [Input('toggle-button', 'n_clicks')]
)
def toggle_interval(n_clicks):
    # Jika tombol ditekan, ubah status interval
    return n_clicks % 2 != 0

# Callback untuk memperbarui grafik berdasarkan kolom yang dipilih dan seleksi pengguna
@app.callback(
    [Output('time-series-graph', 'figure'),
     Output('ms-plot-graph', 'figure')],
    [Input('column-dropdown', 'value'),
     Input('time-series-graph', 'relayoutData'),
     Input('interval-update', 'n_intervals')]
)
def update_graph(selected_columns, relayout_data, n_intervals):
    # Membaca data terbaru dari CSV
    df = read_data()

    # Jika tidak ada kolom yang dipilih, tampilkan grafik kosong
    if not selected_columns:
        return {
            'data': [],
            'layout': go.Layout(
                title='No Data Selected',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Value'}
            )
        }, {
            'data': [],
            'layout': go.Layout(
                title='MS Plot - No Data Selected',
                xaxis={'title': 'MO'},
                yaxis={'title': 'VO'}
            )
        }

    # Filter data berdasarkan seleksi pengguna (jika ada)
    if relayout_data and 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
        start_time = pd.to_datetime(relayout_data['xaxis.range[0]'])
        end_time = pd.to_datetime(relayout_data['xaxis.range[1]'])
        df = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)]

    # Membuat grafik Time Series berdasarkan kolom yang dipilih
    traces_time_series = []
    for column in selected_columns:
        traces_time_series.append(go.Scatter(
            x=df['Time'],  # Gunakan kolom 'Time' sebagai sumbu X
            y=df[column],
            mode='lines',
            name=column
        ))

    # Layout untuk grafik Time Series
    time_series_fig = {
        'data': traces_time_series,
        'layout': go.Layout(
            title='Time Series Data',
            xaxis={
                'title': 'Time',  # Sumbu X adalah Time yang sudah dikonversi
                'showgrid': True  # Menampilkan grid pada sumbu X
            },
            yaxis={'title': 'Value'},
            hovermode='closest'
        )
    }

    # Menyiapkan data untuk analisis FDA
    dataf = df[selected_columns]
    X = dataf.T.to_numpy()

    # Inisialisasi dan fitting data menggunakan IncFDO
    inc_fdo = IncFDO()
    inc_fdo.initial_fit(X)

    # Membuat plot data untuk visualisasi MS Plot
    plot_data = pd.DataFrame({
        'MO': inc_fdo.MO,
        'VO': inc_fdo.VO,
        'Label': selected_columns  # Menggunakan nama kolom sebagai label
    })

    # Membuat scatter plot MS Plot menggunakan plotly express
    ms_plot_fig = px.scatter(
        plot_data, 
        x='MO', 
        y='VO', 
        color='Label',  # Warna berdasarkan label unik
        title='MS Plot',
        labels={'MO': 'MO', 'VO': 'VO'},
        template='plotly'
    )

    # Kembalikan kedua grafik
    return time_series_fig, ms_plot_fig

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run_server(debug=True)