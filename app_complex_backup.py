"""
Pharmaceutical Manufacturing Digital Twin - Databricks Dash App
Main entry point for Databricks Apps deployment
Combines Dash frontend with FastAPI backend integration
"""
import os
from datetime import datetime, timedelta
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests

# Import synthetic data generator
import sys
sys.path.insert(0, os.path.dirname(__file__))
from backend.utils.synthetic_data import pharma_data_generator

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Pharmaceutical Manufacturing Digital Twin"
)

server = app.server

# Databricks color scheme
COLORS = {
    'primary': '#1b3139',
    'secondary': '#ff5f46',
    'info': '#016bc1',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'background': '#f9f7f4',
}

# API Base URL (use FastAPI backend if available)
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8001/api/v1")

# Helper function to safely call API
def call_api(endpoint, default_data):
    """Call FastAPI backend, fallback to synthetic data"""
    try:
        response = requests.get(f"{API_BASE}/{endpoint}", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return default_data

# Header Component
def create_header():
    return dbc.Navbar(
        dbc.Container([
            html.Div([
                html.H6(
                    "Pharmaceutical Manufacturing Digital Twin",
                    style={'fontWeight': 600, 'marginBottom': 0, 'color': '#ffffff'}
                ),
                html.Small(
                    "Powered by Databricks Lakehouse Platform",
                    style={'fontSize': '0.75rem', 'opacity': 0.8, 'color': '#ffffff'}
                ),
            ], style={'display': 'flex', 'flexDirection': 'column'}),
        ], fluid=True),
        color=COLORS['primary'],
        dark=True,
        sticky="top",
    )

# Sidebar Navigation
def create_sidebar():
    menu_items = [
        {'id': 'overview', 'label': 'Overview', 'icon': '📊'},
        {'id': 'bioreactor', 'label': 'Bioreactor Monitoring', 'icon': '🧬'},
        {'id': 'batch-quality', 'label': 'Batch Quality', 'icon': '✅'},
        {'id': 'maintenance', 'label': 'Predictive Maintenance', 'icon': '🔧'},
        {'id': 'contamination', 'label': 'Contamination Detection', 'icon': '⚠️'},
    ]

    return html.Div([
        dbc.Nav([
            dbc.NavLink(
                [
                    html.Span(item['icon'], style={'marginRight': '10px'}),
                    html.Span(item['label']),
                ],
                id=f"nav-{item['id']}",
                href=f"#{item['id']}",
                style={
                    'borderRadius': '4px',
                    'margin': '4px 8px',
                    'padding': '10px',
                }
            ) for item in menu_items
        ], vertical=True, pills=True),
    ], style={
        'position': 'fixed',
        'top': '56px',
        'left': 0,
        'bottom': 0,
        'width': '280px',
        'backgroundColor': '#ffffff',
        'borderRight': f"1px solid #dce0e2",
        'overflowY': 'auto',
        'paddingTop': '16px',
    })

# Overview Page
def create_overview_page():
    # Get data from API or synthetic
    bioreactors_data = call_api("bioreactor/list", [])
    batches_data = call_api("batch/list?limit=50", pharma_data_generator.generate_batch_records(50))
    equipment_data = call_api("equipment/list", pharma_data_generator.generate_equipment_health(15))

    # Calculate KPIs
    if isinstance(batches_data, list):
        active_batches = len([b for b in batches_data if b.get('status') == 'In Progress'])
        yields = [b.get('yield_percent', 0) for b in batches_data if b.get('yield_percent')]
        avg_yield = sum(yields) / len(yields) if yields else 0
    else:
        active_batches = 2
        avg_yield = 91.5

    if isinstance(equipment_data, list):
        equipment_at_risk = len([e for e in equipment_data if e.get('health_score', 100) < 80])
    else:
        equipment_at_risk = 2

    kpi_cards = [
        {'label': 'Active Batches', 'value': active_batches, 'color': COLORS['info']},
        {'label': 'Avg Batch Yield', 'value': f"{avg_yield:.1f}%", 'color': COLORS['success']},
        {'label': 'Equipment at Risk', 'value': equipment_at_risk, 'color': COLORS['warning']},
        {'label': 'Bioreactors Online', 'value': 4, 'color': COLORS['secondary']},
    ]

    return html.Div([
        html.H4("Manufacturing Overview", style={'marginBottom': '24px', 'fontWeight': 600}),

        # KPI Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P(kpi['label'], style={'marginBottom': '8px', 'fontSize': '0.9rem'}),
                        html.H3(str(kpi['value']), style={'fontWeight': 700, 'color': kpi['color']}),
                    ])
                ], style={
                    'background': f"linear-gradient(135deg, {kpi['color']}15 0%, {kpi['color']}05 100%)",
                    'border': f"1px solid {kpi['color']}30",
                })
            ], width=12, md=3) for kpi in kpi_cards
        ], style={'marginBottom': '24px'}),

        # System Status
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("System Health", style={'fontWeight': 600}),
                    dbc.CardBody([
                        dbc.Alert("✓ All bioreactors operational", color="success", style={'marginBottom': '8px'}),
                        dbc.Alert(f"⚠ {equipment_at_risk} equipment units need attention", color="warning", style={'marginBottom': '8px'}),
                        dbc.Alert("✓ No contamination detected", color="success"),
                    ])
                ])
            ], width=12, md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recent Activity", style={'fontWeight': 600}),
                    dbc.CardBody([
                        html.P(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                               style={'fontSize': '0.9rem'}),
                        html.Hr(),
                        html.P("• Batch B2024-001 in exponential phase", style={'fontSize': '0.85rem'}),
                        html.P("• Equipment health check completed", style={'fontSize': '0.85rem'}),
                        html.P("• ML models updated", style={'fontSize': '0.85rem'}),
                    ])
                ])
            ], width=12, md=6),
        ])
    ])

# Bioreactor Page
def create_bioreactor_page():
    df = pharma_data_generator.generate_bioreactor_timeseries("BR-01", hours=24, interval_minutes=10)

    # Create sensor charts
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature (°C)', 'pH Level', 'Dissolved Oxygen (%)', 'Cell Density (OD600)'),
        vertical_spacing=0.15
    )

    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], name='Temperature',
                            line=dict(color=COLORS['secondary'], width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ph'], name='pH',
                            line=dict(color=COLORS['info'], width=2)), row=1, col=2)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['dissolved_oxygen'], name='DO',
                            line=dict(color=COLORS['success'], width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['cell_density'], name='Cell Density',
                            line=dict(color='#9b59b6', width=2)), row=2, col=2)

    fig.update_layout(height=700, showlegend=False, plot_bgcolor='white', paper_bgcolor='white')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')

    return html.Div([
        html.H4("Bioreactor Real-Time Monitoring", style={'marginBottom': '24px', 'fontWeight': 600}),
        dbc.Card([
            dbc.CardHeader("Bioreactor-01 (Batch B2024-001)", style={'fontWeight': 600}),
            dbc.CardBody([
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ])
        ])
    ])

# Batch Quality Page
def create_batch_quality_page():
    batches = pharma_data_generator.generate_batch_records(20)
    df = pd.DataFrame(batches)

    return html.Div([
        html.H4("Batch Quality Control", style={'marginBottom': '24px', 'fontWeight': 600}),
        dbc.Card([
            dbc.CardHeader("Current Batch Status", style={'fontWeight': 600}),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df[['batch_id', 'product_name', 'status', 'yield_percent', 'quality_score']].to_dict('records'),
                    columns=[
                        {'name': 'Batch ID', 'id': 'batch_id'},
                        {'name': 'Product', 'id': 'product_name'},
                        {'name': 'Status', 'id': 'status'},
                        {'name': 'Yield %', 'id': 'yield_percent', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                        {'name': 'Quality Score', 'id': 'quality_score', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                    ],
                    style_cell={'textAlign': 'left', 'padding': '12px'},
                    style_header={'backgroundColor': COLORS['background'], 'fontWeight': 600},
                    style_data_conditional=[
                        {'if': {'filter_query': '{status} = "Released"'}, 'backgroundColor': '#e8f5e9'},
                        {'if': {'filter_query': '{status} = "In Progress"'}, 'backgroundColor': '#fff8e1'},
                    ],
                    page_size=10,
                )
            ])
        ])
    ])

# Maintenance Page
def create_maintenance_page():
    equipment = pharma_data_generator.generate_equipment_health(10)
    df = pd.DataFrame(equipment)

    return html.Div([
        html.H4("Predictive Maintenance", style={'marginBottom': '24px', 'fontWeight': 600}),
        dbc.Card([
            dbc.CardHeader("Equipment Health Dashboard", style={'fontWeight': 600}),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df[['name', 'type', 'health_score', 'status', 'next_maintenance']].to_dict('records'),
                    columns=[
                        {'name': 'Equipment', 'id': 'name'},
                        {'name': 'Type', 'id': 'type'},
                        {'name': 'Health Score', 'id': 'health_score', 'type': 'numeric'},
                        {'name': 'Status', 'id': 'status'},
                        {'name': 'Next Maintenance', 'id': 'next_maintenance'},
                    ],
                    style_cell={'textAlign': 'left', 'padding': '12px'},
                    style_header={'backgroundColor': COLORS['background'], 'fontWeight': 600},
                    style_data_conditional=[
                        {'if': {'filter_query': '{status} = "Critical"'}, 'backgroundColor': '#ffebee', 'color': '#c62828', 'fontWeight': 600},
                        {'if': {'filter_query': '{status} = "Warning"'}, 'backgroundColor': '#fff8e1', 'color': '#f57f17'},
                        {'if': {'filter_query': '{status} = "Operational"'}, 'backgroundColor': '#e8f5e9'},
                    ],
                    page_size=10,
                )
            ])
        ])
    ])

# Contamination Page
def create_contamination_page():
    alerts = pharma_data_generator.generate_contamination_alerts(15)
    df = pd.DataFrame(alerts)

    return html.Div([
        html.H4("Contamination Detection System", style={'marginBottom': '24px', 'fontWeight': 600}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P("High Risk", style={'marginBottom': '8px', 'fontSize': '0.9rem'}),
                        html.H3(str(len([a for a in alerts if a['status'] == 'High'])),
                               style={'fontWeight': 700, 'color': COLORS['danger']}),
                    ])
                ], style={'background': f"linear-gradient(135deg, {COLORS['danger']}15 0%, {COLORS['danger']}05 100%)"})
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P("Medium Risk", style={'marginBottom': '8px', 'fontSize': '0.9rem'}),
                        html.H3(str(len([a for a in alerts if a['status'] == 'Medium'])),
                               style={'fontWeight': 700, 'color': COLORS['warning']}),
                    ])
                ], style={'background': f"linear-gradient(135deg, {COLORS['warning']}15 0%, {COLORS['warning']}05 100%)"})
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P("Low Risk", style={'marginBottom': '8px', 'fontSize': '0.9rem'}),
                        html.H3(str(len([a for a in alerts if a['status'] == 'Low'])),
                               style={'fontWeight': 700, 'color': COLORS['success']}),
                    ])
                ], style={'background': f"linear-gradient(135deg, {COLORS['success']}15 0%, {COLORS['success']}05 100%)"})
            ], width=4),
        ], style={'marginBottom': '24px'}),

        dbc.Card([
            dbc.CardHeader("Recent Contamination Alerts", style={'fontWeight': 600}),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df[['timestamp', 'bioreactor', 'risk_score', 'status', 'action']].to_dict('records'),
                    columns=[
                        {'name': 'Timestamp', 'id': 'timestamp'},
                        {'name': 'Bioreactor', 'id': 'bioreactor'},
                        {'name': 'Risk Score', 'id': 'risk_score', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                        {'name': 'Status', 'id': 'status'},
                        {'name': 'Action', 'id': 'action'},
                    ],
                    style_cell={'textAlign': 'left', 'padding': '12px'},
                    style_header={'backgroundColor': COLORS['background'], 'fontWeight': 600},
                    page_size=10,
                )
            ])
        ])
    ])

# Main Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='interval-component', interval=30000, n_intervals=0),  # 30 seconds
    create_header(),
    create_sidebar(),
    html.Div([
        html.Div(id='page-content', style={'padding': '24px'})
    ], style={
        'marginLeft': '280px',
        'marginTop': '56px',
        'backgroundColor': COLORS['background'],
        'minHeight': 'calc(100vh - 56px)',
    })
])

# Callbacks
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'hash')
)
def display_page(hash_value):
    if not hash_value or hash_value == '#overview':
        return create_overview_page()
    elif hash_value == '#bioreactor':
        return create_bioreactor_page()
    elif hash_value == '#batch-quality':
        return create_batch_quality_page()
    elif hash_value == '#maintenance':
        return create_maintenance_page()
    elif hash_value == '#contamination':
        return create_contamination_page()
    else:
        return create_overview_page()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run_server(debug=False, host='0.0.0.0', port=port)
