"""
Pharmaceutical Manufacturing Digital Twin - Standalone Databricks App
All dependencies embedded for easy deployment
"""
import os
import random
from datetime import datetime, timedelta
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Synthetic Data Generator (embedded)
class PharmaDataGenerator:
    """Generate realistic pharmaceutical manufacturing data"""

    def __init__(self, seed: int = 42):
        Faker.seed(seed)
        random.seed(seed)
        np.random.seed(seed)

    def generate_bioreactor_timeseries(self, bioreactor_id: str, hours: int = 24, interval_minutes: int = 10) -> pd.DataFrame:
        """Generate realistic bioreactor sensor timeseries"""
        num_points = (hours * 60) // interval_minutes
        timestamps = [datetime.now() - timedelta(minutes=interval_minutes * i) for i in range(num_points, 0, -1)]

        data = []
        for i, ts in enumerate(timestamps):
            growth_phase_hours = i * interval_minutes / 60
            if growth_phase_hours < 4:
                phase, growth_factor = "lag", 0.1
            elif growth_phase_hours < 16:
                phase, growth_factor = "exponential", (growth_phase_hours - 4) / 12
            else:
                phase, growth_factor = "stationary", 1.0

            data.append({
                'timestamp': ts,
                'temperature': round(37.0 + np.random.normal(0, 0.05), 2),
                'ph': round(7.0 + np.random.normal(0, 0.02), 2),
                'dissolved_oxygen': round(45 + np.random.normal(0, 2), 1),
                'cell_density': round(max(0, growth_factor * 4.5 + np.random.normal(0, 0.1)), 2),
            })
        return pd.DataFrame(data)

    def generate_batch_records(self, num_batches: int = 20):
        """Generate synthetic batch records"""
        statuses = ["In Progress", "QC Review", "Released"]
        batches = []
        for i in range(num_batches):
            batches.append({
                'batch_id': f"B2024-{str(i+1).zfill(3)}",
                'product_name': random.choice(["mAb-A", "Vaccine-X", "Insulin-Pro"]),
                'status': random.choice(statuses),
                'yield_percent': round(np.random.normal(92, 4), 1),
                'quality_score': round(np.random.normal(95, 3), 1),
            })
        return batches

    def generate_equipment_health(self, num_equipment: int = 10):
        """Generate equipment health data"""
        equipment = []
        for i in range(num_equipment):
            health_score = random.uniform(65, 98)
            status = "Operational" if health_score >= 85 else ("Warning" if health_score >= 70 else "Critical")
            equipment.append({
                'name': f"Equipment-{i+1:02d}",
                'type': random.choice(["Bioreactor", "Centrifuge", "Lyophilizer"]),
                'health_score': round(health_score, 1),
                'status': status,
                'next_maintenance': (datetime.now() + timedelta(days=random.randint(5, 90))).strftime('%Y-%m-%d'),
            })
        return equipment

    def generate_contamination_alerts(self, num_alerts: int = 15):
        """Generate contamination alerts"""
        alerts = []
        for i in range(num_alerts):
            risk_score = np.random.beta(2, 5)
            status = "Low" if risk_score < 0.3 else ("Medium" if risk_score < 0.7 else "High")
            alerts.append({
                'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                'bioreactor': f"BR-{random.randint(1, 5):02d}",
                'risk_score': round(risk_score, 2),
                'status': status,
                'action': "Monitor" if status == "Low" else ("Investigate" if status == "Medium" else "Immediate Action"),
            })
        return alerts

# Initialize data generator
pharma_data_generator = PharmaDataGenerator()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Colors
COLORS = {
    'primary': '#1b3139',
    'secondary': '#ff5f46',
    'info': '#016bc1',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'background': '#f9f7f4',
}

# Header
def create_header():
    return dbc.Navbar(
        dbc.Container([
            html.H6("Pharmaceutical Manufacturing Digital Twin", style={'color': 'white', 'margin': 0}),
            html.Small("Powered by Databricks", style={'color': 'white', 'opacity': 0.8}),
        ]),
        color=COLORS['primary'],
        dark=True,
    )

# Overview Page
def create_overview_page():
    batches = pharma_data_generator.generate_batch_records(20)
    equipment = pharma_data_generator.generate_equipment_health(10)

    active_batches = len([b for b in batches if b['status'] == 'In Progress'])
    avg_yield = sum(b['yield_percent'] for b in batches) / len(batches)
    equipment_at_risk = len([e for e in equipment if e['health_score'] < 80])

    return html.Div([
        html.H4("Manufacturing Overview", style={'marginBottom': '20px'}),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Active Batches"),
                html.H3(str(active_batches), style={'color': COLORS['info']}),
            ])), width=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Avg Yield"),
                html.H3(f"{avg_yield:.1f}%", style={'color': COLORS['success']}),
            ])), width=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Equipment at Risk"),
                html.H3(str(equipment_at_risk), style={'color': COLORS['warning']}),
            ])), width=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Bioreactors Online"),
                html.H3("4", style={'color': COLORS['secondary']}),
            ])), width=3),
        ])
    ])

# Bioreactor Page
def create_bioreactor_page():
    df = pharma_data_generator.generate_bioreactor_timeseries("BR-01", hours=24)

    fig = make_subplots(rows=2, cols=2, subplot_titles=('Temperature', 'pH', 'DO', 'Cell Density'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], line=dict(color=COLORS['secondary'])), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ph'], line=dict(color=COLORS['info'])), row=1, col=2)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['dissolved_oxygen'], line=dict(color=COLORS['success'])), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['cell_density'], line=dict(color='#9b59b6')), row=2, col=2)
    fig.update_layout(height=600, showlegend=False)

    return html.Div([
        html.H4("Bioreactor Monitoring"),
        dbc.Card(dbc.CardBody(dcc.Graph(figure=fig)))
    ])

# Main Layout
app.layout = html.Div([
    dcc.Location(id='url'),
    create_header(),
    html.Div(id='page-content', style={'padding': '20px'})
])

@app.callback(Output('page-content', 'children'), Input('url', 'hash'))
def display_page(hash_value):
    if hash_value == '#bioreactor':
        return create_bioreactor_page()
    return create_overview_page()

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
