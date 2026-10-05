' === QuetzalMart RPA · Crear un INSERT por fila para la tabla centralizada ===
' in_tipo = "clientes" -> x_rpa_cliente   |   in_tipo = "productos" -> x_rpa_producto
Dim mapa As Dictionary(Of String, String)
Dim tabla As String
If in_tipo = "clientes" Then
    tabla = "x_rpa_cliente"
    mapa = New Dictionary(Of String, String) From {
        {"Name", "x_name"}, {"Company Type", "x_company_type"}, {"Related Company", "x_related_company"},
        {"Email", "x_email"}, {"Phone", "x_phone"}, {"Street", "x_street"}, {"Street2", "x_street2"},
        {"City", "x_city"}, {"State", "x_state"}, {"Zip", "x_zip"}, {"Country", "x_country"},
        {"Tax ID", "x_tax_id"}, {"Website", "x_website"}, {"Tags", "x_tags"}, {"Reference", "x_reference"},
        {"Notes", "x_notes"}, {"Archivo origen", "x_archivo_origen"}}
Else
    tabla = "x_rpa_producto"
    mapa = New Dictionary(Of String, String) From {
        {"ID Externo", "x_id_externo"}, {"Name", "x_name"}, {"Product Type", "x_product_type"},
        {"Internal Reference", "x_internal_reference"}, {"Barcode", "x_barcode"}, {"Sales Price", "x_sales_price"},
        {"Cost", "x_cost"}, {"Weight", "x_weight"}, {"Sales Description", "x_sales_description"},
        {"Product Values", "x_product_values"}, {"Cantidad a la mano", "x_cantidad_a_la_mano"},
        {"Está publicado", "x_esta_publicado"}, {"Archivo origen", "x_archivo_origen"}}
End If

out_sqls = New List(Of String)
If in_dt Is Nothing Then Return
For Each fila As DataRow In in_dt.Rows
    Dim columnasSql As New List(Of String)
    Dim valoresSql As New List(Of String)
    For Each par As KeyValuePair(Of String, String) In mapa
        Dim valor As String = ""
        If in_dt.Columns.Contains(par.Key) AndAlso Not IsDBNull(fila(par.Key)) Then valor = fila(par.Key).ToString().Trim()
        columnasSql.Add(par.Value)
        ' Duplicar la comilla simple deja el texto seguro dentro del SQL
        valoresSql.Add(If(valor = "", "NULL", "'" & valor.Replace("'", "''") & "'"))
    Next
    columnasSql.AddRange({"x_lote", "x_estado", "create_date", "write_date"})
    valoresSql.AddRange({"'" & in_lote & "'", "'Pendiente'", "(now() at time zone 'utc')", "(now() at time zone 'utc')"})
    out_sqls.Add("INSERT INTO " & tabla & " (" & String.Join(", ", columnasSql) & ") VALUES (" & String.Join(", ", valoresSql) & ")")
Next
