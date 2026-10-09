# ======================================================================
# QuetzalMart · RPA · Crear tablas centralizadas (ejecutar UNA vez)
# Crea dentro de la MISMA base de datos de Odoo (PostgreSQL):
#   x_rpa_cliente  -> filas de las hojas "clientes"
#   x_rpa_producto -> filas de las hojas "productos"
# y el menú "Cargas RPA" para verlas desde Odoo.
# Si lo ejecutas otra vez no duplica nada.
# ======================================================================
TABLAS = [
    ('x_rpa_cliente', 'Carga RPA - Clientes', 'Clientes cargados', [
        ('x_name', 'Name', 'char'), ('x_company_type', 'Company Type', 'char'),
        ('x_related_company', 'Related Company', 'char'), ('x_email', 'Email', 'char'),
        ('x_phone', 'Phone', 'char'), ('x_street', 'Street', 'char'), ('x_street2', 'Street2', 'char'),
        ('x_city', 'City', 'char'), ('x_state', 'State', 'char'), ('x_zip', 'Zip', 'char'),
        ('x_country', 'Country', 'char'), ('x_tax_id', 'Tax ID', 'char'), ('x_website', 'Website', 'char'),
        ('x_tags', 'Tags', 'char'), ('x_reference', 'Reference', 'char'), ('x_notes', 'Notes', 'text'),
    ]),
    ('x_rpa_producto', 'Carga RPA - Productos', 'Productos cargados', [
        ('x_id_externo', 'ID Externo', 'char'), ('x_name', 'Name', 'char'),
        ('x_product_type', 'Product Type', 'char'), ('x_internal_reference', 'Internal Reference', 'char'),
        ('x_barcode', 'Barcode', 'char'), ('x_sales_price', 'Sales Price', 'char'), ('x_cost', 'Cost', 'char'),
        ('x_weight', 'Weight', 'char'), ('x_sales_description', 'Sales Description', 'text'),
        ('x_product_values', 'Product Values', 'text'), ('x_cantidad_a_la_mano', 'Cantidad a la mano', 'char'),
        ('x_esta_publicado', 'Está publicado', 'char'),
    ]),
]
CONTROL = [
    ('x_archivo_origen', 'Archivo origen', 'char'), ('x_lote', 'Lote del robot', 'char'),
    ('x_estado', 'Estado', 'char'), ('x_mensaje', 'Mensaje', 'text'),
    ('x_registro_odoo', 'ID creado en Odoo', 'integer'),
]
version = env['ir.module.module'].search([('name', '=', 'base')], limit=1).latest_version or ''
tipo_lista = 'tree' if version.startswith('17') else 'list'
menu_raiz = env['ir.ui.menu'].search([('name', '=', 'Cargas RPA'), ('parent_id', '=', False)], limit=1)
if not menu_raiz:
    menu_raiz = env['ir.ui.menu'].create({'name': 'Cargas RPA', 'sequence': 90})
grupo_interno = env.ref('base.group_user')
orden = 10
primera_accion = False
for tecnico, descripcion, nombre_menu, campos in TABLAS:
    modelo = env['ir.model'].search([('model', '=', tecnico)], limit=1)
    if not modelo:
        modelo = env['ir.model'].create({'name': descripcion, 'model': tecnico, 'state': 'manual', 'order': 'id desc'})
    for nombre, etiqueta, tipo in campos + CONTROL:
        campo = env['ir.model.fields'].search([('model_id', '=', modelo.id), ('name', '=', nombre)], limit=1)
        if not campo:
            env['ir.model.fields'].create({'model_id': modelo.id, 'name': nombre, 'field_description': etiqueta,
                                           'ttype': tipo, 'state': 'manual'})
        elif campo.field_description != etiqueta:
            campo.write({'field_description': etiqueta})
    if not env['ir.model.access'].search_count([('model_id', '=', modelo.id)]):
        env['ir.model.access'].create({'name': tecnico + '_usuarios', 'model_id': modelo.id,
                                       'group_id': grupo_interno.id, 'perm_read': True, 'perm_write': True,
                                       'perm_create': True, 'perm_unlink': True})
    columnas = ''.join(['<field name="%s" optional="show"/>' % c[0] for c in campos])
    arquitectura = ('<%s create="false" default_order="id desc">'
                    '<field name="create_date" string="Cargado el"/>'
                    '<field name="x_lote"/><field name="x_archivo_origen"/>%s'
                    '<field name="x_estado" decoration-success="x_estado == \'Procesado\'" '
                    'decoration-danger="x_estado == \'Error\'" decoration-warning="x_estado == \'Pendiente\'"/>'
                    '<field name="x_mensaje"/><field name="x_registro_odoo"/></%s>') % (tipo_lista, columnas, tipo_lista)
    vista = env['ir.ui.view'].search([('model', '=', tecnico), ('type', '=', tipo_lista)], limit=1)
    if vista:
        vista.write({'arch': arquitectura})
    else:
        env['ir.ui.view'].create({'name': tecnico + '.lista', 'model': tecnico, 'type': tipo_lista, 'arch': arquitectura})
    accion = env['ir.actions.act_window'].search([('res_model', '=', tecnico)], limit=1)
    if not accion:
        accion = env['ir.actions.act_window'].create({'name': nombre_menu, 'res_model': tecnico,
                                                      'view_mode': tipo_lista + ',form'})
    if not env['ir.ui.menu'].search_count([('action', '=', 'ir.actions.act_window,%d' % accion.id)]):
        env['ir.ui.menu'].create({'name': nombre_menu, 'parent_id': menu_raiz.id,
                                  'action': 'ir.actions.act_window,%d' % accion.id, 'sequence': orden})
    primera_accion = primera_accion or accion
    orden += 10
# El menú principal necesita una acción para salir en la cuadrícula de apps
if primera_accion:
    menu_raiz.write({'action': 'ir.actions.act_window,%d' % primera_accion.id, 'web_icon': 'base,static/description/icon.png'})
log('Tablas del RPA listas: x_rpa_cliente y x_rpa_producto')
