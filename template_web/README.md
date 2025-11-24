# Web Template - FastAPI + Jinja2

Generic template for web applications with FastAPI and server-side rendering using Jinja2.

## Features

- ✅ FastAPI + Jinja2 for server-side rendering
- ✅ Cookie-based authentication
- ✅ Reusable base templates (layout, datatable, log, detail)
- ✅ Jinja2 macros for common components
- ✅ DataTables with server-side processing
- ✅ Global loader system
- ✅ Static files (CSS, JS, images)
- ✅ HTML forms with validation
- ✅ User sessions
- ✅ MVC architecture
- ✅ Docker ready

## Structure

```
template_web/
├── main.py              # Entry point
├── requirements.txt
├── .env.example
├── config/             # Configuration
├── controller/         # Business logic
├── dependencies/       # Auth and utilities
├── exception/          # Error handlers
├── router/             # Routes
├── schema/             # Schemas
├── static/             # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── lib/           # Libraries (jQuery, Bootstrap, DataTables, etc.)
└── templates/          # Jinja2 templates
    ├── Shared/         # Base templates and reusable components
    │   ├── layout.html.jinja           # Main layout
    │   ├── datatable_base.html.jinja   # Base for server-side tables
    │   ├── bitacora_base.html.jinja    # Base for logs with filters
    │   ├── detail_base.html.jinja      # Base for detail pages
    │   ├── macros.html.jinja           # Reusable macros
    │   └── loader.html.jinja           # Loader component
    ├── Home/           # Home templates
    │   └── index.html.jinja
    ├── Autentica/      # Authentication templates
    │   └── index.html.jinja
    ├── Mantenedor/     # Maintainer templates (CRUD)
    │   └── ejemplo_datatable.html.jinja
    └── Bitacora/       # Log templates
        ├── ejemplo_bitacora.html.jinja
        └── ejemplo_bitacora_detalle.html.jinja
```

## Installation

```bash
py -3.12 -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Install repositorio_lib (required dependency)
pip install -e ../repositorio_lib

# Configure environment variables (in repositorio_lib, NOT here)
cd ../repositorio_lib/config
cp .env.example .env
# Edit .env with DB, JWT, SMTP, etc.
cd ../../template_web

uvicorn main:app --port 8000 --reload
```

**⚠️ IMPORTANT:** Environment variables are configured in `repositorio_lib/config/.env`

## Usage

### 1. Base Templates

The template includes several base files for different page types:

#### Main Layout (`Shared/layout.html.jinja`)

Base layout with navbar, footer, and global components:

```jinja
{% extends "Shared/layout.html.jinja" %}

{% block content %}
<h1>My Content</h1>
{% endblock %}

{% block scripts %}
<script>
  // Page-specific JavaScript
</script>
{% endblock %}
```

#### DataTable Base (`Shared/datatable_base.html.jinja`)

For CRUD pages with server-side tables:

```jinja
{% extends "Shared/datatable_base.html.jinja" %}

{% block page_title %}Users{% endblock %}
{% block create_button_text %}Create User{% endblock %}
{% block create_button_id %}btnCrear{% endblock %}

{% block datatable_js %}
<script>
  // Use InicializarTablaServerSide helper
  InicializarTablaServerSide("#tabla", {
    url: "/api/usuarios/info",
    columns: [
      { data: "id", title: "ID", name: "id" },
      { data: "nombre", title: "Name", name: "nombre" }
    ]
  });
</script>
{% endblock %}
```

See complete example in: `templates/Mantenedor/ejemplo_datatable.html.jinja`

#### Log Base (`Shared/bitacora_base.html.jinja`)

For logs with custom filters:

```jinja
{% extends "Shared/bitacora_base.html.jinja" %}

{% block page_title %}My Log{% endblock %}

{% block filtros %}
<!-- Your custom filters here -->
{% endblock %}

{% block datatable_js %}
<script>
  // Table logic with filters
</script>
{% endblock %}
```

See complete example in: `templates/Bitacora/ejemplo_bitacora.html.jinja`

#### Detail Base (`Shared/detail_base.html.jinja`)

For detail pages with readonly fields:

```jinja
{% extends "Shared/detail_base.html.jinja" %}
{% from 'Shared/macros.html.jinja' import detail_field, detail_textarea %}

{% block page_title %}Detail{% endblock %}

{% block detail_content %}
{{ detail_field("id", "ID") }}
{{ detail_textarea("descripcion", "Description", rows=3) }}
{% endblock %}
```

See complete example in: `templates/Bitacora/ejemplo_bitacora_detalle.html.jinja`

### 2. Reusable Macros

The `Shared/macros.html.jinja` file contains macros for common components:

```jinja
{% from 'Shared/macros.html.jinja' import datatable_styles, datatable_scripts, page_header %}

{# Include DataTables styles #}
{% block styles %}
{{ datatable_styles() }}
{% endblock %}

{# Header with create button #}
{{ page_header(title="My Page", create_button_text="Create", create_button_id="btnCrear") }}

{# DataTables scripts #}
{{ datatable_scripts() }}
```

**Available macros:**
- `datatable_styles()` - DataTables CSS styles
- `datatable_scripts()` - DataTables JS scripts
- `page_header(title, create_button_text, create_button_id)` - Page header with button
- `datatable_container(table_id)` - Table container
- `form_input(field_id, label, value, placeholder, type, readonly)` - Form input
- `form_select(field_id, label, options, selected_value)` - Select dropdown
- `form_toggle(field_id, label, checked)` - Toggle switch
- `detail_field(field_id, label, col_class)` - Readonly field for details
- `detail_textarea(field_id, label, rows, col_class)` - Readonly textarea
- `alert(type, message, dismissible)` - Alert message
- `badge(text, type)` - Badge component
- `icon(name, size, color)` - FontAwesome icon

### 3. DataTables with Server-Side Processing

The project includes a JavaScript helper (`static/js/datatable-serverside.js`) to facilitate configuration:

```javascript
// Initialize server-side table
InicializarTablaServerSide("#tabla", {
  url: "/api/datos",
  columns: [
    { data: "id", title: "ID", name: "id" },
    { data: "nombre", title: "Name", name: "nombre" }
  ],
  defaultOrder: [[0, 'desc']],
  pageLength: 25
});

// Reload table
RecargarTablaServerSide("#tabla");

// Reset table
ReiniciarDataTable("#tabla");
```

**Available helper functions:**
- `RenderizarEstado(activo)` - Status badge (Active/Inactive)
- `RenderizarBotonVer(funcion, parametro)` - "View" button
- `RenderizarBotonEditar(funcion, row)` - "Edit" button
- `RenderizarBotonToggle(funcion, row, activo)` - Toggle status button
- `RenderizarBotonReiniciarClave(funcion, row)` - Reset password button
- `FormatearFechaHora(fecha)` - Format date/time
- `TruncarTexto(texto, maxLength)` - Truncate long text

### 4. Loader System

The global loader is included in the layout and can be used on any page:

```javascript
// Show loader
Loader.show('Loading data...');

// Hide loader
Loader.hide();

// Auto-loader in forms (add class)
<form class="auto-loader" data-loader-text="Processing...">
```

### 5. Create New Page

**1. HTML Template** (`templates/MyModule/my_page.html.jinja`):
```jinja
{% extends "Shared/layout.html.jinja" %}

{% block content %}
<h1>My Page</h1>
{% endblock %}

{% block scripts %}
<script>
  // Specific JavaScript
</script>
{% endblock %}
```

**2. Router** (`router/v1Router.py`):
```python
@router.get("/my-page")
async def my_page(
    request: Request,
    user: dict = Depends(get_current_user_cookie)
):
    return templates.TemplateResponse(
        "MyModule/my_page.html.jinja",
        {
            "request": request,
            "title": "My Page",
            "user_name": user.get("nombre_completo"),
            "user_profile": user.get("perfil")
        }
    )
```

### 6. Forms with Validation

```jinja
{% from 'Shared/macros.html.jinja' import form_input, form_select, form_toggle %}

<div class="row">
  {{ form_input("nombre", "Name", value="", placeholder="Enter name") }}
  {{ form_select("perfil", "Profile", options=perfiles_data, selected_value=1) }}
  {{ form_toggle("activo", "Active", checked=True) }}
</div>
```

**JavaScript validation:**
```javascript
// Validate generic field
await ValidarCampoGenerico(element, errorElement, {
  tipo: "email", // null for generic text
  mensajeError: "This field is required"
});

// Clear field errors
LimpiarErroresCampos(["nombre", "email"]);
```

### 7. Authentication

```python
# Protect route with cookie auth
@router.get("/dashboard")
async def dashboard(
    request: Request,
    user: dict = Depends(get_current_user_cookie)
):
    return templates.TemplateResponse(
        "Home/index.html.jinja",
        {
            "request": request,
            "user_name": user.get("nombre_completo"),
            "user_profile": user.get("perfil")
        }
    )
```

### 8. SweetAlert Messages

```javascript
// Temporary success
MostrarExitoTemporal("Operation successful");

// Error
MostrarError("Error", "Error message");

// Confirmation
MostrarConfirmacion("Confirm?", "Message", "Yes, confirm").then((result) => {
  if (result.isConfirmed) {
    // Confirmed action
  }
});

// Download format selector
MostrarSelectorFormatoDescarga().then((result) => {
  if (result.isConfirmed) {
    const formato = result.value; // 'xlsx', 'csv', 'pdf'
  }
});
```

## Included Examples

The template includes complete usage examples:

1. **Login**: `templates/Autentica/index.html.jinja`
2. **Home**: `templates/Home/index.html.jinja`
3. **DataTable CRUD**: `templates/Mantenedor/ejemplo_datatable.html.jinja`
4. **Log with Filters**: `templates/Bitacora/ejemplo_bitacora.html.jinja`
5. **Detail Page**: `templates/Bitacora/ejemplo_bitacora_detalle.html.jinja`

## Docker

```bash
docker build -t web-template .

# Environment variables from repositorio_lib
docker run -p 8000:8000 \
  -v $(pwd)/../repositorio_lib:/app/repositorio_lib \
  --env-file ../repositorio_lib/config/.env \
  web-template
```

**Note:** The `.env` file must be in `../repositorio_lib/config/.env`

## Important Notes

1. **Environment variables**: Configure ONLY in `repositorio_lib/config/.env` (DO NOT create .env in this template)
2. **File extension**: Use `.html.jinja` for templates
3. **Server-side processing**: For large tables, use server-side processing
4. **JavaScript helpers**: Review `/static/js/datatable-serverside.js` and `/static/js/site.js` for available functions
5. **Macros**: Import only the macros you need for better performance
6. **Loader**: The global loader activates automatically on link navigation and forms with the `auto-loader` class

## Centralized Configuration

```python
# Import configuration from repositorio_lib
from repositorio_lib.config.settings import db_settings, jwt_settings, app_settings

# Use in code
db_url = db_settings.get_connection_string(async_mode=True)
secret_key = jwt_settings.SECRET_KEY
log_dir = app_settings.get_log_dir()
```

## License

Free code template for use in Python projects
