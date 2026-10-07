' === QuetzalMart RPA · Normalizar una hoja "clientes" o "productos" ===
' Copia las filas de in_dtHoja al consolidado que corresponde, usando los
' encabezados de los Excel de ejemplo (acepta "Name*", "ID Externo", tildes, etc.)
Dim columnasClientes As String() = {"Name", "Company Type", "Related Company", "Email", "Phone", "Street", "Street2", "City", "State", "Zip", "Country", "Tax ID", "Website", "Tags", "Reference", "Notes"}
Dim columnasProductos As String() = {"External ID", "Name", "Product Type", "Internal Reference", "Barcode", "Sales Price", "Cost", "Weight", "Sales Description", "Product Values", "Cantidad a la mano", "Está publicado"}
Dim sinonimos As New Dictionary(Of String, String) From {
    {"id externo", "external id"}, {"published", "esta publicado"}, {"is published", "esta publicado"},
    {"quantity on hand", "cantidad a la mano"}, {"on hand", "cantidad a la mano"}}

Dim normalizar As Func(Of String, String) = Function(texto As String)
    Dim limpio As String = texto.Replace("*", "").Trim().ToLowerInvariant().Normalize(System.Text.NormalizationForm.FormD)
    Dim sb As New System.Text.StringBuilder()
    For Each letra As Char In limpio
        If System.Globalization.CharUnicodeInfo.GetUnicodeCategory(letra) <> System.Globalization.UnicodeCategory.NonSpacingMark Then sb.Append(letra)
    Next
    Dim resultado As String = System.Text.RegularExpressions.Regex.Replace(sb.ToString(), "\s+", " ")
    If sinonimos.ContainsKey(resultado) Then resultado = sinonimos(resultado)
    Return resultado
End Function

Dim aTexto As Func(Of Object, String) = Function(valor As Object)
    If valor Is Nothing OrElse IsDBNull(valor) Then Return ""
    If TypeOf valor Is Double Then Return CDbl(valor).ToString("0.##########", System.Globalization.CultureInfo.InvariantCulture)
    If TypeOf valor Is Boolean Then Return If(CBool(valor), "True", "False")
    If TypeOf valor Is DateTime Then Return CDate(valor).ToString("yyyy-MM-dd")
    Return Convert.ToString(valor, System.Globalization.CultureInfo.InvariantCulture).Trim()
End Function

Dim esClientes As Boolean = (in_tipo = "clientes")
Dim columnas As String() = If(esClientes, columnasClientes, columnasProductos)
Dim destino As DataTable = If(esClientes, io_dtClientes, io_dtProductos)
If destino Is Nothing Then destino = New DataTable()
If destino.Columns.Count = 0 Then
    For Each nombreColumna As String In columnas
        destino.Columns.Add(nombreColumna, GetType(String))
    Next
    destino.Columns.Add("Archivo origen", GetType(String))
End If

' Para cada columna oficial busca en qué posición viene en la hoja (-1 si no viene)
Dim posiciones As New List(Of Integer)
For Each nombreColumna As String In columnas
    Dim posicion As Integer = -1
    For i As Integer = 0 To in_dtHoja.Columns.Count - 1
        If normalizar(in_dtHoja.Columns(i).ColumnName) = normalizar(nombreColumna) Then
            posicion = i
            Exit For
        End If
    Next
    posiciones.Add(posicion)
Next

out_filas = 0
For Each filaHoja As DataRow In in_dtHoja.Rows
    Dim valores As New List(Of Object)
    Dim tieneDatos As Boolean = False
    For Each posicion As Integer In posiciones
        Dim valor As String = If(posicion >= 0, aTexto(filaHoja(posicion)), "")
        If valor <> "" Then tieneDatos = True
        valores.Add(valor)
    Next
    If tieneDatos Then
        valores.Add(in_archivo)
        destino.Rows.Add(valores.ToArray())
        out_filas = out_filas + 1
    End If
Next

If esClientes Then
    io_dtClientes = destino
Else
    io_dtProductos = destino
End If
