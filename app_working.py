import os
from datetime import datetime, timedelta
import random
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Initialize the Dash app with Bootstrap theme
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
    'text': '#1b3139',
    'border': '#dce0e2',
}

# Mock data generators for pharmaceutical manufacturing
def generate_bioreactor_data(hours=24):
    """Generate mock bioreactor sensor data"""
    timestamps = [datetime.now() - timedelta(hours=hours-i) for i in range(hours)]

    # Critical Process Parameters
    temperature = [37.0 + random.uniform(-0.2, 0.2) for _ in range(hours)]  # ±0.1°C precision
    ph = [7.0 + random.uniform(-0.1, 0.1) for _ in range(hours)]  # ±0.05 pH units
    dissolved_oxygen = [45 + random.uniform(-5, 5) for _ in range(hours)]  # % saturation
    agitation_rpm = [120 + random.randint(-5, 5) for _ in range(hours)]
    pressure = [1.2 + random.uniform(-0.02, 0.02) for _ in range(hours)]  # ±0.01 bar

    # Critical Quality Attributes
    cell_density = [i * 0.15 + random.uniform(-0.05, 0.05) for i in range(hours)]  # OD600
    viable_cell_count = [i * 2.5e6 + random.uniform(-1e5, 1e5) for i in range(hours)]  # cells/mL

    return pd.DataFrame({
        'timestamp': timestamps,
        'temperature': temperature,
        'ph': ph,
        'dissolved_oxygen': dissolved_oxygen,
        'agitation_rpm': agitation_rpm,
        'pressure': pressure,
        'cell_density': cell_density,
        'viable_cell_count': viable_cell_count
    })

def generate_batch_data():
    """Generate mock batch records"""
    batches = []
    batch_ids = ['B2024-001', 'B2024-002', 'B2024-003', 'B2024-004', 'B2024-005', 'B2024-006']
    products = ['mAb-A', 'Vaccine-X', 'mAb-B', 'Insulin-Pro', 'mAb-A', 'Vaccine-Y']
    statuses = ['In Progress', 'QC Review', 'Released', 'Released', 'In Progress', 'QC Review']
    yields = [92.5, 88.3, 94.1, 91.7, 89.2, 93.5]

    for i, batch_id in enumerate(batch_ids):
        batches.append({
            'batch_id': batch_id,
            'product': products[i],
            'start_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            'status': statuses[i],
            'yield_percent': yields[i],
            'quality_score': random.uniform(90, 100)
        })

    return pd.DataFrame(batches)

def generate_equipment_health():
    """Generate mock equipment health data"""
    equipment = [
        {'name': 'Bioreactor-01', 'type': 'Bioreactor', 'health_score': 95, 'status': 'Operational', 'next_maintenance': '2025-01-15'},
        {'name': 'Chromatography-A1', 'type': 'HPLC', 'health_score': 78, 'status': 'Warning', 'next_maintenance': '2024-12-20'},
        {'name': 'Centrifuge-02', 'type': 'Centrifuge', 'health_score': 88, 'status': 'Operational', 'next_maintenance': '2025-01-08'},
        {'name': 'Bioreactor-02', 'type': 'Bioreactor', 'health_score': 92, 'status': 'Operational', 'next_maintenance': '2025-01-22'},
        {'name': 'Lyophilizer-01', 'type': 'Freeze Dryer', 'health_score': 65, 'status': 'Critical', 'next_maintenance': '2024-12-10'},
        {'name': 'Filtration-Unit-03', 'type': 'TFF System', 'health_score': 82, 'status': 'Operational', 'next_maintenance': '2024-12-28'},
    ]
    return pd.DataFrame(equipment)

def generate_contamination_alerts():
    """Generate mock contamination detection alerts"""
    alerts = [
        {'timestamp': '2024-12-05 14:23', 'bioreactor': 'BR-03', 'risk_score': 0.23, 'status': 'Low', 'action': 'Monitor'},
        {'timestamp': '2024-12-05 10:15', 'bioreactor': 'BR-01', 'risk_score': 0.67, 'status': 'Medium', 'action': 'Investigate'},
        {'timestamp': '2024-12-04 22:45', 'bioreactor': 'BR-02', 'risk_score': 0.15, 'status': 'Low', 'action': 'Monitor'},
        {'timestamp': '2024-12-04 18:30', 'bioreactor': 'BR-04', 'risk_score': 0.89, 'status': 'High', 'action': 'Immediate Action'},
    ]
    return pd.DataFrame(alerts)

# Header Component
def create_header():
    return dbc.Navbar(
        dbc.Container([
            html.Div([
                html.Img(
                    src="/assets/logo.svg",
                    height="32px",
                    style={'marginRight': '16px'}
                ),
                html.H6(
                    "Pharmaceutical Manufacturing",
                    style={'fontWeight': 600, 'marginRight': '16px', 'marginBottom': 0, 'color': '#ffffff'}
                ),
                html.Div([
                    html.Div(
                        "Digital Twin Platform",
                        style={'fontWeight': 500, 'lineHeight': 1.2, 'fontSize': '1rem', 'color': '#ffffff'}
                    ),
                    html.Small(
                        "Powered by Databricks Lakehouse & Zerobus",
                        style={'fontSize': '0.65rem', 'opacity': 0.8, 'lineHeight': 1, 'color': '#ffffff'}
                    ),
                ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'flex-start'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ], fluid=True),
        color=COLORS['primary'],
        dark=True,
        sticky="top",
        style={'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.15)'}
    )

# Sidebar Navigation
def create_sidebar():
    menu_items = [
        {'id': 'overview', 'label': 'Overview', 'icon': '📊'},
        {'id': 'bioreactor', 'label': 'Bioreactor Monitoring', 'icon': '🧬'},
        {'id': 'batch-quality', 'label': 'Batch Quality Control', 'icon': '✅'},
        {'id': 'predictive-maintenance', 'label': 'Predictive Maintenance', 'icon': '🔧'},
        {'id': 'contamination', 'label': 'Contamination Detection', 'icon': '⚠️'},
    ]

    return html.Div([
        html.Div([
            dbc.Nav([
                dbc.NavLink(
                    [
                        html.Span(item['icon'], style={'marginRight': '10px', 'minWidth': '40px'}),
                        html.Span(item['label']),
                    ],
                    id=f"nav-{item['id']}",
                    href=f"/{item['id']}",
                    style={
                        'borderRadius': '4px',
                        'margin': '4px 8px',
                        'padding': '10px',
                        'fontWeight': 500,
                        'fontSize': '0.95rem',
                        'color': COLORS['text'],
                    }
                ) for item in menu_items
            ], vertical=True, pills=True),
        ], style={'overflow': 'auto', 'marginTop': '16px'}),
    ], style={
        'position': 'fixed',
        'top': '56px',
        'left': 0,
        'bottom': 0,
        'width': '280px',
        'backgroundColor': '#ffffff',
        'borderRight': f"1px solid {COLORS['border']}",
        'zIndex': 1000,
    })

# Overview Page
def create_overview_page():
    bioreactor_df = generate_bioreactor_data(24)
    batch_df = generate_batch_data()
    equipment_df = generate_equipment_health()

    # Calculate KPIs
    active_batches = len(batch_df[batch_df['status'] == 'In Progress'])
    avg_yield = batch_df['yield_percent'].mean()
    equipment_at_risk = len(equipment_df[equipment_df['health_score'] < 80])

    kpi_cards = [
        {'label': 'Active Batches', 'value': active_batches, 'color': COLORS['info']},
        {'label': 'Avg Batch Yield', 'value': f"{avg_yield:.1f}%", 'color': COLORS['success']},
        {'label': 'Equipment at Risk', 'value': equipment_at_risk, 'color': COLORS['warning']},
        {'label': 'Current Cell Density', 'value': f"{bioreactor_df['cell_density'].iloc[-1]:.2f}", 'color': COLORS['secondary']},
    ]

    return html.Div([
        html.H4("Manufacturing Overview", style={'marginBottom': '24px', 'fontWeight': 600, 'color': COLORS['primary']}),

        # KPI Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P(kpi['label'], style={'color': '#5a6f77', 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                        html.H3(str(kpi['value']), style={'fontWeight': 700, 'color': kpi['color'], 'marginBottom': 0}),
                    ])
                ], style={
                    'height': '100%',
                    'background': f"linear-gradient(135deg, {kpi['color']}15 0%, {kpi['color']}05 100%)",
                    'border': f"1px solid {kpi['color']}30",
                    'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.08)',
                })
            ], width=12, md=6, lg=3, style={'marginBottom': '24px'}) for kpi in kpi_cards
        ]),

        # Manufacturing Status
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Real-Time Process Status", style={'fontWeight': 600, 'backgroundColor': COLORS['background']}),
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.Strong("Temperature: "),
                                html.Span(f"{bioreactor_df['temperature'].iloc[-1]:.2f}°C",
                                         style={'color': COLORS['success'], 'fontWeight': 600})
                            ], style={'marginBottom': '8px'}),
                            html.Div([
                                html.Strong("pH: "),
                                html.Span(f"{bioreactor_df['ph'].iloc[-1]:.2f}",
                                         style={'color': COLORS['success'], 'fontWeight': 600})
                            ], style={'marginBottom': '8px'}),
                            html.Div([
                                html.Strong("Dissolved Oxygen: "),
                                html.Span(f"{bioreactor_df['dissolved_oxygen'].iloc[-1]:.1f}%",
                                         style={'color': COLORS['success'], 'fontWeight': 600})
                            ], style={'marginBottom': '8px'}),
                            html.Div([
                                html.Strong("Agitation: "),
                                html.Span(f"{bioreactor_df['agitation_rpm'].iloc[-1]:.0f} RPM",
                                         style={'color': COLORS['success'], 'fontWeight': 600})
                            ]),
                        ])
                    ])
                ], style={'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.08)', 'marginBottom': '24px'})
            ], width=12, md=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("System Health", style={'fontWeight': 600, 'backgroundColor': COLORS['background']}),
                    dbc.CardBody([
                        dbc.Alert("✓ All bioreactors operational", color="success", style={'marginBottom': '8px', 'padding': '8px'}),
                        dbc.Alert("⚠ 2 equipment units require attention", color="warning", style={'marginBottom': '8px', 'padding': '8px'}),
                        dbc.Alert("✓ No contamination detected", color="success", style={'marginBottom': 0, 'padding': '8px'}),
                    ])
                ], style={'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.08)', 'marginBottom': '24px'})
            ], width=12, md=6),
        ]),
    ])

# Bioreactor Monitoring Page
def create_bioreactor_page():
    df = generate_bioreactor_data(24)

    # Create subplots for sensor data
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('Temperature (°C)', 'pH Level', 'Dissolved Oxygen (%)',
                       'Agitation Speed (RPM)', 'Cell Density (OD600)', 'Viable Cell Count (cells/mL)'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    # Temperature
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], mode='lines+markers',
                            name='Temperature', line=dict(color=COLORS['secondary'], width=2),
                            marker=dict(size=4)), row=1, col=1)
    fig.add_hline(y=37.1, line_dash="dash", line_color="red", annotation_text="Upper Limit", row=1, col=1)
    fig.add_hline(y=36.9, line_dash="dash", line_color="red", annotation_text="Lower Limit", row=1, col=1)

    # pH
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ph'], mode='lines+markers',
                            name='pH', line=dict(color=COLORS['info'], width=2),
                            marker=dict(size=4)), row=1, col=2)
    fig.add_hline(y=7.05, line_dash="dash", line_color="red", annotation_text="Upper Limit", row=1, col=2)
    fig.add_hline(y=6.95, line_dash="dash", line_color="red", annotation_text="Lower Limit", row=1, col=2)

    # Dissolved Oxygen
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['dissolved_oxygen'], mode='lines+markers',
                            name='DO', line=dict(color=COLORS['success'], width=2),
                            marker=dict(size=4)), row=2, col=1)

    # Agitation
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['agitation_rpm'], mode='lines+markers',
                            name='RPM', line=dict(color=COLORS['warning'], width=2),
                            marker=dict(size=4)), row=2, col=2)

    # Cell Density
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['cell_density'], mode='lines+markers',
                            name='OD600', line=dict(color='#9b59b6', width=2),
                            marker=dict(size=4)), row=3, col=1)

    # Viable Cell Count
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['viable_cell_count'], mode='lines+markers',
                            name='Cells/mL', line=dict(color='#e67e22', width=2),
                            marker=dict(size=4)), row=3, col=2)

    fig.update_layout(
        height=900,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='DM Sans, sans-serif', size=11),
        margin=dict(t=40, b=20, l=60, r=20)
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')

    return html.Div([
        html.H4("Bioreactor Real-Time Monitoring", style={'marginBottom': '24px', 'fontWeight': 600, 'color': COLORS['primary']}),

        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.Span("Bioreactor-01 ", style={'fontWeight': 600}),
                    html.Span("(Batch B2024-001 - mAb-A Production)", style={'color': '#5a6f77'}),
                    html.Span(" • ", style={'margin': '0 8px'}),
                    html.Span("Status: ", style={'fontWeight': 500}),
                    dbc.Badge("Operational", color="success"),
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], style={'backgroundColor': COLORS['background']}),
            dbc.CardBody([
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ])
        ], style={'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.08)'})
    ])

# Batch Quality Control Page
def create_batch_quality_page():
    df = generate_batch_data()

    return html.Div([
        html.H4("Batch Quality Control", style={'marginBottom': '24px', 'fontWeight': 600, 'color': COLORS['primary']}),

        dbc.Card([
            dbc.CardHeader("Current Batch Status", style={'fontWeight': 600, 'backgroundColor': COLORS['background']}),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[
                        {'name': 'Batch ID', 'id': 'batch_id'},
                        {'name': 'Product', 'id': 'product'},
                        {'name': 'Start Date', 'id': 'start_date'},
                        {'name': 'Status', 'id': 'status'},
                        {'name': 'Yield %', 'id': 'yield_percent', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                        {'name': 'Quality Score', 'id': 'quality_score', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                    ],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '12px',
                        'fontFamily': '"DM Sans", sans-serif',
                        'fontSize': '14px',
                    },
                    style_header={
                        'backgroundColor': COLORS['background'],
                        'fontWeight': 600,
                        'color': COLORS['text'],
                        'borderBottom': f"2px solid {COLORS['border']}"
                    },
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{status} = "Released"'},
                            'backgroundColor': '#e8f5e9',
                        },
                        {
                            'if': {'filter_query': '{status} = "In Progress"'},
                            'backgroundColor': '#fff8e1',
                        },
                        {
                            'if': {'filter_query': '{yield_percent} < 90'},
                            'color': COLORS['danger'],
                            'fontWeight': 600
                        },
                    ],
                )
            ])
        ], style={'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.08)', 'marginBottom': '24px'}),

        # Yield Distribution Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Batch Yield Distribution", style={'fontWeight': 600, 'backgroundColor': COLORS['background']}),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=go.Figure(data=[
                                go.Bar(x=df['batch_id'], y=df['yield_percent'],
                                      marker_color=[COLORS['success'] if y >= 90 else COLORS['warning'] for y in df['yield_percent']],
                                      text=df['yield_percent'].apply(lambda x: f"{x:.1f}%"),
                                      textposition='outside')
                            ]).update_layout(
                                yaxis_title="Yield (%)",
                                xaxis_title="Batch ID",
                                plot_bgcolor='white',
                                paper_bgcolor='white',
                                height=350,
                                showlegend=False,
                                font=dict(family='DM Sans, sans-serif'),
                                margin=dict(t=20, b=40, l=60, r=20)
                            ).update_xaxes(showgrid=False).update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0'),
                            config={'displayModeBar': False}
                        )
                    ])
                ], style={'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.08)'})
            ], width=12)
        ])
    ])

# Predictive Maintenance Page
def create_predictive_maintenance_page():
    df = generate_equipment_health()

    return html.Div([
        html.H4("Predictive Maintenance", style={'marginBottom': '24px', 'fontWeight': 600, 'color': COLORS['primary']}),

        dbc.Card([
            dbc.CardHeader("Equipment Health Dashboard", style={'fontWeight': 600, 'backgroundColor': COLORS['background']}),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[
                        {'name': 'Equipment Name', 'id': 'name'},
                        {'name': 'Type', 'id': 'type'},
                        {'name': 'Health Score', 'id': 'health_score', 'type': 'numeric'},
                        {'name': 'Status', 'id': 'status'},
                        {'name': 'Next Maintenance', 'id': 'next_maintenance'},
                    ],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '12px',
                        'fontFamily': '"DM Sans", sans-serif',
                        'fontSize': '14px',
                    },
                    style_header={
                        'backgroundColor': COLORS['background'],
                        'fontWeight': 600,
                        'color': COLORS['text'],
                        'borderBottom': f"2px solid {COLORS['border']}"
                    },
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{status} = "Critical"'},
                            'backgroundColor': '#ffebee',
                            'color': '#c62828',
                            'fontWeight': 600
                        },
                        {
                            'if': {'filter_query': '{status} = "Warning"'},
                            'backgroundColor': '#fff8e1',
                            'color': '#f57f17',
                            'fontWeight': 600
                        },
                        {
                            'if': {'filter_query': '{status} = "Operational"'},
                            'backgroundColor': '#e8f5e9',
                        },
                    ],
                )
            ])
        ], style={'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.08)', 'marginBottom': '24px'}),

        # Equipment Health Gauge
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(f"{row['name']}", style={'fontWeight': 600, 'backgroundColor': COLORS['background']}),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=row['health_score'],
                                title={'text': f"Health Score<br><span style='font-size:0.8em;color:gray'>{row['type']}</span>"},
                                gauge={
                                    'axis': {'range': [None, 100]},
                                    'bar': {'color': COLORS['success'] if row['health_score'] >= 85 else COLORS['warning'] if row['health_score'] >= 70 else COLORS['danger']},
                                    'steps': [
                                        {'range': [0, 70], 'color': "rgba(231, 76, 60, 0.2)"},
                                        {'range': [70, 85], 'color': "rgba(243, 156, 18, 0.2)"},
                                        {'range': [85, 100], 'color': "rgba(46, 204, 113, 0.2)"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': 70
                                    }
                                }
                            )).update_layout(
                                height=250,
                                margin=dict(t=40, b=20, l=20, r=20),
                                font=dict(family='DM Sans, sans-serif')
                            ),
                            config={'displayModeBar': False}
                        )
                    ])
                ], style={'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.08)', 'marginBottom': '24px'})
            ], width=12, md=6, lg=4) for _, row in df.iterrows()
        ])
    ])

# Contamination Detection Page
def create_contamination_page():
    df = generate_contamination_alerts()

    return html.Div([
        html.H4("Contamination Detection System", style={'marginBottom': '24px', 'fontWeight': 600, 'color': COLORS['primary']}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P("Active Alerts", style={'color': '#5a6f77', 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                        html.H3("4", style={'fontWeight': 700, 'color': COLORS['info'], 'marginBottom': 0}),
                    ])
                ], style={'background': f"linear-gradient(135deg, {COLORS['info']}15 0%, {COLORS['info']}05 100%)", 'border': f"1px solid {COLORS['info']}30"})
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P("High Risk", style={'color': '#5a6f77', 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                        html.H3("1", style={'fontWeight': 700, 'color': COLORS['danger'], 'marginBottom': 0}),
                    ])
                ], style={'background': f"linear-gradient(135deg, {COLORS['danger']}15 0%, {COLORS['danger']}05 100%)", 'border': f"1px solid {COLORS['danger']}30"})
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P("Medium Risk", style={'color': '#5a6f77', 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                        html.H3("1", style={'fontWeight': 700, 'color': COLORS['warning'], 'marginBottom': 0}),
                    ])
                ], style={'background': f"linear-gradient(135deg, {COLORS['warning']}15 0%, {COLORS['warning']}05 100%)", 'border': f"1px solid {COLORS['warning']}30"})
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P("Low Risk", style={'color': '#5a6f77', 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                        html.H3("2", style={'fontWeight': 700, 'color': COLORS['success'], 'marginBottom': 0}),
                    ])
                ], style={'background': f"linear-gradient(135deg, {COLORS['success']}15 0%, {COLORS['success']}05 100%)", 'border': f"1px solid {COLORS['success']}30"})
            ], width=3),
        ], style={'marginBottom': '24px'}),

        dbc.Card([
            dbc.CardHeader("Recent Contamination Alerts", style={'fontWeight': 600, 'backgroundColor': COLORS['background']}),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[
                        {'name': 'Timestamp', 'id': 'timestamp'},
                        {'name': 'Bioreactor', 'id': 'bioreactor'},
                        {'name': 'Risk Score', 'id': 'risk_score', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                        {'name': 'Status', 'id': 'status'},
                        {'name': 'Recommended Action', 'id': 'action'},
                    ],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '12px',
                        'fontFamily': '"DM Sans", sans-serif',
                        'fontSize': '14px',
                    },
                    style_header={
                        'backgroundColor': COLORS['background'],
                        'fontWeight': 600,
                        'color': COLORS['text'],
                        'borderBottom': f"2px solid {COLORS['border']}"
                    },
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{status} = "High"'},
                            'backgroundColor': '#ffebee',
                            'color': '#c62828',
                            'fontWeight': 600
                        },
                        {
                            'if': {'filter_query': '{status} = "Medium"'},
                            'backgroundColor': '#fff8e1',
                            'color': '#f57f17',
                            'fontWeight': 600
                        },
                        {
                            'if': {'filter_query': '{status} = "Low"'},
                            'backgroundColor': '#e8f5e9',
                        },
                    ],
                )
            ])
        ], style={'boxShadow': '0px 2px 8px rgba(27, 49, 57, 0.08)'})
    ])

# Main Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='interval-component', interval=5000, n_intervals=0),  # Update every 5 seconds
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

# Callback for page navigation
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/' or pathname == '/overview':
        return create_overview_page()
    elif pathname == '/bioreactor':
        return create_bioreactor_page()
    elif pathname == '/batch-quality':
        return create_batch_quality_page()
    elif pathname == '/predictive-maintenance':
        return create_predictive_maintenance_page()
    elif pathname == '/contamination':
        return create_contamination_page()
    else:
        return create_overview_page()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run_server(debug=False, host='0.0.0.0', port=port)
