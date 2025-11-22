"""
Minimal Pharmaceutical Manufacturing Digital Twin for Databricks Apps
"""
import os
from datetime import datetime, timedelta
import random
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Expose server for WSGI

# Simple data generator
def generate_data():
    timestamps = [datetime.now() - timedelta(hours=24-i) for i in range(24)]
    return pd.DataFrame({
        'time': timestamps,
        'temp': [37 + random.uniform(-0.2, 0.2) for _ in range(24)],
        'ph': [7.0 + random.uniform(-0.1, 0.1) for _ in range(24)],
    })

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Pharmaceutical Manufacturing Digital Twin", className="text-center my-4"),
            html.P("Powered by Databricks Lakehouse Platform", className="text-center text-muted"),
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Active Batches", className="card-title"),
                    html.H2("2", className="text-primary"),
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Avg Yield", className="card-title"),
                    html.H2("91.5%", className="text-success"),
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Equipment at Risk", className="card-title"),
                    html.H2("2", className="text-warning"),
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Bioreactors Online", className="card-title"),
                    html.H2("4", className="text-info"),
                ])
            ])
        ], width=3),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Bioreactor Monitoring")),
                dbc.CardBody([
                    dcc.Graph(id='bioreactor-graph')
                ])
            ])
        ])
    ]),

    dcc.Interval(id='interval', interval=30000, n_intervals=0)
], fluid=True)

# Callback
@app.callback(
    Output('bioreactor-graph', 'figure'),
    Input('interval', 'n_intervals')
)
def update_graph(n):
    df = generate_data()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['temp'],
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='#ff5f46', width=2)
    ))

    fig.update_layout(
        title="Bioreactor Temperature - Last 24 Hours",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        hovermode='x unified',
        height=400
    )

    return fig

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run_server(debug=False, host='0.0.0.0', port=port)
