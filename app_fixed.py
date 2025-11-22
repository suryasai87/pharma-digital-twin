"""
Pharmaceutical Manufacturing Digital Twin - Databricks App
Optimized for Databricks Apps deployment
"""
import os
import random
from datetime import datetime, timedelta
import dash
from dash import dcc, html, Input, Output, dash_table
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
                'agitation_rpm': int(120 + np.random.normal(0, 5)),
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
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Pharma Digital Twin"
)

# IMPORTANT: Expose server for Databricks Apps
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
            html.Div([
                html.H6("Pharmaceutical Manufacturing Digital Twin",
                       style={'color': 'white', 'margin': 0, 'fontWeight': 600}),
                html.Small("Powered by Databricks Lakehouse Platform",
                          style={'color': 'white', 'opacity': 0.8, 'fontSize': '0.7rem'}),
            ], style={'display': 'flex', 'flexDirection': 'column'}),
        ], fluid=True),
        color=COLORS['primary'],
        dark=True,
        sticky="top",
    )

# Sidebar
def create_sidebar():
    menu_items = [
        {'id': 'overview', 'label': 'Overview', 'icon': '📊'},
        {'id': 'bioreactor', 'label': 'Bioreactor Monitoring', 'icon': '🧬'},
        {'id': 'batch', 'label': 'Batch Quality', 'icon': '✅'},
        {'id': 'maintenance', 'label': 'Maintenance', 'icon': '🔧'},
        {'id': 'contamination', 'label': 'Contamination', 'icon': '⚠️'},
    ]

    return html.Div([
        dbc.Nav([
            dbc.NavLink(
                [html.Span(item['icon'], style={'marginRight': '10px'}),
                 html.Span(item['label'])],
                href=f"#{item['id']}",
                style={'borderRadius': '4px', 'margin': '4px', 'padding': '10px'}
            ) for item in menu_items
        ], vertical=True, pills=True),
    ], style={
        'position': 'fixed',
        'top': '56px',
        'left': 0,
        'bottom': 0,
        'width': '250px',
        'backgroundColor': 'white',
        'borderRight': '1px solid #dce0e2',
        'padding': '16px 8px',
        'overflowY': 'auto',
    })

# Overview Page
def create_overview_page():
    batches = pharma_data_generator.generate_batch_records(20)
    equipment = pharma_data_generator.generate_equipment_health(10)

    active_batches = len([b for b in batches if b['status'] == 'In Progress'])
    avg_yield = sum(b['yield_percent'] for b in batches) / len(batches)
    equipment_at_risk = len([e for e in equipment if e['health_score'] < 80])

    return html.Div([
        html.H4("Manufacturing Overview", style={'marginBottom': '24px', 'fontWeight': 600}),

        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Active Batches", style={'fontSize': '0.9rem', 'marginBottom': '8px'}),
                html.H3(str(active_batches), style={'color': COLORS['info'], 'fontWeight': 700}),
            ]), style={'background': f"linear-gradient(135deg, {COLORS['info']}15 0%, {COLORS['info']}05 100%)"}), width=3),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Avg Batch Yield", style={'fontSize': '0.9rem', 'marginBottom': '8px'}),
                html.H3(f"{avg_yield:.1f}%", style={'color': COLORS['success'], 'fontWeight': 700}),
            ]), style={'background': f"linear-gradient(135deg, {COLORS['success']}15 0%, {COLORS['success']}05 100%)"}), width=3),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Equipment at Risk", style={'fontSize': '0.9rem', 'marginBottom': '8px'}),
                html.H3(str(equipment_at_risk), style={'color': COLORS['warning'], 'fontWeight': 700}),
            ]), style={'background': f"linear-gradient(135deg, {COLORS['warning']}15 0%, {COLORS['warning']}05 100%)"}), width=3),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Bioreactors Online", style={'fontSize': '0.9rem', 'marginBottom': '8px'}),
                html.H3("4", style={'color': COLORS['secondary'], 'fontWeight': 700}),
            ]), style={'background': f"linear-gradient(135deg, {COLORS['secondary']}15 0%, {COLORS['secondary']}05 100%)"}), width=3),
        ], style={'marginBottom': '24px'}),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("System Health", style={'fontWeight': 600}),
                dbc.CardBody([
                    dbc.Alert("✓ All bioreactors operational", color="success", style={'marginBottom': '8px'}),
                    dbc.Alert(f"⚠ {equipment_at_risk} equipment units need attention", color="warning", style={'marginBottom': '8px'}),
                    dbc.Alert("✓ No contamination detected", color="success"),
                ])
            ]), width=6),

            dbc.Col(dbc.Card([
                dbc.CardHeader("Recent Activity", style={'fontWeight': 600}),
                dbc.CardBody([
                    html.P(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style={'fontSize': '0.85rem'}),
                    html.Hr(),
                    html.Ul([
                        html.Li("Batch B2024-001 in exponential phase"),
                        html.Li("Equipment health check completed"),
                        html.Li("ML models updated"),
                    ], style={'fontSize': '0.85rem', 'paddingLeft': '20px'}),
                ])
            ]), width=6),
        ])
    ])

# Bioreactor Page
def create_bioreactor_page():
    df = pharma_data_generator.generate_bioreactor_timeseries("BR-01", hours=24)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature (°C)', 'pH Level', 'Dissolved Oxygen (%)', 'Cell Density (OD600)')
    )

    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'],
                            name='Temp', line=dict(color=COLORS['secondary'], width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ph'],
                            name='pH', line=dict(color=COLORS['info'], width=2)), row=1, col=2)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['dissolved_oxygen'],
                            name='DO', line=dict(color=COLORS['success'], width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['cell_density'],
                            name='Density', line=dict(color='#9b59b6', width=2)), row=2, col=2)

    fig.update_layout(height=700, showlegend=False, plot_bgcolor='white')
    fig.update_xaxes(showgrid=True, gridcolor='#e0e0e0')
    fig.update_yaxes(showgrid=True, gridcolor='#e0e0e0')

    return html.Div([
        html.H4("Bioreactor Real-Time Monitoring", style={'marginBottom': '24px', 'fontWeight': 600}),
        dbc.Card([
            dbc.CardHeader("Bioreactor-01 (Batch B2024-001)", style={'fontWeight': 600}),
            dbc.CardBody(dcc.Graph(figure=fig, config={'displayModeBar': False}))
        ])
    ])

# Batch Quality Page
def create_batch_page():
    batches = pharma_data_generator.generate_batch_records(15)
    df = pd.DataFrame(batches)

    return html.Div([
        html.H4("Batch Quality Control", style={'marginBottom': '24px', 'fontWeight': 600}),
        dbc.Card([
            dbc.CardHeader("Current Batch Status", style={'fontWeight': 600}),
            dbc.CardBody(
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[
                        {'name': 'Batch ID', 'id': 'batch_id'},
                        {'name': 'Product', 'id': 'product_name'},
                        {'name': 'Status', 'id': 'status'},
                        {'name': 'Yield %', 'id': 'yield_percent'},
                        {'name': 'Quality Score', 'id': 'quality_score'},
                    ],
                    style_cell={'textAlign': 'left', 'padding': '12px'},
                    style_header={'backgroundColor': COLORS['background'], 'fontWeight': 600},
                    page_size=10,
                )
            )
        ])
    ])

# Main Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    create_header(),
    create_sidebar(),
    html.Div(
        id='page-content',
        style={
            'marginLeft': '250px',
            'marginTop': '56px',
            'padding': '24px',
            'backgroundColor': COLORS['background'],
            'minHeight': 'calc(100vh - 56px)',
        }
    )
])

# Callbacks
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'hash')
)
def display_page(hash_value):
    if hash_value == '#bioreactor':
        return create_bioreactor_page()
    elif hash_value == '#batch':
        return create_batch_page()
    else:
        return create_overview_page()

# DO NOT include if __name__ == '__main__' for Databricks Apps
# The server object is used directly by gunicorn/WSGI server
