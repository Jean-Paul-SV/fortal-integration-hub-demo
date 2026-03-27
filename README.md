# Construction Operations Odoo

Repositorio publico del addon `construction-operations-odoo`, orientado a la administracion de obras, contratistas y actas de contratista en operaciones de construccion. El paquete concentra catalogos operativos, flujo de aprobacion, auditoria funcional, importacion masiva por CSV y control de acceso por roles.

## Resumen Ejecutivo

La solucion cubre un frente operativo frecuente en empresas del sector construccion:

- catalogo de obras
- catalogo de contratistas
- actas de contratista con flujo de revision y aprobacion
- auditoria funcional sobre decisiones y responsables
- importacion masiva de novedades por CSV
- seguridad segmentada por perfiles

La implementacion esta desarrollada con Odoo ORM, vistas XML y reglas de acceso nativas, sin depender de Odoo Studio ni de addons genericos de terceros.

## Capacidades Principales

- modelado de datos para obras, contratistas, actas y lineas
- flujo de estados `draft`, `sent`, `approved` y `rejected`
- validaciones de negocio sobre valores y aprobaciones
- registro de usuario aprobador, fecha y trazabilidad funcional
- asistente transitorio para importacion agrupada desde CSV
- seguridad por grupos para Direccion, Contabilidad y Supervisor
- pruebas automatizadas del flujo base

## Alcance Funcional

1. Administracion de obras con supervisor responsable.
2. Administracion de contratistas vinculados a la operacion.
3. Registro de actas con conceptos, subtotales y total consolidado.
4. Envio de actas para revision operativa.
5. Aprobacion o rechazo por usuarios autorizados.
6. Importacion de lineas desde CSV con agrupacion por obra, contratista y fecha.
7. Restricciones de visibilidad y permisos por rol.

## Documentacion

La evidencia funcional consolidada se entrega en:

- `docs/construction-operations-odoo-dossier.pdf`

## Estructura del Repositorio

- `models/`: modelos de negocio.
- `views/`: formularios, listas, menus y acciones.
- `wizard/`: asistente de importacion CSV.
- `security/`: grupos, reglas y accesos.
- `tests/`: pruebas automatizadas del flujo principal.
- `data/`: secuencias y datos tecnicos.
- `demo/`: archivo CSV de referencia para carga inicial.
- `docs/`: dossier PDF y capturas funcionales.

## Requisitos

1. Odoo 16 Community o Enterprise.
2. Modulos `base` y `mail`.
3. Python 3.10 o superior en la instalacion de Odoo.

## Compatibilidad

La implementacion utiliza APIs ORM y vistas XML compatibles con Odoo 16. La migracion a Odoo 17 requiere, en condiciones normales, ajuste de version en `__manifest__.py` y validacion puntual de vistas en el entorno destino.

## Instalacion

El identificador tecnico del addon es `construction_operations_odoo`.

1. Copiar la carpeta `construction_operations_odoo` a una ruta incluida en `addons_path`.
2. Reiniciar Odoo.
3. Actualizar la lista de aplicaciones.
4. Instalar o actualizar el modulo desde Apps o por linea de comandos.

### Ejemplo local

```bash
odoo-bin -d construction_operations_db -r odoo -w odoo --addons-path="addons,custom_addons" -u construction_operations_odoo
```

### Ejemplo en Windows

```powershell
python .\odoo-bin -d construction_operations_db --addons-path="C:\odoo\addons,C:\Users\paulk" -u construction_operations_odoo
```

### Ejemplo con Docker

```bash
docker run --name construction-odoo16 -p 8069:8069 ^
  -v C:\Users\paulk:/mnt/extra-addons ^
  -e HOST=host.docker.internal ^
  -e USER=odoo ^
  -e PASSWORD=odoo ^
  odoo:16
```

Luego actualizar el modulo:

```bash
docker exec -it construction-odoo16 odoo -d construction_operations_db -u construction_operations_odoo --stop-after-init
```

## Flujo Funcional

1. Configurar usuarios en los grupos Direccion, Contabilidad y Supervisor.
2. Crear una obra y asignar supervisor responsable.
3. Registrar un contratista.
4. Crear un acta con una o varias lineas.
5. Enviar el acta a revision.
6. Aprobar o rechazar con un usuario autorizado.
7. Revisar la trazabilidad funcional para validar responsable y fecha.

## Importacion CSV

Ir a `Construction Operations > Operaciones > Importar actas CSV` y cargar `demo/actas_import_example.csv`.

### Columnas obligatorias

- `obra`
- `contratista`
- `fecha`
- `concepto`
- `valor`

### Reglas de carga

- Cada fila genera una linea de acta.
- Si dos filas comparten obra, contratista y fecha, se consolidan en la misma acta en borrador.
- Si `valor` es menor o igual a cero, la importacion se rechaza.
- Si faltan columnas obligatorias, la importacion se rechaza.

## Pruebas

Para ejecutar las pruebas del modulo:

```bash
odoo-bin -d construction_operations_test --test-enable --stop-after-init -i construction_operations_odoo
```

Casos cubiertos:

- auditoria al aprobar un acta
- bloqueo de aprobacion cuando el total es cero
- agrupacion correcta del CSV en una sola acta con varias lineas

## Nota Importante

Las capturas y el dossier incluidos corresponden a un entorno funcional controlado. Se presentan como evidencia tecnica y operativa del modulo y de la configuracion contable utilizada para la documentacion.
