"""
Dashboard Interactivo de Análisis de Datos - Empresa Andina
Incluye tres vistas principales: Gerencial, Comercial y Operativo
"""

# Configurar encoding para Windows
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime

# ================================
# CARGA Y PROCESAMIENTO DE DATOS
# ================================

print("📊 Cargando datos...")

# Cargar todos los archivos CSV
ventas_df = pd.read_csv('tablas/ventas_andina.csv')
clientes_df = pd.read_csv('tablas/clientes_andina.csv')
inventario_df = pd.read_csv('tablas/inventario_andina.csv')
cartera_df = pd.read_csv('tablas/cartera_andina.csv')
productos_df = pd.read_csv('tablas/productos_andina.csv')
importaciones_df = pd.read_csv('tablas/importaciones_andina.csv')

# Convertir fechas
ventas_df['fecha'] = pd.to_datetime(ventas_df['fecha'])
clientes_df['fecha_alta'] = pd.to_datetime(clientes_df['fecha_alta'])
inventario_df['fecha_corte'] = pd.to_datetime(inventario_df['fecha_corte'])
cartera_df['fecha_factura'] = pd.to_datetime(cartera_df['fecha_factura'])
cartera_df['fecha_vencimiento'] = pd.to_datetime(cartera_df['fecha_vencimiento'])
importaciones_df['fecha_orden'] = pd.to_datetime(importaciones_df['fecha_orden'])
importaciones_df['fecha_llegada'] = pd.to_datetime(importaciones_df['fecha_llegada'])

# Calcular métricas derivadas en ventas
ventas_df['margen_pct'] = (ventas_df['margen_total_cop'] / ventas_df['subtotal_cop'] * 100).round(2)
ventas_df['mes'] = ventas_df['fecha'].dt.to_period('M').astype(str)
ventas_df['año'] = ventas_df['fecha'].dt.year

# Enriquecer ventas con información de clientes
ventas_df = ventas_df.merge(clientes_df[['cliente_id', 'nombre_cliente', 'tamano_cliente']], 
                            on='cliente_id', how='left')

# Calcular fechas mínimas y máximas para el filtro
fecha_min_ventas = ventas_df['fecha'].min()
fecha_max_ventas = ventas_df['fecha'].max()

# Obtener valores únicos para filtros
categorias_disponibles = sorted(ventas_df['categoria'].unique().tolist())
regiones_disponibles = sorted(ventas_df['region'].unique().tolist())
segmentos_disponibles = sorted(ventas_df['segmento'].unique().tolist())
centros_logisticos = sorted(inventario_df['centro_logistico'].unique().tolist())

print("✅ Datos cargados exitosamente")
print(f"   - Ventas: {len(ventas_df):,} registros")
print(f"   - Clientes: {len(clientes_df):,} registros")
print(f"   - Inventario: {len(inventario_df):,} registros")
print(f"   - Cartera: {len(cartera_df):,} registros")
print(f"   - Rango de fechas: {fecha_min_ventas.date()} a {fecha_max_ventas.date()}")

# ================================
# CONFIGURACIÓN DE LA APP
# ================================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Andina - Análisis de Datos"

# Exponer el servidor para deployment (necesario para Gunicorn)
server = app.server

# Colores y estilos
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c',
    'warning': '#ff7f0e',
    'danger': '#d62728',
    'info': '#17a2b8',
    'background': '#f8f9fa',
    'card': '#ffffff'
}

# ================================
# FUNCIONES AUXILIARES
# ================================

def create_kpi_card(title, value, icon="📊", color=COLORS['primary']):
    """Crea una tarjeta de KPI"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={'fontSize': '2rem', 'marginRight': '10px'}),
                html.Div([
                    html.H6(title, className="text-muted mb-1"),
                    html.H4(value, className="mb-0", style={'color': color, 'fontWeight': 'bold'})
                ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
            ])
        ])
    ], className="mb-3 shadow-sm")

def format_currency(value):
    """Formatea números como moneda colombiana"""
    return f"${value:,.0f}".replace(",", ".")

def format_number(value):
    """Formatea números con separadores de miles"""
    return f"{value:,.0f}".replace(",", ".")

# ================================
# DASHBOARD GERENCIAL
# ================================

def create_gerencial_layout(ventas_filtradas, cartera_filtrada):
    """Crea el layout del Dashboard Gerencial con datos filtrados"""
    
    # KPIs principales
    total_ventas = ventas_filtradas['subtotal_cop'].sum()
    total_clientes = clientes_df[clientes_df['estado'] == 'Activo']['cliente_id'].nunique()
    total_margen = ventas_filtradas['margen_total_cop'].sum()
    cartera_vencida = cartera_filtrada[cartera_filtrada['dias_mora'] > 0]['saldo_cop'].sum()
    
    # Gráfico: Tendencia de ventas mensual
    ventas_mes = ventas_filtradas.groupby('mes').agg({
        'subtotal_cop': 'sum',
        'margen_total_cop': 'sum'
    }).reset_index()
    
    fig_tendencia = go.Figure()
    fig_tendencia.add_trace(go.Scatter(
        x=ventas_mes['mes'], 
        y=ventas_mes['subtotal_cop']/1e6,
        mode='lines+markers',
        name='Ventas',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8)
    ))
    fig_tendencia.update_layout(
        title="Tendencia de Ventas Mensual",
        xaxis_title="Mes",
        yaxis_title="Ventas (Millones COP)",
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Gráfico: Ventas por región (treemap)
    ventas_region = ventas_filtradas.groupby('region')['subtotal_cop'].sum().reset_index()
    fig_region = px.treemap(
        ventas_region,
        path=['region'],
        values='subtotal_cop',
        title='Distribución de Ventas por Región',
        color='subtotal_cop',
        color_continuous_scale='Blues'
    )
    
    # Gráfico: Top 10 productos
    top_productos = ventas_filtradas.groupby('subcategoria').agg({
        'subtotal_cop': 'sum',
        'cantidad': 'sum'
    }).sort_values('subtotal_cop', ascending=False).head(10).reset_index()
    
    fig_productos = px.bar(
        top_productos,
        x='subtotal_cop',
        y='subcategoria',
        orientation='h',
        title='Top 10 Productos por Ventas',
        labels={'subtotal_cop': 'Ventas (COP)', 'subcategoria': 'Producto'},
        color='subtotal_cop',
        color_continuous_scale='Greens'
    )
    fig_productos.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
    
    # Gráfico: Margen por categoría
    margen_categoria = ventas_filtradas.groupby('categoria').agg({
        'margen_total_cop': 'sum',
        'subtotal_cop': 'sum'
    }).reset_index()
    margen_categoria['margen_pct'] = (margen_categoria['margen_total_cop'] / margen_categoria['subtotal_cop'] * 100).round(2)
    
    fig_margen = px.bar(
        margen_categoria,
        x='categoria',
        y='margen_pct',
        title='Margen Porcentual por Categoría',
        labels={'margen_pct': 'Margen (%)', 'categoria': 'Categoría'},
        color='margen_pct',
        color_continuous_scale='RdYlGn'
    )
    
    return dbc.Container([
        html.H3("📈 Dashboard Gerencial - Visión General", className="mb-4 mt-3"),
        
        # KPIs
        dbc.Row([
            dbc.Col(create_kpi_card("Ventas Totales", format_currency(total_ventas), "💰", COLORS['success']), md=3),
            dbc.Col(create_kpi_card("Clientes Activos", format_number(total_clientes), "👥", COLORS['info']), md=3),
            dbc.Col(create_kpi_card("Margen Total", format_currency(total_margen), "📊", COLORS['primary']), md=3),
            dbc.Col(create_kpi_card("Cartera Vencida", format_currency(cartera_vencida), "⚠️", COLORS['danger']), md=3),
        ]),
        
        # Gráficos principales
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_tendencia)])
                ], className="shadow-sm mb-3")
            ], md=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_margen)])
                ], className="shadow-sm mb-3")
            ], md=4),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_region)])
                ], className="shadow-sm mb-3")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_productos)])
                ], className="shadow-sm mb-3")
            ], md=6),
        ])
    ], fluid=True)

# ================================
# DASHBOARD COMERCIAL
# ================================

def create_comercial_layout(ventas_filtradas, cartera_filtrada):
    """Crea el layout del Dashboard Comercial con datos filtrados"""
    
    # KPIs comerciales
    ventas_total = ventas_filtradas['subtotal_cop'].sum()
    margen_promedio = ventas_filtradas['margen_pct'].mean()
    ticket_promedio = ventas_filtradas['subtotal_cop'].mean()
    descuento_promedio = ventas_filtradas['descuento_pct'].mean()
    
    # Gráfico: Ventas y margen por categoría
    ventas_categoria = ventas_filtradas.groupby('categoria').agg({
        'subtotal_cop': 'sum',
        'margen_total_cop': 'sum'
    }).reset_index()
    
    fig_ventas_margen = go.Figure()
    fig_ventas_margen.add_trace(go.Bar(
        name='Ventas',
        x=ventas_categoria['categoria'],
        y=ventas_categoria['subtotal_cop']/1e6,
        marker_color=COLORS['primary']
    ))
    fig_ventas_margen.add_trace(go.Bar(
        name='Margen',
        x=ventas_categoria['categoria'],
        y=ventas_categoria['margen_total_cop']/1e6,
        marker_color=COLORS['success']
    ))
    fig_ventas_margen.update_layout(
        title='Ventas vs Margen por Categoría',
        xaxis_title='Categoría',
        yaxis_title='Millones COP',
        barmode='group',
        template='plotly_white'
    )
    
    # Gráfico: Top clientes
    top_clientes = ventas_filtradas.groupby('nombre_cliente')['subtotal_cop'].sum().sort_values(ascending=False).head(15).reset_index()
    
    fig_clientes = px.bar(
        top_clientes,
        x='subtotal_cop',
        y='nombre_cliente',
        orientation='h',
        title='Top 15 Clientes por Ventas',
        labels={'subtotal_cop': 'Ventas (COP)', 'nombre_cliente': 'Cliente'},
        color='subtotal_cop',
        color_continuous_scale='Purples'
    )
    fig_clientes.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
    
    # Gráfico: Performance por ejecutivo
    ejecutivo_perf = ventas_filtradas.groupby('ejecutivo').agg({
        'subtotal_cop': 'sum',
        'margen_total_cop': 'sum',
        'venta_id': 'count'
    }).reset_index()
    ejecutivo_perf.columns = ['Ejecutivo', 'Ventas', 'Margen', 'Num_Ventas']
    ejecutivo_perf['Margen_Pct'] = (ejecutivo_perf['Margen'] / ejecutivo_perf['Ventas'] * 100).round(2)
    ejecutivo_perf = ejecutivo_perf.sort_values('Ventas', ascending=False).head(10)
    
    fig_ejecutivos = go.Figure()
    fig_ejecutivos.add_trace(go.Bar(
        name='Ventas (Millones)',
        x=ejecutivo_perf['Ejecutivo'],
        y=ejecutivo_perf['Ventas']/1e6,
        marker_color=COLORS['info']
    ))
    fig_ejecutivos.update_layout(
        title='Top 10 Ejecutivos por Ventas',
        xaxis_title='Ejecutivo',
        yaxis_title='Ventas (Millones COP)',
        template='plotly_white'
    )
    
    # Gráfico: Ventas por segmento
    ventas_segmento = ventas_filtradas.groupby('segmento')['subtotal_cop'].sum().reset_index()
    fig_segmento = px.pie(
        ventas_segmento,
        values='subtotal_cop',
        names='segmento',
        title='Distribución de Ventas por Segmento',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Gráfico: Evolución temporal
    ventas_tiempo = ventas_filtradas.groupby(['mes', 'categoria'])['subtotal_cop'].sum().reset_index()
    fig_tiempo = px.line(
        ventas_tiempo,
        x='mes',
        y='subtotal_cop',
        color='categoria',
        title='Evolución de Ventas por Categoría',
        labels={'subtotal_cop': 'Ventas (COP)', 'mes': 'Mes'}
    )
    fig_tiempo.update_layout(template='plotly_white')
    
    return dbc.Container([
        html.H3("💼 Dashboard Comercial - Ventas, Margen y Clientes", className="mb-4 mt-3"),
        
        # KPIs
        dbc.Row([
            dbc.Col(create_kpi_card("Ventas Totales", format_currency(ventas_total), "💰", COLORS['success']), md=3),
            dbc.Col(create_kpi_card("Margen Promedio", f"{margen_promedio:.1f}%", "📈", COLORS['primary']), md=3),
            dbc.Col(create_kpi_card("Ticket Promedio", format_currency(ticket_promedio), "🎫", COLORS['info']), md=3),
            dbc.Col(create_kpi_card("Descuento Promedio", f"{descuento_promedio:.1f}%", "🏷️", COLORS['warning']), md=3),
        ]),
        
        # Gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_ventas_margen)])
                ], className="shadow-sm mb-3")
            ], md=12),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_tiempo)])
                ], className="shadow-sm mb-3")
            ], md=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_segmento)])
                ], className="shadow-sm mb-3")
            ], md=4),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_clientes)])
                ], className="shadow-sm mb-3")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_ejecutivos)])
                ], className="shadow-sm mb-3")
            ], md=6),
        ])
    ], fluid=True)

# ================================
# DASHBOARD OPERATIVO
# ================================

def create_operativo_layout(ventas_filtradas, cartera_filtrada, inventario_filtrado=None):
    """Crea el layout del Dashboard Operativo con datos filtrados"""
    
    # Usar inventario filtrado o completo
    if inventario_filtrado is None:
        inventario_filtrado = inventario_df
    
    # KPIs operativos
    inventario_actual = inventario_filtrado[inventario_filtrado['fecha_corte'] == inventario_filtrado['fecha_corte'].max()]
    valor_inventario = inventario_actual['valor_inventario_cop'].sum()
    stock_total = inventario_actual['stock_unidades'].sum()
    cartera_total = cartera_filtrada['saldo_cop'].sum()
    morosidad_pct = (cartera_filtrada[cartera_filtrada['dias_mora'] > 0]['saldo_cop'].sum() / cartera_total * 100) if cartera_total > 0 else 0
    
    # Gráfico: Inventario por centro logístico
    inv_centro = inventario_actual.groupby('centro_logistico').agg({
        'valor_inventario_cop': 'sum',
        'stock_unidades': 'sum'
    }).reset_index()
    
    fig_centros = px.bar(
        inv_centro,
        x='centro_logistico',
        y='valor_inventario_cop',
        title='Valor de Inventario por Centro Logístico',
        labels={'valor_inventario_cop': 'Valor (COP)', 'centro_logistico': 'Centro Logístico'},
        color='valor_inventario_cop',
        color_continuous_scale='Teal'
    )
    
    # Gráfico: Inventario por categoría
    inv_categoria = inventario_actual.groupby('categoria')['valor_inventario_cop'].sum().reset_index()
    fig_inv_cat = px.pie(
        inv_categoria,
        values='valor_inventario_cop',
        names='categoria',
        title='Distribución de Inventario por Categoría',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Gráfico: Evolución del inventario
    inv_tiempo = inventario_filtrado.groupby('fecha_corte')['valor_inventario_cop'].sum().reset_index()
    fig_inv_tiempo = px.line(
        inv_tiempo,
        x='fecha_corte',
        y='valor_inventario_cop',
        title='Evolución del Valor de Inventario',
        labels={'valor_inventario_cop': 'Valor (COP)', 'fecha_corte': 'Fecha'},
        markers=True
    )
    fig_inv_tiempo.update_layout(template='plotly_white')
    
    # Gráfico: Estado de cartera
    cartera_estado = cartera_filtrada.groupby('estado')['saldo_cop'].sum().reset_index()
    fig_cartera = px.pie(
        cartera_estado,
        values='saldo_cop',
        names='estado',
        title='Estado de Cartera',
        color_discrete_sequence=['#2ca02c', '#ff7f0e', '#d62728'],
        hole=0.4
    )
    
    # Gráfico: Morosidad por región
    cartera_mora = cartera_filtrada[cartera_filtrada['dias_mora'] > 0].groupby('region')['saldo_cop'].sum().reset_index()
    cartera_mora = cartera_mora.sort_values('saldo_cop', ascending=False)
    
    fig_mora = px.bar(
        cartera_mora,
        x='region',
        y='saldo_cop',
        title='Cartera Vencida por Región',
        labels={'saldo_cop': 'Saldo Vencido (COP)', 'region': 'Región'},
        color='saldo_cop',
        color_continuous_scale='Reds'
    )
    
    # Tabla: Top productos en inventario
    top_inv = inventario_actual.groupby('subcategoria').agg({
        'stock_unidades': 'sum',
        'valor_inventario_cop': 'sum'
    }).sort_values('valor_inventario_cop', ascending=False).head(10).reset_index()
    
    # Gráfico: Días de mora (histograma)
    cartera_con_mora = cartera_filtrada[cartera_filtrada['dias_mora'] > 0]
    fig_dias_mora = px.histogram(
        cartera_con_mora,
        x='dias_mora',
        nbins=20,
        title='Distribución de Días de Morosidad',
        labels={'dias_mora': 'Días de Mora', 'count': 'Número de Documentos'},
        color_discrete_sequence=[COLORS['danger']]
    )
    
    return dbc.Container([
        html.H3("⚙️ Dashboard Operativo - Inventario y Cartera", className="mb-4 mt-3"),
        
        # KPIs
        dbc.Row([
            dbc.Col(create_kpi_card("Valor Inventario", format_currency(valor_inventario), "📦", COLORS['info']), md=3),
            dbc.Col(create_kpi_card("Stock Total", format_number(stock_total) + " unidades", "📊", COLORS['primary']), md=3),
            dbc.Col(create_kpi_card("Cartera Total", format_currency(cartera_total), "💵", COLORS['success']), md=3),
            dbc.Col(create_kpi_card("Morosidad", f"{morosidad_pct:.1f}%", "⚠️", COLORS['danger']), md=3),
        ]),
        
        # Inventario
        html.H5("📦 Análisis de Inventario", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_centros)])
                ], className="shadow-sm mb-3")
            ], md=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_inv_cat)])
                ], className="shadow-sm mb-3")
            ], md=4),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_inv_tiempo)])
                ], className="shadow-sm mb-3")
            ], md=12),
        ]),
        
        # Cartera
        html.H5("💰 Análisis de Cartera", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_cartera)])
                ], className="shadow-sm mb-3")
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_mora)])
                ], className="shadow-sm mb-3")
            ], md=8),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([dcc.Graph(figure=fig_dias_mora)])
                ], className="shadow-sm mb-3")
            ], md=12),
        ])
    ], fluid=True)

# ================================
# LAYOUT PRINCIPAL
# ================================

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("📊 Dashboard Andina - Inteligencia de Negocios", 
                       className="text-center mb-1",
                       style={'color': COLORS['primary'], 'fontWeight': 'bold'}),
                html.P("Análisis integral de ventas, clientes, inventario y cartera",
                      className="text-center text-muted mb-3")
            ], style={'backgroundColor': COLORS['card'], 'padding': '20px', 'borderRadius': '10px',
                     'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginTop': '20px', 'marginBottom': '10px'})
        ])
    ]),
    
    # Filtro de fechas
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    # Título y selector de fechas
                    html.Div([
                        html.Label("📅 Filtro por Rango de Fechas:", 
                                  style={'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                        dcc.DatePickerRange(
                            id='date-filter',
                            start_date=fecha_min_ventas,
                            end_date=fecha_max_ventas,
                            min_date_allowed=fecha_min_ventas,
                            max_date_allowed=fecha_max_ventas,
                            display_format='DD/MM/YYYY',
                            first_day_of_week=1,
                            style={'marginBottom': '15px'}
                        ),
                        html.Span(" (Filtra ventas y cartera)", 
                                 className="text-muted", 
                                 style={'display': 'block', 'fontSize': '0.85rem', 'marginBottom': '15px'})
                    ], style={'textAlign': 'center'}),
                    
                    # Botones de acceso rápido
                    html.Div([
                        html.Label("⚡ Accesos Rápidos:", 
                                  style={'fontWeight': 'bold', 'marginBottom': '8px', 'display': 'block', 'fontSize': '0.9rem'}),
                        dbc.ButtonGroup([
                            dbc.Button("📊 Todos los Datos", id="btn-all", color="primary", outline=True, size="sm"),
                            dbc.Button("📅 Último Año", id="btn-year", color="info", outline=True, size="sm"),
                            dbc.Button("📆 Último Semestre", id="btn-semester", color="info", outline=True, size="sm"),
                            dbc.Button("📋 Último Trimestre", id="btn-quarter", color="info", outline=True, size="sm"),
                            dbc.Button("🗓️ Últimos 6 Meses", id="btn-6months", color="secondary", outline=True, size="sm"),
                            dbc.Button("📌 Últimos 3 Meses", id="btn-3months", color="secondary", outline=True, size="sm"),
                            dbc.Button("📍 Mes Actual", id="btn-month", color="success", outline=True, size="sm"),
                        ], size="sm", style={'flexWrap': 'wrap', 'gap': '5px'})
                    ], style={'textAlign': 'center'})
                ], style={'padding': '20px'})
            ], className="shadow-sm mb-3")
        ])
    ]),
    
    # Filtros adicionales
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Label("🔍 Filtros Adicionales:", 
                                  style={'fontWeight': 'bold', 'marginBottom': '15px', 'display': 'block', 'fontSize': '1rem'}),
                        
                        dbc.Row([
                            # Filtro de Categorías
                            dbc.Col([
                                html.Label("🏷️ Categorías:", style={'fontWeight': '600', 'fontSize': '0.9rem'}),
                                dcc.Dropdown(
                                    id='filter-categorias',
                                    options=[{'label': cat, 'value': cat} for cat in categorias_disponibles],
                                    multi=True,
                                    placeholder="Todas las categorías",
                                    style={'fontSize': '0.85rem'}
                                )
                            ], md=3, className="mb-3"),
                            
                            # Filtro de Regiones
                            dbc.Col([
                                html.Label("🌍 Regiones:", style={'fontWeight': '600', 'fontSize': '0.9rem'}),
                                dcc.Dropdown(
                                    id='filter-regiones',
                                    options=[{'label': reg, 'value': reg} for reg in regiones_disponibles],
                                    multi=True,
                                    placeholder="Todas las regiones",
                                    style={'fontSize': '0.85rem'}
                                )
                            ], md=3, className="mb-3"),
                            
                            # Filtro de Segmentos
                            dbc.Col([
                                html.Label("🎯 Segmentos:", style={'fontWeight': '600', 'fontSize': '0.9rem'}),
                                dcc.Dropdown(
                                    id='filter-segmentos',
                                    options=[{'label': seg, 'value': seg} for seg in segmentos_disponibles],
                                    multi=True,
                                    placeholder="Todos los segmentos",
                                    style={'fontSize': '0.85rem'}
                                )
                            ], md=3, className="mb-3"),
                            
                            # Filtro de Centros Logísticos
                            dbc.Col([
                                html.Label("🏭 Centros Logísticos:", style={'fontWeight': '600', 'fontSize': '0.9rem'}),
                                dcc.Dropdown(
                                    id='filter-centros',
                                    options=[{'label': centro, 'value': centro} for centro in centros_logisticos],
                                    multi=True,
                                    placeholder="Todos los centros",
                                    style={'fontSize': '0.85rem'}
                                )
                            ], md=3, className="mb-3"),
                        ]),
                        
                        # Botón para limpiar filtros
                        html.Div([
                            dbc.Button(
                                "🧹 Limpiar Todos los Filtros",
                                id="btn-clear-filters",
                                color="warning",
                                outline=True,
                                size="sm",
                                className="mt-2"
                            )
                        ], style={'textAlign': 'center'})
                    ])
                ], style={'padding': '20px'})
            ], className="shadow-sm mb-3")
        ])
    ]),
    
    # Tabs
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="📈 Dashboard Gerencial", tab_id="gerencial", 
                       label_style={'fontSize': '1.1rem', 'fontWeight': 'bold'}),
                dbc.Tab(label="💼 Dashboard Comercial", tab_id="comercial",
                       label_style={'fontSize': '1.1rem', 'fontWeight': 'bold'}),
                dbc.Tab(label="⚙️ Dashboard Operativo", tab_id="operativo",
                       label_style={'fontSize': '1.1rem', 'fontWeight': 'bold'}),
            ], id="tabs", active_tab="gerencial", className="mb-3")
        ])
    ]),
    
    # Contenido dinámico
    dbc.Row([
        dbc.Col([
            html.Div(id="tab-content")
        ])
    ])
], fluid=True, style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'paddingBottom': '40px'})

# ================================
# CALLBACKS
# ================================

# Callback para botones de acceso rápido
@app.callback(
    [Output("date-filter", "start_date"),
     Output("date-filter", "end_date")],
    [Input("btn-all", "n_clicks"),
     Input("btn-year", "n_clicks"),
     Input("btn-semester", "n_clicks"),
     Input("btn-quarter", "n_clicks"),
     Input("btn-6months", "n_clicks"),
     Input("btn-3months", "n_clicks"),
     Input("btn-month", "n_clicks")],
    prevent_initial_call=True
)
def update_date_range(btn_all, btn_year, btn_semester, btn_quarter, btn_6m, btn_3m, btn_month):
    """Actualiza el rango de fechas según el botón presionado"""
    from dash import callback_context
    from datetime import timedelta
    from dateutil.relativedelta import relativedelta
    
    # Identificar qué botón fue presionado
    if not callback_context.triggered:
        return fecha_min_ventas, fecha_max_ventas
    
    button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    # Calcular el rango según el botón
    end_date = fecha_max_ventas
    
    if button_id == "btn-all":
        # Todos los datos
        start_date = fecha_min_ventas
    elif button_id == "btn-year":
        # Último año
        start_date = end_date - relativedelta(years=1)
    elif button_id == "btn-semester":
        # Último semestre (6 meses)
        start_date = end_date - relativedelta(months=6)
    elif button_id == "btn-quarter":
        # Último trimestre (3 meses)
        start_date = end_date - relativedelta(months=3)
    elif button_id == "btn-6months":
        # Últimos 6 meses
        start_date = end_date - relativedelta(months=6)
    elif button_id == "btn-3months":
        # Últimos 3 meses
        start_date = end_date - relativedelta(months=3)
    elif button_id == "btn-month":
        # Mes actual (último mes completo)
        start_date = end_date - relativedelta(months=1)
    else:
        start_date = fecha_min_ventas
    
    # Asegurar que no sea anterior a la fecha mínima
    if start_date < fecha_min_ventas:
        start_date = fecha_min_ventas
    
    return start_date, end_date


# Callback para limpiar todos los filtros
@app.callback(
    [Output("filter-categorias", "value"),
     Output("filter-regiones", "value"),
     Output("filter-segmentos", "value"),
     Output("filter-centros", "value")],
    Input("btn-clear-filters", "n_clicks"),
    prevent_initial_call=True
)
def clear_filters(n_clicks):
    """​Limpia todos los filtros adicionales"""
    return None, None, None, None


@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"),
     Input("date-filter", "start_date"),
     Input("date-filter", "end_date"),
     Input("filter-categorias", "value"),
     Input("filter-regiones", "value"),
     Input("filter-segmentos", "value"),
     Input("filter-centros", "value")]
)
def render_tab_content(active_tab, start_date, end_date, categorias, regiones, segmentos, centros):
    """​Renderiza el contenido según la pestaña activa y todos los filtros"""
    
    # Filtrar datos por rango de fechas
    if start_date and end_date:
        ventas_filtradas = ventas_df[(ventas_df['fecha'] >= start_date) & (ventas_df['fecha'] <= end_date)]
        cartera_filtrada = cartera_df[(cartera_df['fecha_factura'] >= start_date) & (cartera_df['fecha_factura'] <= end_date)]
    else:
        ventas_filtradas = ventas_df.copy()
        cartera_filtrada = cartera_df.copy()
    
    # Aplicar filtros adicionales a ventas
    if categorias:
        ventas_filtradas = ventas_filtradas[ventas_filtradas['categoria'].isin(categorias)]
    if regiones:
        ventas_filtradas = ventas_filtradas[ventas_filtradas['region'].isin(regiones)]
        cartera_filtrada = cartera_filtrada[cartera_filtrada['region'].isin(regiones)]
    if segmentos:
        ventas_filtradas = ventas_filtradas[ventas_filtradas['segmento'].isin(segmentos)]
    
    # Filtrar inventario por centro logístico
    if centros:
        inventario_filtrado = inventario_df[inventario_df['centro_logistico'].isin(centros)]
    else:
        inventario_filtrado = inventario_df.copy()
    
    # Aplicar filtro de categorías al inventario también
    if categorias:
        inventario_filtrado = inventario_filtrado[inventario_filtrado['categoria'].isin(categorias)]
    
    # Renderizar vista correspondiente con datos filtrados
    if active_tab == "gerencial":
        return create_gerencial_layout(ventas_filtradas, cartera_filtrada)
    elif active_tab == "comercial":
        return create_comercial_layout(ventas_filtradas, cartera_filtrada)
    elif active_tab == "operativo":
        # Pasar inventario filtrado a la vista operativa
        return create_operativo_layout(ventas_filtradas, cartera_filtrada, inventario_filtrado)
    return html.Div("Seleccione una pestaña")

# ================================
# EJECUTAR APP
# ================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Dashboard iniciado correctamente")
    print("="*60)
    print("📱 Accede al dashboard en: http://127.0.0.1:8050/")
    print("💡 Presiona Ctrl+C para detener el servidor")
    print("="*60 + "\n")
    
    app.run(debug=True, port=8050)

