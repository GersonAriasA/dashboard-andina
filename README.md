# Dashboard de Inteligencia de Negocios - Andina

Dashboard interactivo desarrollado con Plotly Dash para análisis integral de datos empresariales.

## 🚀 Inicio Rápido

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar el Dashboard

```bash
python dashboard.py
```

El dashboard estará disponible en: **http://127.0.0.1:8050/**

## 📊 Características Principales

### Tres Vistas de Análisis

1. **📈 Dashboard Gerencial** - Visión general del negocio
2. **💼 Dashboard Comercial** - Análisis de ventas, márgenes y clientes
3. **⚙️ Dashboard Operativo** - Gestión de inventario y cartera

### 🎯 Filtros Inteligentes

**Selector de Rango de Fechas**
- Permite seleccionar cualquier rango personalizado
- Formato: DD/MM/YYYY
- Filtra automáticamente ventas y cartera

**⚡ Accesos Rápidos** (Nuevos Botones)
- 📊 **Todos los Datos** - Vista completa (2022-2024)
- 📅 **Último Año** - Últimos 12 meses
- 📆 **Último Semestre** - Últimos 6 meses
- 📋 **Último Trimestre** - Últimos 3 meses
- 🗓️ **Últimos 6 Meses** - Medio año reciente
- 📌 **Últimos 3 Meses** - Trimestre reciente
- 📍 **Mes Actual** - Último mes completo

**¿Cómo usar los botones?**
Simplemente haz clic en cualquier botón y el filtro de fechas se actualizará automáticamente. Todos los gráficos y KPIs se recalcularán con el nuevo rango.

### 🔍 Filtros Adicionales (Multi-Select)

**Ubicación**: Debajo del filtro de fechas

**4 Filtros Dinámicos Disponibles:**

1. **🏷️ Categorías** - Filtra por categoría de producto
   - Afecta: Ventas, Inventario
   - Multi-selección: Puedes seleccionar múltiples categorías

2. **🌍 Regiones** - Filtra por región geográfica
   - Afecta: Ventas, Cartera
   - Regiones: Caribe, Llanos, Santanderes, Pacífico, etc.

3. **🎯 Segmentos** - Filtra por segmento de cliente
   - Afecta: Ventas
   - Segmentos: Cadena de Ferreterías, Comercializadora Local, Constructora, etc.

4. **🏭 Centros Logísticos** - Filtra por ubicación de inventario
   - Afecta: Inventario
   - Centros: Bogotá, Cali, Barranquilla, etc.

**🧹 Botón Limpiar Filtros**
- Ubicación: Debajo de los 4 filtros
- Función: Restablece todos los filtros adicionales a su estado inicial (sin filtros)
- Los filtros de fecha no se ven afectados

**💡 Uso Combinado de Filtros**

Los filtros trabajan en conjunto. Por ejemplo:
- Filtrar por "Último Año" + "Región: Caribe" + "Categoría: Tecnología y Seguridad" mostrará solo las operaciones tecnológicas en la región Caribe del último año
- Los filtros vacíos (sin selección) se consideran como "Todos"
- El filtrado es acumulativo: mientras más filtros apliques, más específicos serán los resultados

## 📂 Estructura de Datos

El dashboard procesa 6 archivos CSV ubicados en la carpeta `tablas/`:

- `ventas_andina.csv` - 6,000 registros de ventas
- `clientes_andina.csv` - 220 clientes
- `inventario_andina.csv` - 4,320 registros de stock
- `cartera_andina.csv` - 2,200 documentos
- `productos_andina.csv` - 160 productos
- `importaciones_andina.csv` - 140 importaciones

**Período de datos**: 2022-01-01 a 2024-12-31

## 🎨 Métricas y Visualizaciones

### Dashboard Gerencial (4 KPIs + 4 Gráficos)
- Ventas totales, Clientes activos, Margen total, Cartera vencida
- Tendencia mensual, Margen por categoría, Distribución regional, Top 10 productos

### Dashboard Comercial (4 KPIs + 5 Gráficos)
- Ventas, Margen promedio, Ticket promedio, Descuento promedio
- Ventas vs Margen, Evolución temporal, Segmentación, Top clientes, Top ejecutivos

### Dashboard Operativo (4 KPIs + 6 Gráficos)
- Valor inventario, Stock total, Cartera total, Morosidad
- Inventario por centro y categoría, Evolución, Estado de cartera, Morosidad regional

## 🛠️ Tecnologías

- **Python 3.x**
- **Pandas** - Análisis de datos
- **Plotly** - Visualizaciones interactivas
- **Dash** - Framework web
- **Dash Bootstrap Components** - UI components
- **python-dateutil** - Cálculo de fechas

## 📝 Archivos Principales

- `dashboard.py` - Aplicación principal (~680 líneas)
- `requirements.txt` - Dependencias del proyecto
- `tablas/` - Directorio con archivos CSV de datos

## 💡 Consejos de Uso

1. **Filtrado rápido**: Usa los botones de acceso rápido para análisis comunes
2. **Filtrado personalizado**: Usa el selector de fechas para rangos específicos
3. **Interactividad**: Los gráficos permiten zoom, pan y hover tooltips
4. **Navegación**: Cambia entre vistas usando las pestañas superiores
5. **Actualización**: Al cambiar filtros, todos los KPIs y gráficos se actualizan automáticamente

## 🔄 Detener el Dashboard

Presiona `Ctrl+C` en la terminal donde se ejecuta el dashboard.

## 📊 Ejemplo de Uso

1. Abre el dashboard en tu navegador
2. Selecciona la vista "Dashboard Comercial"
3. Haz clic en "📅 Último Año" para ver solo datos recientes
4. Analiza las tendencias de ventas y márgenes
5. Identifica los top clientes del período

---

**Desarrollado para Andina** | Dashboard de Inteligencia de Negocios
