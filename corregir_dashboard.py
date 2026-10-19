
from pathlib import Path
import re
import sys
import textwrap
import zipfile

BASE = Path(__file__).resolve().parent
APP = BASE / "app.py"
PARQUET = BASE / "resumen_ifc_consolidado.parquet"
REQ = BASE / "requirements.txt"
ZIP_OUT = BASE / "dashboard_bim_apv_corregido.zip"
BACKUP = BASE / "app_original_backup.py"

if not APP.exists():
    sys.exit("ERROR: No encuentro app.py en esta carpeta.")

source = APP.read_text(encoding="utf-8")

# Conservar el original antes de modificar nada.
if not BACKUP.exists():
    BACKUP.write_text(source, encoding="utf-8")

# Sustituir los argumentos obsoletos de Streamlit.
source = source.replace(
    "use_container_width=True",
    'width="stretch"'
).replace(
    "use_container_width=False",
    'width="content"'
)

# Añadir una marca de progreso al entrar en cada pestaña.
def marcar_tab(match):
    indent = match.group(1)
    tab_name = match.group(2)
    marker = (
        f'{indent}print("[DIAG RENDER] Entrando en '
        f'{tab_name}", flush=True)\n'
    )
    return marker + match.group(0)

source = re.sub(
    r"(?m)^([ \t]*)with (tab\d+):[ \t]*$",
    marcar_tab,
    source
)

# Mostrar el traceback dentro de Streamlit en vez de depender
# exclusivamente de los logs del servidor.
marker = "# --- CAPTURA GLOBAL DE ERRORES PARA DEPLOY ---"

if marker not in source:
    title = 'st.title("📋 Dashboard Integral de Auditoría BIM - APV")'

    before, separator, after = source.partition(title)

    if not separator:
        sys.exit(
            "ERROR: No encuentro el título esperado. "
            "No se ha modificado app.py."
        )

    after = textwrap.indent(after.lstrip("\n"), "    ")

    source = (
        before + separator + "\n\n"
        + marker + "\n"
        + "try:\n"
        + after + "\n"
        + "except Exception as exc:\n"
        + "    print('[DIAG FATAL] Error de ejecución:', "
          "repr(exc), flush=True)\n"
        + "    st.error('La aplicación se interrumpió durante "
          "el renderizado.')\n"
        + "    st.exception(exc)\n"
    )

# Validar sintaxis antes de reemplazar la aplicación.
try:
    compile(source, str(APP), "exec")
except SyntaxError as exc:
    sys.exit(
        f"ERROR de sintaxis en la versión preparada: {exc}. "
        "Se conserva el app.py original."
    )

APP.write_text(source, encoding="utf-8")

# Dependencias compatibles con la versión preparada.
requirements = """\
streamlit==1.55.0
pandas>=2.2,<3.0
numpy>=1.26,<3.0
plotly>=5.24,<7.0
pyarrow>=18,<23
python-calamine>=0.3
ifcopenshell>=0.8.3,<0.9
"""
REQ.write_text(requirements, encoding="utf-8")

# Generar paquete completo para desplegar.
if not PARQUET.exists():
    print(
        "AVISO: No está el Parquet en esta carpeta. "
        "El ZIP se creará sin los datos."
    )

with zipfile.ZipFile(
    ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED
) as zf:
    zf.write(APP, "app.py")
    zf.write(REQ, "requirements.txt")

    if PARQUET.exists():
        zf.write(PARQUET, PARQUET.name)

    if BACKUP.exists():
        zf.write(BACKUP, BACKUP.name)

    readme = """\
DASHBOARD BIM APV - DESPLIEGUE

1. Conserva app.py y requirements.txt en la raíz del repositorio.
2. Conserva resumen_ifc_consolidado.parquet junto a app.py.
3. Usa Python 3.12 en la configuración de despliegue.
4. Haz commit y reinicia la aplicación.

Los registros [DIAG RENDER] indican la última pestaña
a la que llegó el programa.
[DIAG FATAL] muestra la excepción si se interrumpe
la ejecución del código Python.

Los avisos de ancho no demuestran por sí solos
un fallo de lectura del Parquet.
"""
    zf.writestr("LEEME_DESPLIEGUE.txt", readme)

print("✅ Código preparado y sintaxis validada.")
print(f"📦 Paquete: {ZIP_OUT}")
print(f"🛟 Copia original: {BACKUP}")
print("Sube el ZIP generado o sus archivos a GitHub.")
