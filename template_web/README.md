# Web Template - FastAPI + Jinja2

Plantilla genérica para aplicaciones web con FastAPI y renderizado server-side usando Jinja2.

## Características

- ✅ FastAPI + Jinja2 para renderizado server-side
- ✅ Autenticación basada en cookies
- ✅ Templates base reutilizables (layout, datatable, bitacora, detail)
- ✅ Macros Jinja2 para componentes comunes
- ✅ DataTables con server-side processing
- ✅ Sistema de loader global
- ✅ Archivos estáticos (CSS, JS, imágenes)
- ✅ Formularios HTML con validación
- ✅ Sesiones de usuario
- ✅ Arquitectura MVC
- ✅ Docker ready

## Estructura

```
template_web/
├── main.py              # Entry point
├── requirements.txt
├── .env.example
├── config/             # Configuración
├── controller/         # Lógica de negocio
├── dependencies/       # Auth y utilidades
├── exception/          # Manejadores de errores
├── router/             # Rutas
├── schema/             # Schemas
├── static/             # CSS, JS, imágenes
│   ├── css/
│   ├── js/
│   └── lib/           # Bibliotecas (jQuery, Bootstrap, DataTables, etc.)
└── templates/          # Templates Jinja2
    ├── Shared/         # Templates base y componentes reutilizables
    │   ├── layout.html.jinja           # Layout principal
    │   ├── datatable_base.html.jinja   # Base para tablas server-side
    │   ├── bitacora_base.html.jinja    # Base para bitácoras con filtros
    │   ├── detail_base.html.jinja      # Base para páginas de detalle
    │   ├── macros.html.jinja           # Macros reutilizables
    │   └── loader.html.jinja           # Componente de loader
    ├── Home/           # Templates de inicio
    │   └── index.html.jinja
    ├── Autentica/      # Templates de autenticación
    │   └── index.html.jinja
    ├── Mantenedor/     # Templates de mantenedores (CRUD)
    │   └── ejemplo_datatable.html.jinja
    └── Bitacora/       # Templates de bitácoras
        ├── ejemplo_bitacora.html.jinja
        └── ejemplo_bitacora_detalle.html.jinja
```

## Instalación

```bash
py -3.12 -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --port 8000 --reload
```

## Uso

### 1. Templates Base

El template incluye varios archivos base para diferentes tipos de páginas:

#### Layout Principal (`Shared/layout.html.jinja`)

Layout base con navbar, footer y componentes globales:

```jinja
{% extends "Shared/layout.html.jinja" %}

{% block content %}
<h1>Mi Contenido</h1>
{% endblock %}

{% block scripts %}
<script>
  // JavaScript específico de la página
</script>
{% endblock %}
```

#### DataTable Base (`Shared/datatable_base.html.jinja`)

Para páginas CRUD con tablas server-side:

```jinja
{% extends "Shared/datatable_base.html.jinja" %}

{% block page_title %}Usuarios{% endblock %}
{% block create_button_text %}Crear Usuario{% endblock %}
{% block create_button_id %}btnCrear{% endblock %}

{% block datatable_js %}
<script>
  // Usar helper InicializarTablaServerSide
  InicializarTablaServerSide("#tabla", {
    url: "/api/usuarios/info",
    columns: [
      { data: "id", title: "ID", name: "id" },
      { data: "nombre", title: "Nombre", name: "nombre" }
    ]
  });
</script>
{% endblock %}
```

Ver ejemplo completo en: `templates/Mantenedor/ejemplo_datatable.html.jinja`

#### Bitácora Base (`Shared/bitacora_base.html.jinja`)

Para bitácoras con filtros personalizados:

```jinja
{% extends "Shared/bitacora_base.html.jinja" %}

{% block page_title %}Mi Bitácora{% endblock %}

{% block filtros %}
<!-- Tus filtros personalizados aquí -->
{% endblock %}

{% block datatable_js %}
<script>
  // Lógica de la tabla con filtros
</script>
{% endblock %}
```

Ver ejemplo completo en: `templates/Bitacora/ejemplo_bitacora.html.jinja`

#### Detail Base (`Shared/detail_base.html.jinja`)

Para páginas de detalle con campos readonly:

```jinja
{% extends "Shared/detail_base.html.jinja" %}
{% from 'Shared/macros.html.jinja' import detail_field, detail_textarea %}

{% block page_title %}Detalle{% endblock %}

{% block detail_content %}
{{ detail_field("id", "ID") }}
{{ detail_textarea("descripcion", "Descripción", rows=3) }}
{% endblock %}
```

Ver ejemplo completo en: `templates/Bitacora/ejemplo_bitacora_detalle.html.jinja`

### 2. Macros Reutilizables

El archivo `Shared/macros.html.jinja` contiene macros para componentes comunes:

```jinja
{% from 'Shared/macros.html.jinja' import datatable_styles, datatable_scripts, page_header %}

{# Incluir estilos de DataTables #}
{% block styles %}
{{ datatable_styles() }}
{% endblock %}

{# Header con botón de crear #}
{{ page_header(title="Mi Página", create_button_text="Crear", create_button_id="btnCrear") }}

{# Scripts de DataTables #}
{{ datatable_scripts() }}
```

**Macros disponibles:**
- `datatable_styles()` - Estilos CSS de DataTables
- `datatable_scripts()` - Scripts JS de DataTables
- `page_header(title, create_button_text, create_button_id)` - Header de página con botón
- `datatable_container(table_id)` - Container para tabla
- `form_input(field_id, label, value, placeholder, type, readonly)` - Input de formulario
- `form_select(field_id, label, options, selected_value)` - Select dropdown
- `form_toggle(field_id, label, checked)` - Toggle switch
- `detail_field(field_id, label, col_class)` - Campo readonly para detalles
- `detail_textarea(field_id, label, rows, col_class)` - Textarea readonly
- `alert(type, message, dismissible)` - Alert message
- `badge(text, type)` - Badge component
- `icon(name, size, color)` - Icono FontAwesome

### 3. DataTables con Server-Side Processing

El proyecto incluye un helper JavaScript (`static/js/datatable-serverside.js`) para facilitar la configuración:

```javascript
// Inicializar tabla server-side
InicializarTablaServerSide("#tabla", {
  url: "/api/datos",
  columns: [
    { data: "id", title: "ID", name: "id" },
    { data: "nombre", title: "Nombre", name: "nombre" }
  ],
  defaultOrder: [[0, 'desc']],
  pageLength: 25
});

// Recargar tabla
RecargarTablaServerSide("#tabla");

// Reiniciar tabla
ReiniciarDataTable("#tabla");
```

**Funciones auxiliares disponibles:**
- `RenderizarEstado(activo)` - Badge de estado (Activo/Inactivo)
- `RenderizarBotonVer(funcion, parametro)` - Botón "Ver"
- `RenderizarBotonEditar(funcion, row)` - Botón "Editar"
- `RenderizarBotonToggle(funcion, row, activo)` - Botón toggle estado
- `RenderizarBotonReiniciarClave(funcion, row)` - Botón reiniciar clave
- `FormatearFechaHora(fecha)` - Formatear fecha/hora
- `TruncarTexto(texto, maxLength)` - Truncar texto largo

### 4. Sistema de Loader

El loader global está incluido en el layout y se puede usar en cualquier página:

```javascript
// Mostrar loader
Loader.show('Cargando datos...');

// Ocultar loader
Loader.hide();

// Auto-loader en formularios (agregar clase)
<form class="auto-loader" data-loader-text="Procesando...">
```

### 5. Crear Nueva Página

**1. Template HTML** (`templates/MiModulo/mi_pagina.html.jinja`):
```jinja
{% extends "Shared/layout.html.jinja" %}

{% block content %}
<h1>Mi Página</h1>
{% endblock %}

{% block scripts %}
<script>
  // JavaScript específico
</script>
{% endblock %}
```

**2. Router** (`router/v1Router.py`):
```python
@router.get("/mi-pagina")
async def mi_pagina(
    request: Request,
    user: dict = Depends(get_current_user_cookie)
):
    return templates.TemplateResponse(
        "MiModulo/mi_pagina.html.jinja",
        {
            "request": request,
            "title": "Mi Página",
            "user_name": user.get("nombre_completo"),
            "user_profile": user.get("perfil")
        }
    )
```

### 6. Formularios con Validación

```jinja
{% from 'Shared/macros.html.jinja' import form_input, form_select, form_toggle %}

<div class="row">
  {{ form_input("nombre", "Nombre", value="", placeholder="Ingrese nombre") }}
  {{ form_select("perfil", "Perfil", options=perfiles_data, selected_value=1) }}
  {{ form_toggle("activo", "Activo", checked=True) }}
</div>
```

**Validación JavaScript:**
```javascript
// Validar campo genérico
await ValidarCampoGenerico(element, errorElement, {
  tipo: "email", // null para texto genérico
  mensajeError: "Este campo es obligatorio"
});

// Limpiar errores
LimpiarErroresCampos(["nombre", "email"]);
```

### 7. Autenticación

```python
# Proteger ruta con cookie auth
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

### 8. Mensajes SweetAlert

```javascript
// Éxito temporal
MostrarExitoTemporal("Operación exitosa");

// Error
MostrarError("Error", "Mensaje de error");

// Confirmación
MostrarConfirmacion("¿Confirmar?", "Mensaje", "Sí, confirmar").then((result) => {
  if (result.isConfirmed) {
    // Acción confirmada
  }
});

// Selector de formato de descarga
MostrarSelectorFormatoDescarga().then((result) => {
  if (result.isConfirmed) {
    const formato = result.value; // 'xlsx', 'csv', 'pdf'
  }
});
```

## Ejemplos Incluidos

El template incluye ejemplos completos de uso:

1. **Login**: `templates/Autentica/index.html.jinja`
2. **Home**: `templates/Home/index.html.jinja`
3. **DataTable CRUD**: `templates/Mantenedor/ejemplo_datatable.html.jinja`
4. **Bitácora con Filtros**: `templates/Bitacora/ejemplo_bitacora.html.jinja`
5. **Página de Detalle**: `templates/Bitacora/ejemplo_bitacora_detalle.html.jinja`

## Docker

```bash
docker build -t web-template .
docker run -p 8000:8000 --env-file .env web-template
```

## Notas Importantes

1. **Extensión de archivos**: Usar `.html.jinja` para templates
2. **Server-side processing**: Para tablas grandes, usar server-side processing
3. **Helpers JavaScript**: Revisar `/static/js/datatable-serverside.js` y `/static/js/site.js` para funciones disponibles
4. **Macros**: Importar solo los macros que necesites para mejor rendimiento
5. **Loader**: El loader global se activa automáticamente en navegación de links y formularios con clase `auto-loader`

## Licencia

Plantilla de código libre para uso en proyectos Python
