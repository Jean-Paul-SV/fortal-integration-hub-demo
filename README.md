# Construction Operations Odoo

Módulo Odoo 16 para la gestión de operaciones de construcción: obras, contratistas, actas y aprobaciones.

## Descripción

Módulo personalizado para empresas del sector construcción que necesitan llevar el control de sus obras, registrar contratistas, gestionar actas de trabajo y manejar flujos de aprobación directamente desde Odoo.

## Compatibilidad

- **Odoo**: 16.0
- **Categoría**: Operaciones / Construcción

## Funcionalidades

- **Obras**: registro y seguimiento de proyectos de construcción
- **Contratistas**: catálogo de proveedores y contratistas por obra
- **Actas**: generación y gestión de actas de trabajo o entrega
- **Aprobaciones**: flujo de aprobación configurable para actas y documentos
- **Importación masiva**: wizard para importar actas desde archivo externo

## Modelos principales

| Modelo | Descripción |
|---|---|
| `obra` | Proyecto de construcción con ubicación, fechas y estado |
| `contratista` | Empresa o persona contratada para una obra |
| `acta` | Documento de registro de trabajo ejecutado |
| Wizard `acta_import` | Importación masiva de actas |

## Instalación

1. Clonar el repositorio dentro de la carpeta de addons de Odoo:

```bash
git clone https://github.com/Jean-Paul-SV/construction-operations-odoo.git addons/construction_operations_odoo
```

2. Reiniciar el servidor Odoo:

```bash
./odoo-bin -u construction_operations_odoo -d nombre_base_de_datos
```

3. Activar el módulo desde **Aplicaciones** en la interfaz de Odoo.

## Estructura del módulo

```
construction_operations_odoo/
├── models/
│   ├── obra.py
│   ├── contratista.py
│   └── acta.py
├── views/
│   ├── obra_views.xml
│   ├── contratista_views.xml
│   ├── acta_views.xml
│   └── menu_views.xml
├── wizard/
│   └── acta_import_wizard.py
├── security/
│   └── ir.model.access.csv
├── __manifest__.py
└── __init__.py
```

## Configuración del módulo

El archivo `__manifest__.py` declara:

```python
{
    "name": "Construction Operations Odoo",
    "version": "16.0.1.0.0",
    "summary": "Modulo Odoo para obras, contratistas, actas y aprobaciones en operaciones de construccion.",
    "category": "Operations",
    "depends": ["base"],
}
```