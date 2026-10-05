# ======================================================================
# QuetzalMart · RPA · Procesar cargas pendientes
# El robot de UiPath inserta filas con Estado = "Pendiente" en
# x_rpa_cliente y x_rpa_producto. Este código convierte cada fila en un
# Contacto o en un Producto (publicado en la tienda y con existencias)
# y deja el resultado en Estado / Mensaje / ID creado en Odoo.
# ======================================================================
# no_vat_validation: guarda el Tax ID tal como viene en el Excel (sin validarlo por país)
Contacto = env['res.partner'].sudo().with_context(no_vat_validation=True)
Pais = env['res.country'].sudo()
Departamento = env['res.country.state'].sudo()
Etiqueta = env['res.partner.category'].sudo()
Plantilla = env['product.template'].sudo()
Variante = env['product.product'].sudo()
DatosXml = env['ir.model.data'].sudo()
Campos = env['ir.model.fields'].sudo()

def texto(valor):
    return (valor or '').strip()

def numero(valor):
    limpio = texto(valor).replace('Q', '').replace('$', '').replace(' ', '')
    if ',' in limpio and '.' in limpio:
        limpio = limpio.replace(',', '')
    else:
        limpio = limpio.replace(',', '.')
    try:
        return float(limpio)
    except Exception:
        return 0.0

def existe_campo(modelo, campo):
    return bool(Campos.search_count([('model', '=', modelo), ('name', '=', campo)]))

tiene_inventario = existe_campo('stock.quant', 'inventory_quantity')
tiene_almacenable = existe_campo('product.template', 'is_storable')
tiene_tienda = existe_campo('product.template', 'is_published')
tiene_desc_web = existe_campo('product.template', 'description_ecommerce')
categoria_web = False
if tiene_tienda:
    categoria_web = env['product.public.category'].sudo().search([('name', '=', 'Cargados por RPA')], limit=1)
    if not categoria_web:
        categoria_web = env['product.public.category'].sudo().create({'name': 'Cargados por RPA'})
ubicacion = False
if tiene_inventario:
    # Almacén de la empresa principal; si no tiene, el primero que exista (ej. el de la sucursal Guatemala)
    almacen = env['stock.warehouse'].sudo().search([('company_id', '=', env.company.id)], order='id', limit=1)
    if not almacen:
        almacen = env['stock.warehouse'].sudo().search([], order='id', limit=1)
    ubicacion = almacen.lot_stock_id

# ---------------------------- CLIENTES ----------------------------
for fila in env['x_rpa_cliente'].sudo().search([('x_estado', '=', 'Pendiente')], order='id', limit=500):
    try:
        nombre = texto(fila.x_name)
        # Obligatorios según el auxiliar (foro, 26/09): Name y Company Type
        faltan = [etiqueta for etiqueta, valor in (('Name', nombre), ('Company Type', texto(fila.x_company_type))) if not valor]
        if faltan:
            fila.write({'x_estado': 'Omitido', 'x_mensaje': 'Falta dato obligatorio: ' + ', '.join(faltan)})
            continue
        tipo = texto(fila.x_company_type).lower()
        valores = {
            'name': nombre,
            'company_type': 'company' if tipo in ('company', 'empresa', 'compañía', 'compania') else 'person',
            'email': texto(fila.x_email) or False, 'phone': texto(fila.x_phone) or False,
            'street': texto(fila.x_street) or False, 'street2': texto(fila.x_street2) or False,
            'city': texto(fila.x_city) or False, 'zip': texto(fila.x_zip) or False,
            'website': texto(fila.x_website) or False, 'ref': texto(fila.x_reference) or False,
            'comment': texto(fila.x_notes) or False, 'customer_rank': 1,
        }
        avisos = []
        pais = Pais
        if texto(fila.x_country):
            pais = Pais.search(['|', ('code', '=ilike', texto(fila.x_country)), ('name', '=ilike', texto(fila.x_country))], limit=1)
            if pais:
                valores['country_id'] = pais.id
            else:
                avisos.append('país "%s" no existe' % texto(fila.x_country))
        if texto(fila.x_state):
            dominio = ['|', ('code', '=ilike', texto(fila.x_state)), ('name', '=ilike', texto(fila.x_state))]
            if pais:
                dominio = [('country_id', '=', pais.id)] + dominio
            depto = Departamento.search(dominio, limit=1)
            if depto:
                valores['state_id'] = depto.id
                valores['country_id'] = depto.country_id.id
            else:
                avisos.append('estado "%s" no existe' % texto(fila.x_state))
        if texto(fila.x_related_company):
            empresa = Contacto.search([('name', '=ilike', texto(fila.x_related_company)), ('is_company', '=', True)], limit=1)
            if not empresa:
                empresa = Contacto.create({'name': texto(fila.x_related_company), 'company_type': 'company'})
            valores['parent_id'] = empresa.id
        ids_etiquetas = []
        for nombre_etiqueta in texto(fila.x_tags).replace(';', ',').split(','):
            nombre_etiqueta = nombre_etiqueta.strip()
            if nombre_etiqueta:
                etiqueta = Etiqueta.search([('name', '=ilike', nombre_etiqueta)], limit=1) or Etiqueta.create({'name': nombre_etiqueta})
                ids_etiquetas.append(etiqueta.id)
        if ids_etiquetas:
            valores['category_id'] = [(6, 0, ids_etiquetas)]
        # Si ya existe (misma referencia, correo o nombre) se actualiza en vez de duplicarlo
        contacto = Contacto
        if valores['ref']:
            contacto = Contacto.search([('ref', '=', valores['ref'])], limit=1)
        if not contacto and valores['email']:
            contacto = Contacto.search([('email', '=ilike', valores['email'])], limit=1)
        if not contacto:
            contacto = Contacto.search([('name', '=ilike', nombre)], limit=1)
        if contacto:
            contacto.write(valores)
            accion = 'Actualizado'
        else:
            contacto = Contacto.create(valores)
            accion = 'Creado'
        # Tax ID (NIT): Odoo lo guarda en la empresa "dueña" del contacto (si tiene Related Company, en esa empresa)
        nit = texto(fila.x_tax_id)
        if nit:
            contacto.commercial_partner_id.write({'vat': nit})
        mensaje = accion + ' en Contactos'
        if avisos:
            mensaje += ' (' + '; '.join(avisos) + ')'
        fila.write({'x_estado': 'Procesado', 'x_mensaje': mensaje, 'x_registro_odoo': contacto.id})
    except Exception as error:
        fila.write({'x_estado': 'Error', 'x_mensaje': str(error)})

# ---------------------------- PRODUCTOS ----------------------------
for fila in env['x_rpa_producto'].sudo().search([('x_estado', '=', 'Pendiente')], order='id', limit=500):
    try:
        nombre = texto(fila.x_name)
        # Obligatorios según el auxiliar (foro, 26/09): External ID, Name y Product Type
        faltan = [etiqueta for etiqueta, valor in (('ID Externo', texto(fila.x_id_externo)), ('Name', nombre), ('Product Type', texto(fila.x_product_type))) if not valor]
        if faltan:
            fila.write({'x_estado': 'Omitido', 'x_mensaje': 'Falta dato obligatorio: ' + ', '.join(faltan)})
            continue
        tipo_texto = texto(fila.x_product_type).lower()
        if tipo_texto in ('service', 'servicio'):
            tipo = 'service'
        elif tipo_texto == 'combo':
            tipo = 'combo'
        elif tipo_texto in ('storable', 'storable product', 'almacenable') and not tiene_almacenable:
            tipo = 'product'
        else:
            tipo = 'consu'
        referencia = texto(fila.x_internal_reference)
        valores = {
            'name': nombre, 'type': tipo, 'default_code': referencia or False,
            'list_price': numero(fila.x_sales_price), 'standard_price': numero(fila.x_cost),
            'weight': numero(fila.x_weight), 'description_sale': texto(fila.x_sales_description) or False,
            'sale_ok': True,
        }
        if tiene_almacenable and tipo == 'consu':
            valores['is_storable'] = True
        if tiene_tienda:
            valores['is_published'] = texto(fila.x_esta_publicado).lower() in ('true', 'verdadero', 'sí', 'si', '1', 'yes', 'x')
            valores['public_categ_ids'] = [(4, categoria_web.id)]
        if texto(fila.x_product_values):
            if tiene_desc_web:
                valores['description_ecommerce'] = texto(fila.x_product_values)
            else:
                valores['description'] = texto(fila.x_product_values)
        # Buscar si ya existe: primero por ID Externo, luego por Internal Reference
        id_externo = texto(fila.x_id_externo)
        nombre_xml = ''
        enlace = DatosXml
        if id_externo:
            nombre_xml = id_externo.split('.')[-1].replace(' ', '_')
            enlace = DatosXml.search([('module', '=', '__import__'), ('name', '=', nombre_xml), ('model', '=', 'product.template')], limit=1)
        producto = Plantilla.browse(enlace.res_id).exists() if enlace else Plantilla
        if not producto and referencia:
            producto = Plantilla.search([('default_code', '=', referencia)], limit=1)
        # Código de barras: solo si ningún OTRO producto ya lo usa (Odoo no permite repetidos)
        avisos = []
        codigo = texto(fila.x_barcode)
        if codigo.endswith('.0'):
            codigo = codigo[:-2]
        if codigo:
            dominio = [('barcode', '=', codigo)]
            if producto:
                dominio.append(('product_tmpl_id', '!=', producto.id))
            if Variante.search_count(dominio):
                avisos.append('código de barras %s repetido, no se asignó' % codigo)
            else:
                valores['barcode'] = codigo
        if producto:
            producto.write(valores)
            accion = 'Actualizado'
        else:
            producto = Plantilla.create(valores)
            accion = 'Creado'
        if nombre_xml and not enlace:
            DatosXml.create({'module': '__import__', 'name': nombre_xml, 'model': 'product.template', 'res_id': producto.id})
        # Cantidad a la mano: ajuste de inventario a la cantidad EXACTA del Excel
        cantidad_texto = texto(fila.x_cantidad_a_la_mano)
        almacenable = producto.is_storable if tiene_almacenable else producto.type == 'product'
        if cantidad_texto and tiene_inventario and ubicacion and almacenable:
            quant = env['stock.quant'].sudo().with_context(inventory_mode=True).create({
                'product_id': producto.product_variant_id.id,
                'location_id': ubicacion.id,
                'inventory_quantity': numero(cantidad_texto),
            })
            quant.action_apply_inventory()
            avisos.append('existencia %s' % numero(cantidad_texto))
        mensaje = accion + ' en Productos'
        if avisos:
            mensaje += ' (' + '; '.join(avisos) + ')'
        fila.write({'x_estado': 'Procesado', 'x_mensaje': mensaje, 'x_registro_odoo': producto.id})
    except Exception as error:
        fila.write({'x_estado': 'Error', 'x_mensaje': str(error)})
