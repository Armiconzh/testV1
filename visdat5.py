import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from inc_ms_fda import IncFDO
from prog_ms_fda import ProgressiveFDA

# Membaca data dari file CSV
def read_data():
    df = pd.read_csv("filtered_test2.csv")
    df['Time'] = pd.to_datetime(df['Time_Of_Day_Seconds'], unit='s') + timedelta(hours=7)
    return df

# Membuat aplikasi Dash
app = dash.Dash(__name__)

# Layout aplikasi
app.layout = html.Div([
    html.H1('Time Series Data Visualization with FDA Analysis'),
    
    # Dropdown untuk memilih kolom yang ingin ditambahkan
    dcc.Dropdown(
        id='column-dropdown',
        options=[{'label': col, 'value': col} for col in read_data().columns if col not in ['Time', 'Time_Of_Day_Seconds']],
        multi=True,  # Memungkinkan pemilihan beberapa kolom
        value=[],  # Nilai default kosong (grafik awal kosong)
        style={'width': '100%'}
    ),
    
    # Grafik untuk menampilkan data
    dcc.Graph(id='time-series-graph'),
    
    # Interval untuk memperbarui grafik setiap detik
    dcc.Interval(
        id='interval-update',
        interval=1000,  # Interval 1000 ms = 1 detik
        n_intervals=0
    )
])

# Callback untuk memperbarui grafik berdasarkan kolom yang dipilih
@app.callback(
    Output('time-series-graph', 'figure'),
    [Input('column-dropdown', 'value'),
     Input('interval-update', 'n_intervals')]
)
def update_graph(selected_columns, n_intervals):
    # Membaca data terbaru dari CSV
    df = read_data()

    if not selected_columns:
        return {
            'data': [],
            'layout': go.Layout(
                title='No Data Selected',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Value'}
            )
        }

    # Menyiapkan data untuk IncFDO berdasarkan kolom yang dipilih
    dataf = df[selected_columns]

    # Menyiapkan data untuk analisis FDA
    X = dataf.T.to_numpy()

    # Inisialisasi dan fitting data menggunakan IncFDO
    inc_fdo = IncFDO()
    inc_fdo.initial_fit(X)

    # Membuat plot data untuk visualisasi
    plot_data = pd.DataFrame({
        'MO': inc_fdo.MO,
        'VO': inc_fdo.VO,
        'Label': selected_columns  # Menggunakan nama kolom sebagai label
    })

    # Membuat scatter plot menggunakan plotly express
    fig = px.scatter(
        plot_data, 
        x='MO', 
        y='VO', 
        color='Label',  # Warna berdasarkan label unik
        title='MS Plot',
        labels={'MO': 'MO', 'VO': 'VO'},
        template='plotly'
    )

    # Menampilkan plot
    return fig

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run_server(debug=True)