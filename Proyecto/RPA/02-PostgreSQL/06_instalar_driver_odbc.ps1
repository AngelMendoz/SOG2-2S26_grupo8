# Instala el driver ODBC de PostgreSQL (64 bits) y muestra su nombre exacto.
# Debe aparecer "PostgreSQL Unicode(x64)": es el texto que va en Driver={...} de la cadena de conexion del robot.
winget install --id PostgreSQL.psqlODBC --exact
Get-OdbcDriver -Platform 64-bit | Where-Object Name -like "PostgreSQL*" | Select-Object Name
