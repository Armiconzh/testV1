import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime, timedelta
import pytz

# Membaca data dari file CSV
def read_data():
    df = pd.read_csv("filtered_test2.csv")
    df['Time'] = pd.to_datetime(df['Time_Of_Day_Seconds'], unit='s') + timedelta(hours=7)
    return df

# Membuat aplikasi Dash
app = dash.Dash(__name__)

# Layout aplikasi
app.layout = html.Div([
    html.H1('Time Series Data Visualization'),
    
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

    traces = []
    
    # Membuat trace untuk setiap kolom yang dipilih
    for column in selected_columns:
        traces.append(go.Scatter(
            x=df['Time'],  # Gunakan kolom 'Time' sebagai sumbu X
            y=df[column],
            mode='lines',
            name=column
        ))

    # Layout untuk grafik
    figure = {
        'data': traces,
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
    
    return figure

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run_server(debug=True)
