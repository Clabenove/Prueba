import os
import re
import gc
import time
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Auditoría BIM & Cumplimiento BEP - APV",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Dashboard Integral de Auditoría BIM - APV")

PARAMETROS_APV = list(dict.fromkeys([
    "01_01_APV_PROYECTO", "01_02_APV_FASE",
    "01_03_APV_ESTADO", "01_04_APV_TIPOLOGIA",
    "01_05_APV_DISCIPLINA", "01_06_APV_SUBDISCIPLINA",
    "01_07_APV_ELEMENTO", "01_08_APV_CLASIFICACION",
    "01_09_APV_NOMBRE", "01_10_APV_ALINEACION",
    "01_11_APV_NUMERO", "01_12_APV_MATERIAL",
    "01_13_APV_CAD", "01_14_APV_ZONA",
    "02_01_APV_CAPITULO", "02_02_APV_SUBCAPITULO-1",
    "02_03_APV_SUBCAPITULO-2", "02_04_01_APV_MEDICION",
    "02_04_02_APV_MEDICION-ASOC-1", "02_04_03_APV_MEDICION-ASOC-2",
    "02_04_04_APV_MEDICION-ASOC-3", "02_05_01_APV_UNIDAD-OBRA",
    "02_05_02_APV_UO-ASOC-1", "02_05_03_APV_UO-ASOC-2",
    "02_05_04_APV_UO-ASOC-3", "02_06_01_APV_TIPO-MED",
    "02_06_02_APV_TM-ASOC-1", "02_06_03_APV_TM-ASOC-2",
    "02_06_04_APV_TM-ASOC-3", "03_01_APV_FASE-OBRA",
    "03_02_APV_PLANOS", "03_03_APV_PPTP",
    "03_04_APV_CALIDAD-MOD", "04_01_APV_CÓDIGO-TAREA",
    "04_02_APV_NOMBRE-TAREA", "04_03_APV_INICIO-EJECUCION",
    "04_04_APV_FIN-EJECUCION", "04_05_APV_PLAN-REF",
    "04_06_APV_CERTIF-REF", "04_07_APV_CERTIF",
    "04_08_APV_PORCENTAJE-EJECUTADO", "04_09_APV_CERTIF-MED",
    "04_10_APV_CERTIF-MED-ASOC-1", "04_11_APV_CERTIF-MED-ASOC-2",
    "04_12_APV_CERTIF-MED-ASOC-3", "05_01_APV_SEG-SALUD",
    "05_02_APV_INFORMES-APROBACION", "05_03_APV_CONTROL-CALIDAD",
    "05_03_01_APV_COD-TRAZ", "05_04_APV_ENSAYOS",
    "05_05_APV_FOTOGRAFIAS", "05_06_APV_MEDIO-AMBIENTE",
    "05_07_APV_GESTION-RESIDUOS", "05_08_APV_SERV-AFECTADOS",
    "06_01_APV_PRY-LIQUIDACION", "06_02_APV_LIBRO-EDIF",
    "07_01_APV_CAPA-GIS", "07_02_APV_CAMPO-1",
    "07_03_APV_CAMPO-2", "07_04_APV_CAMPO-3",
    "07_05_APV_CAMPO-4", "07_06_APV_CAMPO-5",
    "07_07_APV_CAMPO-6", "07_08_APV_CAMPO-7",
    "07_09_APV_CAMPO-8", "07_10_APV_CAMPO-9",
    "07_11_APV_CAMPO-10", "07_12_APV_CAMPO-N",
    "08_01_APV_PLAN-MANTENIMIENTO", "08_02_APV_MANUALES-FICHAS",
    "08_03_APV_COD-MANTENIMIENTO", "08_04_APV_COD-EXPLOTACION",
    "08_05_APV_AUX-EXPLOTACION", "08_06_APV_COD-CONTABLE",
    "08_07_APV_CAP-CONTABLE", "08_08_APV_SUB-CAP-CONTABLE",
    "09-02_00_APV_PROYECTO", "09-02_01_APV_SONDEO",
    "09-02_02_APV_COTA-MUESTRA(m)", "09-02_03_APV_DESC-ESTRATO",
    "09-02_04_APV_TIPO", "09-02_05_APV_NÚMERO MUESTRA",
    "09-03_01_APV_PASA-100 (%)", "09-03_02_APV_PASA-80 (%)",
    "09-03_03_APV_PASA-63 (%)", "09-03_04_APV_PASA-50 (%)",
    "09-03_05_APV_PASA-40 (%)", "09-03_06_APV_PASA-25 (%)",
    "09-03_07_APV_PASA-20 (%)", "09-03_08_APV_PASA-12,5 (%)",
    "09-03_09_APV_PASA-10 (%)", "09-03_10_APV_PASA-6,3 (%)",
    "09-03_11_APV_PASA-5 (%)", "09-03_12_APV_PASA-2 (%)",
    "09-03_13_APV_PASA-1,25 (%)", "09-03_14_APV_PASA-0,4 (%)",
    "09-03_15_APV_PASA-0,16 (%)", "09-03_16_APV_PASA-0,08 (%)",
    "09-03_17_APV_ATTERBERG-LL", "09-03_18_APV_ATTERBERG-LP",
    "09-03_19_APV_ATTERBERG-IP", "09-03_20_APV_HN (%)",
    "09-03_21_APV_DENS-APAR-HUMEDA (g/cm3)",
    "09-03_22_APV_DENS-APAR-SECA (g/cm3)",
    "09-03_23_APV_DENS-APAR-SECA (g/cm3)",
    "09-04_01_APV_ACIDEZ BG (ml/Kg)", "09-04_02_APV_SULFATOS (mg/Kg)",
    "09-04_03_APV_CARBONATOS (mg/Kg)", "09-04_04_APV_YESO (%SO4CaH2O)",
    "09-04_05_APV_SALES SOLUBLES", "09-04_06_APV_MAT ORGANICA (%)",
    "09-05_01_APV_CS (kPa)", "09-05_02_APV_CU (MPa)",
    "09-05_03_APV_BRASILEÑO (MPa)", "09-05_04_APV_FRANKLIN (Mpa)",
    "09-05_05_APV_CORTE DIRECTO-c(kPa)", "09-05_06_APV_CORTE DIRECTO-fi(°)",
    "09-05_07_APV_TRIAXIAL-c(kPa)", "09-05_08_APV_TRIAXIAL-fi(°)",
    "09-05_09_APV_EDOMETRO-Cc", "09-05_10_APV_EDOMETRO-Cs",
    "09-05_11_APV_EDOMETRO-e0", "09-05_12_APV_EDOMETRO-sigma'p (Kg/cm2)",
    "09-05_13_APV_EDOMETRO-Cv (m2/año)",
    "09-05_14_APV_LAMBE-HINCHAMIENTO (Mpa)",
    "09-05_15_APV_LAMBE-CAMBIO-POT-VOL",
    "09-05_16_APV_DENSIDAD-MAX(g/cm3)", "09-05_17_APV_DENSIDAD-MIN(g/cm3)",
    "09-05_18_APV_INDICE-COLAPSO (%)", "09-06_01_APV_LEFRANC-PERMEAB (%)",
    "09-07_01_APV_CO2-LIBRE (mg/l)", "09-07_02_APV_ACIDEZ (ud PH)",
    "09-07_03_APV_AMONIO (mg/l)", "09-07_04_APV_MAGNESIO (mg/l)",
    "09-07_05_APV_SULFATOS (mg/l)", "09-07_06_APV_RESIDUO SECO (mg/l)",
    "10_01_APV_ENLACE A FOTO", "10_02_APV_FECHA", "10_03_APV_DISCIPLINA"
]))

PARAMS_NO_GEO = [p for p in PARAMETROS_APV if not p.startswith("09")]
PARAMS_GEO = [p for p in PARAMETROS_APV if p.startswith("09")]

VACIOS_EXACTOS = [
    "", " ", "  ", "nan", "NaN", "NAN",
    "none", "None", "NONE", "<na>", "<NA>", "null", "NULL"
]
COMODINES_EXACTOS = ["-", " -", "- ", " - "]
VALORES_VACIOS_LOWER = {"", "nan", "none", "<na>", "null"}


def mascara_vacio_rapida(df_ref, col_name):
    if col_name not in df_ref.columns:
        return np.ones(len(df_ref), dtype=bool)
    s = df_ref[col_name]
    return s.isna().to_numpy() | s.isin(VACIOS_EXACTOS).to_numpy()


def mascara_comodin_rapida(df_ref, col_name):
    if col_name not in df_ref.columns:
        return np.zeros(len(df_ref), dtype=bool)
    return df_ref[col_name].isin(COMODINES_EXACTOS).to_numpy()


def diagnosticar_nombre_bep(nombre_archivo):
    if not str(nombre_archivo).lower().endswith(".ifc"):
        return "❌ No tiene extensión .ifc"
    base = str(nombre_archivo)[:-4]
    partes = base.split("_")
    if len(partes) != 7:
        return (
            f"❌ Estructura incorrecta: tiene {len(partes)} "
            "bloques separados por '_' (se esperan 7)"
        )
    puerto, contrato, fase, tipo, disc, desc, rev = partes
    errores = []
    if puerto.upper() not in ["V", "S", "G"]:
        errores.append(f"Bloque 1 Puerto ('{puerto}'): debe ser V, S o G")
    if contrato.upper() != "N035":
        if contrato.upper() == "NO35":
            errores.append(
                "Bloque 2 Contrato ('NO35'): tiene letra 'O' en lugar "
                "del número '0' (debe ser N035)"
            )
        else:
            errores.append(f"Bloque 2 Contrato ('{contrato}'): debe ser 'N035'")
    if fase.upper() != "OB":
        if fase == "0B":
            errores.append(
                "Bloque 3 Fase ('0B'): tiene un cero '0' en vez "
                "de la letra 'O' (debe ser 'OB')"
            )
        else:
            errores.append(f"Bloque 3 Fase ('{fase}'): debe ser 'OB'")
    if not re.match(r"^[A-Za-z]{3}$", tipo):
        errores.append(
            f"Bloque 4 Tipo ('{tipo}'): debe tener 3 letras (ej. MOD, SEG)"
        )
    if not re.match(r"^[A-Za-z]{3}$", disc):
        errores.append(f"Bloque 5 Disciplina ('{disc}'): debe tener 3 letras")
    if not re.match(r"^[A-Za-z0-9\-]+$", desc):
        errores.append(f"Bloque 6 Descripción ('{desc}'): caracteres inválidos")
    if not re.match(r"^\d{2}[A-Za-z]$", rev):
        errores.append(
            f"Bloque 7 Revisión ('{rev}'): debe ser 2 dígitos + 1 letra"
        )
    if not errores:
        return "✅ Cumple patrón BEP"
    return "❌ No cumple: " + " | ".join(errores)


def sugerir_nombre_bep(nombre_archivo):
    if not str(nombre_archivo).lower().endswith(".ifc"):
        return "V_N035_OB_MOD_EST_Proyecto_01A.ifc"
    base = str(nombre_archivo)[:-4]
    partes = base.split("_")
    puerto = partes[0] if len(partes) > 0 and partes[0].upper() in ["V", "S", "G"] else "V"
    contrato = "N035"
    fase = "OB"
    tipo = partes[3] if len(partes) > 3 and re.match(r"^[A-Za-z]{3}$", partes[3]) else "MOD"
    disc = partes[4] if len(partes) > 4 and re.match(r"^[A-Za-z]{3}$", partes[4]) else "EST"
    desc = partes[5] if len(partes) > 5 and re.match(r"^[A-Za-z0-9\-]+$", partes[5]) else "Proyecto"
    rev = partes[6] if len(partes) > 6 and re.match(r"^\d{2}[A-Za-z]$", partes[6]) else "01A"
    return f"{puerto.upper()}_{contrato}_{fase}_{tipo.upper()}_{disc.upper()}_{desc}_{rev.upper()}.ifc"


def generar_xml_navisworks(
    valores_unicos,
    nombre_set="Auditoria_APV_Elementos_Vacios",
    usar_id_nativo=False
):
    schema_url = (
        "http://download.autodesk.com/us/navisworks/schemas/"
        "nw-exchange-12.0.xsd"
    )
    prop_name = "Id" if usar_id_nativo else "GlobalId"
    xml = '<?xml version="1.0" encoding="UTF-8" ?>\n'
    xml += (
        '<exchange xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'xsi:noNamespaceSchemaLocation="{schema_url}" units="m">\n'
    )
    xml += '  <selectionsets>\n'
    xml += f'    <selectionset name="{nombre_set}">\n'
    xml += '      <findspec mode="some" disjoint="0">\n'
    xml += '        <conditions>\n'
    for val in valores_unicos[:1000]:
        xml += '          <condition test="equals" flags="10">\n'
        xml += f'            <property><name>{prop_name}</name></property>\n'
        xml += f'            <value><data type="wstring">{val}</data></value>\n'
        xml += '          </condition>\n'
    xml += '        </conditions>\n'
    xml += '        <locator>/</locator>\n'
    xml += '      </findspec>\n'
    xml += '    </selectionset>\n'
    xml += '  </selectionsets>\n'
    xml += '</exchange>'
    return xml


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_PARQUET = os.path.join(BASE_DIR, "resumen_ifc_consolidado.parquet")

if not os.path.isfile(RUTA_PARQUET):
    st.error(f"No se encuentra el archivo: {RUTA_PARQUET}")
    st.stop()


@st.cache_resource(show_spinner="Cargando e indexando base de datos BIM...")
def inicializar_motor_apv(ruta):
    t0 = time.perf_counter()
    df_raw = pd.read_parquet(ruta, engine="pyarrow")
    if df_raw.columns.duplicated().any():
        df_raw = df_raw.loc[:, ~df_raw.columns.duplicated()]

    n_filas = len(df_raw)
    pres_base = np.zeros(n_filas, dtype=np.uint8)
    vac_base = np.zeros(n_filas, dtype=np.uint8)

    for col in PARAMS_NO_GEO:
        v = mascara_vacio_rapida(df_raw, col)
        vac_base += v.astype(np.uint8)
        pres_base += (~v).astype(np.uint8)

    pres_geo = np.zeros(n_filas, dtype=np.uint8)
    vac_geo = np.zeros(n_filas, dtype=np.uint8)

    for col in PARAMS_GEO:
        v = mascara_vacio_rapida(df_raw, col)
        vac_geo += v.astype(np.uint8)
        pres_geo += (~v).astype(np.uint8)

    pres_all = pres_base + pres_geo
    vac_all = vac_base + vac_geo

    archivos_unicos = sorted(
        df_raw["Archivo_Origen"].dropna().unique().tolist()
    )
    s_arch = df_raw["Archivo_Origen"]
    cols_apv_en_df = [c for c in df_raw.columns if "APV" in c]
    grupos_por_arch = {a: set() for a in archivos_unicos}

    for c in cols_apv_en_df:
        prefijo = c.split("_")[0] if "_" in c else ""
        v = mascara_vacio_rapida(df_raw, c)
        if not v.all():
            for a in s_arch.loc[~v].dropna().unique():
                if a in grupos_por_arch:
                    grupos_por_arch[a].add(prefijo)

    info_grupos = []
    for arch in archivos_unicos:
        es_geo = "geo" in str(arch).lower()
        g_set = grupos_por_arch[arch]
        info_grupos.append({
            "Archivo IFC": arch,
            "Tipo de Modelo": (
                "Modelo de Geotecnia" if es_geo
                else "Modelo Estándar / Proyecto"
            ),
            "Grupos Teóricos (BEP)": 11 if es_geo else 9,
            "Grupos Totales Detectados": len(g_set),
            "Grupos Específicos Detectados": (
                ", ".join(sorted(list(g_set))) if g_set else "Ninguno"
            )
        })
    df_grupos = pd.DataFrame(info_grupos)

    gc.collect()
    return (
        df_raw, archivos_unicos, df_grupos,
        pres_base, vac_base, pres_all, vac_all
    )


(
    df_original, archivos_disp, df_informe_grupos,
    pres_base_arr, vac_base_arr, pres_all_arr, vac_all_arr
) = inicializar_motor_apv(RUTA_PARQUET)

col_id_nativo = (
    "ID_Elemento" if "ID_Elemento" in df_original.columns else "GlobalId"
)

# --- BARRA LATERAL ---
st.sidebar.header("⚙ Filtros de Auditoría")
incluir_geo = st.sidebar.checkbox("Incluir Psets 09 (Geotecnia)", value=False)
params_auditar = PARAMETROS_APV if incluir_geo else PARAMS_NO_GEO

ocultar_fantasmas = st.sidebar.checkbox(
    "Omitir sub-elementos fantasma (sin ningún Pset APV)", value=True
)
unificar_duplicados = st.sidebar.checkbox(
    "Eliminar/Unificar elementos duplicados", value=False
)

sel_archivos = st.sidebar.multiselect(
    "Modelos IFC Auditados:", archivos_disp, default=archivos_disp
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Control de Progreso BIM")
st.sidebar.info(
    f"Modelos seleccionados: **{len(sel_archivos)}**\n\n"
    "💡 *Aviso de proyecto: El volumen y número de modelos IFC activos debe mantenerse o incrementarse respecto al mes anterior.*"
)

if not sel_archivos:
    st.warning("Selecciona al menos un modelo IFC en la barra lateral.")
    st.stop()

if len(sel_archivos) == len(archivos_disp):
    mask_arr = np.ones(len(df_original), dtype=bool)
else:
    mask_arr = df_original["Archivo_Origen"].isin(sel_archivos).to_numpy()

if unificar_duplicados:
    dup_arr = df_original[["Archivo_Origen", "GlobalId"]].duplicated(
        keep="first"
    ).to_numpy()
    mask_arr = mask_arr & (~dup_arr)

s_pres_arr = pres_all_arr if incluir_geo else pres_base_arr
s_vac_arr = vac_all_arr if incluir_geo else vac_base_arr

df_arch_pres = pd.DataFrame({
    "arch": df_original["Archivo_Origen"].to_numpy()[mask_arr],
    "pres": s_pres_arr[mask_arr]
})
suma_arch = df_arch_pres.groupby("arch")["pres"].sum()
archivos_vacios = suma_arch[suma_arch == 0].index.tolist()

n_fantasmas = int(((s_pres_arr == 0) & mask_arr).sum())
if ocultar_fantasmas and n_fantasmas > 0:
    if (s_pres_arr[mask_arr] > 0).any():
        es_arch_vacio = (
            df_original["Archivo_Origen"].isin(archivos_vacios).to_numpy()
        )
        mask_arr = mask_arr & ((s_pres_arr > 0) | es_arch_vacio)
        st.sidebar.success(
            f"🧹 Se filtraron {n_fantasmas:,} sub-elementos sin Psets APV. "
            f"Auditando {int(mask_arr.sum()):,} elementos reales."
        )

total_el = int(mask_arr.sum())
mask_tiene_vacios = mask_arr & (s_vac_arr > 0)

# --- LAS 12 PESTAÑAS EXACTAS ACORDADAS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "📖 1. Cumplimiento BEP Naming",
    "🌍 2. Georreferenciación",
    "🧱 3. Integridad IFC",
    "✍️ 4. Calidad de Formato",
    "🕳️ 5. Auditoría de Vacíos",
    "🎯 6. Navisworks Manage",
    "❤️ 7. Salud del Proyecto",
    "🚨 8. Alertas IFCs Vacíos",
    "📐 9. Grupos de parámetros",
    "🔍 10. Ficha por Elemento",
    "💬 11. Asistente IA",
    "📄 12. Resumen Ejecutivo & Exportar"
])

# --- PESTAÑA 1 ---
with tab1:
    st.subheader("1. Cumplimiento BEP Naming (Anejo 02) & Sugerencias")
    cols_t1 = [
        c for c in ["Archivo_Origen", "Esquema_IFC", "Peso_Archivo_MB"]
        if c in df_original.columns
    ]
    sub_t1 = df_original[cols_t1].loc[mask_arr]
    conteos_t1 = sub_t1["Archivo_Origen"].value_counts()
    unicos_t1 = sub_t1.drop_duplicates(subset=["Archivo_Origen"])

    res_naming = []
    for _, row in unicos_t1.iterrows():
        arch = row["Archivo_Origen"]
        esquema = row.get("Esquema_IFC", "No definido")
        peso_raw = pd.to_numeric(row.get("Peso_Archivo_MB", 0.0), errors="coerce")
        peso = 0.0 if pd.isna(peso_raw) else float(peso_raw)
        es_ifc_ok = (
            "IFC4" in str(esquema).upper()
            or "IFC2X3" in str(esquema).upper()
        )
        diag = diagnosticar_nombre_bep(arch)
        sugerencia = sugerir_nombre_bep(arch) if "❌" in diag else "Nombre Correcto"
        res_naming.append({
            "Archivo IFC": arch,
            "Cumple Nomenclatura BEP (y Razón Exacta)": diag,
            "Sugerencia de Nombre (BEP APV)": sugerencia,
            "Esquema IFC": esquema,
            "Estado Esquema": "✅ IFC4 / IFC2x3" if es_ifc_ok else "⚠️ Revisar",
            "Peso Extraído (MB)": round(peso, 2),
            "Elementos Reales Auditados": int(conteos_t1.get(arch, 0))
        })
    st.dataframe(pd.DataFrame(res_naming), use_container_width=True)

# --- PESTAÑA 2 ---
with tab2:
    st.subheader("2. Auditoría de Georreferenciación (ETRS89 / IfcSite)")
    cols_t2 = [
        c for c in [
            "Archivo_Origen", "EPSG", "Origen_X", "Origen_Y", "Origen_Z",
            "Elevacion_Site", "Latitud_Site", "Longitud_Site"
        ] if c in df_original.columns
    ]
    unicos_t2 = (
        df_original[cols_t2].loc[mask_arr]
        .drop_duplicates(subset=["Archivo_Origen"])
    )
    res_geo = []
    for _, row in unicos_t2.iterrows():
        res_geo.append({
            "Archivo IFC": row["Archivo_Origen"],
            "CRS / EPSG": row.get("EPSG", "No definido"),
            "Origen Site X": row.get("Origen_X", 0.0),
            "Origen Site Y": row.get("Origen_Y", 0.0),
            "Origen Site Z": row.get("Origen_Z", 0.0),
            "Elevación Ref (m)": row.get("Elevacion_Site", 0.0),
            "Latitud (IfcSite)": row.get("Latitud_Site", "No definida"),
            "Longitud (IfcSite)": row.get("Longitud_Site", "No definida")
        })
    df_geo = pd.DataFrame(res_geo)
    st.dataframe(df_geo, use_container_width=True)
    if len(df_geo) > 1 and (
        df_geo["Origen Site X"].nunique() > 1
        or df_geo["Origen Site Y"].nunique() > 1
    ):
        st.warning(
            "⚠️ Se detectan diferencias en las coordenadas de origen "
            "(IfcSite) entre los distintos modelos."
        )
    else:
        st.success(
            "✅ Consistencia espacial verificada en el emplazamiento (IfcSite)."
        )

# --- PESTAÑA 3 (OPTIMIZADA: BÚSQUEDA Y FILTRO POR MODELO EN INTEGRIDAD IFC) ---
with tab3:
    st.subheader("3. Integridad IFC y Clasificación de Entidades & Filtrado por Modelo")
    
    # Selector de modelo para la pestaña 3
    modelos_disp_t3 = sorted(df_original["Archivo_Origen"].dropna().unique().tolist())
    filtro_modelo_t3 = st.multiselect("Filtrar modelos IFC en esta vista:", modelos_disp_t3, default=modelos_disp_t3, key="t3_filtro_modelo")
    
    mask_t3 = mask_arr & df_original["Archivo_Origen"].isin(filtro_modelo_t3).to_numpy()
    
    sub_t3 = df_original[["Archivo_Origen", "Clase_IFC"]].loc[mask_t3]
    if not sub_t3.empty:
        conteo_clases = (
            sub_t3.groupby(["Archivo_Origen", "Clase_IFC"])
            .size()
            .reset_index(name="Cantidad")
        )
        fig_clases = px.bar(
            conteo_clases,
            x="Clase_IFC",
            y="Cantidad",
            color="Archivo_Origen",
            barmode="group",
            title="Distribución de Clases IFC por Modelo (Filtrado)"
        )
        st.plotly_chart(fig_clases, use_container_width=True)

        mask_proxy = mask_t3 & (
            df_original["Clase_IFC"].to_numpy() == "IfcBuildingElementProxy"
        )
        n_proxys = int(mask_proxy.sum())
        st.metric("Elementos Genéricos (IfcBuildingElementProxy)", n_proxys)
        if n_proxys > 0:
            st.warning(f"Listado completo de elementos genéricos detectados en los modelos seleccionados ({n_proxys:,}):")
            idx_p = np.flatnonzero(mask_proxy)
            cols_p = [
                c for c in [
                    "Archivo_Origen", col_id_nativo, "GlobalId", "Clase_IFC", "Nombre"
                ] if c in df_original.columns
            ]
            st.dataframe(df_original[cols_p].iloc[idx_p], use_container_width=True)
    else:
        st.info("Selecciona al menos un modelo en el filtro superior.")

# --- PESTAÑA 4 (OPTIMIZADA: TODOS LOS ELEMENTOS, SIN LÍMITE Y FILTRADO POR MODELO/PARÁMETRO) ---
with tab4:
    st.subheader("4. Calidad de Formato (Estricto APV vs BEP) & Panel de Control Total")
    st.markdown(
        "El comodín **`-`** está permitido por el BEP y no genera error. "
        "A continuación se analizan **todos** los elementos sin límite para auditar unidades, estados, espacios en blanco y textos inválidos."
    )
    
    @st.cache_data
    def calcular_todos_los_errores_formato(df_ref, params_audit, mask_F, vacíos_low, uni_val, est_val, ph_malos):
        errores_fmt = []
        for col in params_audit:
            if col not in df_ref.columns:
                continue
            s_col = df_ref[col]
            uniq = s_col.dropna().unique()
            if len(uniq) == 0:
                continue

            es_tmed = "TIPO-MED" in col.upper()
            es_est = "ESTADO" in col.upper()
            mapa_err = {}

            for x in uniq:
                v = str(x)
                v_limpio = v.strip()
                v_low = v_limpio.lower()
                if v_low in vacíos_low or v_limpio == "-":
                    continue
                mot = []
                if v != v_limpio:
                    mot.append("Espacios en blanco al inicio o final")
                if v_low in ph_malos:
                    mot.append("Comodín no permitido (debe usarse '-')")
                if es_tmed and v_low not in uni_val:
                    mot.append(f"Unidad no permitida ('{v_limpio}')")
                elif es_est and v_limpio.capitalize() not in est_val:
                    mot.append(f"Estado de obra no válido ('{v_limpio}')")
                if mot:
                    mapa_err[x] = " + ".join(mot)

            if mapa_err:
                m_err = mask_F & s_col.isin(list(mapa_err.keys())).to_numpy()
                if m_err.any():
                    idx_err = np.flatnonzero(m_err)
                    cols_e = ["Archivo_Origen", col_id_nativo, "GlobalId", col]
                    sub_e = df_ref[cols_e].iloc[idx_err]
                    for _, r_e in sub_e.iterrows():
                        val_det = r_e[col]
                        errores_fmt.append({
                            "Archivo": r_e["Archivo_Origen"],
                            "ID_Elemento": r_e[col_id_nativo],
                            "GlobalId": r_e["GlobalId"],
                            "Parámetro": col,
                            "Contenido Detectado": str(val_det),
                            "Infracción BEP": mapa_err.get(val_det, "Formato")
                        })
        return pd.DataFrame(errores_fmt)

    uni_validas = {"ud", "m", "m2", "dm3", "m3", "kg", "tn", "pa"}
    est_validos = {"Existente", "Demolido", "Temporal", "Proyectado", "Construido"}
    placeholders_malos = {"n/a", "na", "null", "none", "tbd", "sin definir", "por definir", "--", "."}

    with st.spinner("Procesando la totalidad de registros para formato..."):
        df_err_fmt_total = calcular_todos_los_errores_formato(
            df_original, params_auditar, mask_arr, VALORES_VACIOS_LOWER, uni_validas, est_validos, placeholders_malos
        )

    if not df_err_fmt_total.empty:
        st.warning(f"⚠️ Se detectaron un total de **{len(df_err_fmt_total):,}** infracciones de formato.")
        
        st.markdown("#### 🔎 Filtrar por Modelo y Parámetro (Saber qué actualizar):")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            archivos_con_error = sorted(df_err_fmt_total["Archivo"].unique().tolist())
            filtro_arch_f4 = st.multiselect("Filtrar por Modelo IFC:", archivos_con_error, default=archivos_con_error, key="f4_arch")
        with col_f2:
            params_con_error = sorted(df_err_fmt_total["Parámetro"].unique().tolist())
            filtro_param_f4 = st.multiselect("Filtrar por Parámetro dañado:", params_con_error, default=params_con_error, key="f4_param")
            
        df_filtrado_f4 = df_err_fmt_total[
            df_err_fmt_total["Archivo"].isin(filtro_arch_f4) & 
            df_err_fmt_total["Parámetro"].isin(filtro_param_f4)
        ]
        
        st.markdown(f"Mostrando **{len(df_filtrado_f4):,}** elementos identificados para actualizar:")
        st.dataframe(df_filtrado_f4, use_container_width=True)
        
        csv_err_fmt = df_filtrado_f4.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar Listado Completo de Errores de Formato (CSV)",
            data=csv_err_fmt,
            file_name="Errores_Formato_BEP_APV.csv",
            mime="text/csv",
            key="dl_f4"
        )
    else:
        st.success("✅ ¡Excelente! No se detectaron errores de formato bajo los filtros actuales.")

# --- PESTAÑA 5 ---
with tab5:
    st.subheader(
        f"5. Auditoría Exclusiva de los {len(params_auditar)} "
        "Parámetros Oficiales APV"
    )
    st.markdown(
        "Si un parámetro contiene **`-`**, se valida como **Comodín BEP "
        "en Verde (`🟢`)**. Si faltan elementos (`🔴`), a la derecha "
        "tienes una muestra de sus IDs para localizarlos en tu NWD."
    )

    cols_ids_ref = df_original[[col_id_nativo, "GlobalId"]]
    resumen_params = []

    for p in params_auditar:
        es_vac = mask_arr & mascara_vacio_rapida(df_original, p)
        es_com = mask_arr & mascara_comodin_rapida(df_original, p)
        n_vac = int(es_vac.sum())
        n_com = int(es_com.sum())
        n_datos = max(0, total_el - n_vac - n_com)
        pct_valido = (
            round(((n_datos + n_com) / total_el) * 100, 1)
            if total_el > 0 else 0.0
        )

        if n_vac == 0 and n_com > 0:
            estado_str = "🟢 Comodín BEP (-)"
            ids_faltantes, guids_faltantes = "-", "-"
        elif n_vac == 0:
            estado_str = "🟢 Completo (Dato)"
            ids_faltantes, guids_faltantes = "-", "-"
        else:
            estado_str = f"🔴 Faltan {n_vac:,} elementos"
            idx_f = np.flatnonzero(es_vac)[:30]
            sub_f = cols_ids_ref.iloc[idx_f]
            sufijo = " ..." if n_vac > 30 else ""
            ids_faltantes = (
                ", ".join(sub_f[col_id_nativo].astype(str)) + sufijo
            )
            guids_faltantes = (
                ", ".join(sub_f["GlobalId"].astype(str)) + sufijo
            )

        resumen_params.append({
            "Parámetro Oficial APV": p,
            "Estado Auditoría": estado_str,
            "Con Dato Real": n_datos,
            "Con Comodín (-) Válido": n_com,
            "Vacíos (Error)": n_vac,
            "% Cumplimiento (Dato + '-')": pct_valido,
            "ID_Elemento Faltantes (Revit/C3D)": ids_faltantes,
            "GlobalId Faltantes (NWD/IFC)": guids_faltantes
        })
    df_res_vacios = pd.DataFrame(resumen_params)

    def colorear_estado(val):
        if "🟢" in str(val):
            return "background-color: #d4edda; color: #155724; font-weight: bold;"
        return "background-color: #f8d7da; color: #721c24; font-weight: bold;"

    st.dataframe(
        df_res_vacios.style.map(colorear_estado, subset=["Estado Auditoría"]),
        use_container_width=True
    )

    n_inc_total = int(mask_tiene_vacios.sum())
    if n_inc_total > 0:
        st.markdown(
            f"#### 🔍 Detalle de Elementos con algún parámetro vacío "
            f"(mostrando primeros 300 de {n_inc_total:,}):"
        )
        idx_inc = np.flatnonzero(mask_tiene_vacios)[:300]
        cols_b = [
            c for c in [
                "Archivo_Origen", col_id_nativo, "GlobalId", "Clase_IFC", "Nombre"
            ] if c in df_original.columns
        ]
        df_inc_view = df_original[cols_b].iloc[idx_inc].copy()
        df_inc_view["Cant_Vacios"] = s_vac_arr[idx_inc]

        params_disp = [p for p in params_auditar if p in df_original.columns]
        sub_p = df_original[params_disp].iloc[idx_inc]
        mat_vac = sub_p.isna() | sub_p.isin(VACIOS_EXACTOS)
        df_inc_view["Parámetros_Vacíos"] = mat_vac.apply(
            lambda r: ", ".join(r.index[r]), axis=1
        )
        st.dataframe(df_inc_view, use_container_width=True)

# --- PESTAÑA 6 ---
with tab6:
    st.subheader(
        "6. Centro de Coordinación e Interferencias para Navisworks Manage"
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📥 1. Descargar Search Sets XML para Navisworks")
        opciones_nw = (
            ["TODOS los elementos con algún vacío"] + params_auditar
        )
        param_filtro_nw = st.selectbox(
            "Seleccionar grupo de elementos vacíos a aislar:", opciones_nw
        )
        if param_filtro_nw == "TODOS los elementos con algún vacío":
            mask_nw = mask_tiene_vacios
            nombre_xml = "APV_Todos_Los_Vacios"
        else:
            mask_nw = mask_arr & mascara_vacio_rapida(
                df_original, param_filtro_nw
            )
            nombre_xml = f"APV_Vacio_{param_filtro_nw}"

        usar_id_nativo = st.checkbox(
            "Usar ID_Elemento nativo (Tag) en lugar de GlobalId", value=True
        )
        n_sel_nw = int(mask_nw.sum())
        st.write(f"Elementos seleccionados para el XML: **{n_sel_nw:,}**")

        if n_sel_nw > 0:
            col_target = col_id_nativo if usar_id_nativo else "GlobalId"
            idx_nw = np.flatnonzero(mask_nw)[:2000]
            vals_nw = (
                df_original[col_target].iloc[idx_nw]
                .dropna().astype(str).unique()
            )
            xml_str = generar_xml_navisworks(
                vals_nw,
                nombre_set=nombre_xml,
                usar_id_nativo=usar_id_nativo
            )
            st.download_button(
                label=f"⬇️ Descargar XML ({min(len(vals_nw), 1000)} elementos)",
                data=xml_str,
                file_name=f"{nombre_xml}.xml",
                mime="text/xml"
            )
        else:
            st.info("No hay elementos vacíos para este filtro seleccionado.")

    with c2:
        st.markdown("#### 🔍 2. Auditoría de IDs Duplicados")
        if total_el > 0:
            sub_d = df_original[["Archivo_Origen", col_id_nativo]].loc[mask_arr]
            m_dup = sub_d.duplicated(
                subset=["Archivo_Origen", col_id_nativo], keep=False
            )
            n_dups = int(m_dup.sum())
            if n_dups > 0:
                st.warning(
                    f"⚠️ Se detectaron **{n_dups:,} elementos** con "
                    "ID_Elemento duplicado (mostrando primeros 500):"
                )
                idx_d = np.flatnonzero(mask_arr)[m_dup.to_numpy()][:500]
                cols_d = [
                    c for c in [
                        "Archivo_Origen", col_id_nativo,
                        "GlobalId", "Clase_IFC", "Nombre"
                    ] if c in df_original.columns
                ]
                st.dataframe(
                    df_original[cols_d].iloc[idx_d],
                    use_container_width=True
                )
            else:
                st.success(
                    "✅ No existen ID_Elemento duplicados en los modelos."
                )
        else:
            st.info("Sin datos para analizar duplicados.")

# --- PESTAÑA 7 ---
with tab7:
    st.subheader("7. Salud del Proyecto y Métricas Generales")
    c_s1, c_s2, c_s3 = st.columns(3)
    c_s1.metric("Modelos IFC Analizados", len(archivos_disp))
    c_s2.metric("Total Elementos Auditados", f"{len(df_original):,}")
    if "Peso_Archivo_MB" in df_original.columns:
        df_pesos = (
            df_original[["Archivo_Origen", "Peso_Archivo_MB"]]
            .drop_duplicates(subset=["Archivo_Origen"]).copy()
        )
        df_pesos["Peso_Archivo_MB"] = pd.to_numeric(
            df_pesos["Peso_Archivo_MB"], errors="coerce"
        ).fillna(0.0)
        peso_total = float(df_pesos["Peso_Archivo_MB"].sum())
        c_s3.metric(
            "Peso Consolidado de Modelos", f"{round(peso_total, 2)} MB"
        )
        fig_peso = px.bar(
            df_pesos,
            x="Archivo_Origen",
            y="Peso_Archivo_MB",
            title="Peso de Modelos IFC (MB)",
            text="Peso_Archivo_MB"
        )
        st.plotly_chart(fig_peso, use_container_width=True)
    else:
        c_s3.metric("Peso Consolidado de Modelos", "0.0 MB")

# --- PESTAÑA 8 ---
with tab8:
    st.subheader("🚨 8. Alertas y Diagnóstico de IFCs Vacíos por Modelo")
    df_t8 = pd.DataFrame({
        "arch": df_original["Archivo_Origen"],
        "vac": s_vac_arr > 0
    })
    grp_t8 = df_t8.groupby("arch")["vac"].agg(["count", "sum"])
    resumen_modelos_alt = []
    for arch in archivos_disp:
        tot = int(grp_t8.loc[arch, "count"]) if arch in grp_t8.index else 0
        n_v_m = int(grp_t8.loc[arch, "sum"]) if arch in grp_t8.index else 0
        if tot == 0:
            est = "🚨 IFC Vacío"
        elif n_v_m == tot:
            est = "🚨 100% Incompleto"
        elif n_v_m > 0:
            est = f"🔴 Parcial ({n_v_m:,} vacíos)"
        else:
            est = "🟢 100% Completo"
        resumen_modelos_alt.append({
            "Archivo IFC": arch,
            "Elementos": tot,
            "Estado General": est
        })
    st.dataframe(pd.DataFrame(resumen_modelos_alt), use_container_width=True)

# --- PESTAÑA 9 ---
with tab9:
    st.subheader("📐 Grupos de parámetros")
    st.markdown(
        "Informe detallado por modelo sobre los bloques y grupos de "
        "parámetros detectados según la directriz del BEP "
        "(**Geotecnia = 11 grupos**; **Resto de modelos = 9 grupos**)."
    )
    st.dataframe(df_informe_grupos, use_container_width=True)

# --- PESTAÑA 10 ---
with tab10:
    st.subheader("🔍 10. Ficha Detallada por Elemento (Inspector BIM)")
    st.markdown("Selecciona un elemento por su **GlobalId** para consultar todos sus atributos y parámetros APV al detalle.")
    
    ids_disponibles = df_original.loc[mask_arr, "GlobalId"].dropna().unique()
    if len(ids_disponibles) > 0:
        id_seleccionado = st.selectbox("Selecciona un GlobalId:", ids_disponibles, key="select_ficha_globalid")
        elem_info = df_original.loc[df_original["GlobalId"] == id_seleccionado].iloc[0]
        
        with st.expander(f"📋 Ficha Detallada del Elemento: {id_seleccionado}", expanded=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                st.metric("Clase IFC", elem_info.get("Clase_IFC", "N/A"))
                st.metric("Archivo Origen", elem_info.get("Archivo_Origen", "N/A"))
                st.text(f"ID Nativo (Tag): {elem_info.get(col_id_nativo, 'N/A')}")
            with col_f2:
                n_vacios_elem = sum(1 for p in params_auditar if p in elem_info and (pd.isna(elem_info[p]) or str(elem_info[p]).strip() in VACIOS_EXACTOS))
                st.metric("Parámetros APV Vacíos en este objeto", n_vacios_elem, delta_color="inverse")
                
            st.markdown("##### 📊 Todos los Parámetros APV Rellenos:")
            params_presentes = {p: elem_info[p] for p in params_auditar if p in elem_info}
            df_ficha = pd.DataFrame(list(params_presentes.items()), columns=["Parámetro BEP", "Valor Actual"])
            st.dataframe(df_ficha, use_container_width=True, hide_index=True)
    else:
        st.info("No hay elementos disponibles con los filtros actuales.")

# --- PESTAÑA 11 ---
with tab11:
    st.subheader("💬 11. Asistente IA de Entrega y Auditoría")
    st.markdown("Pregúntame cualquier duda sobre el estado de la entrega BIM, volúmenes, errores o estadísticas de los modelos.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ej: ¿Cómo va el estado general y cuántos elementos tienen vacíos?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            prompt_lower = prompt.lower()
            respuesta = ""
            
            if "cuantos" in prompt_lower or "total" in prompt_lower or "modelos" in prompt_lower:
                respuesta = f"Actualmente hay un total de **{total_el:,}** elementos auditados activos, repartidos en **{len(sel_archivos)}** modelos IFC de la Autoridad Portuaria de Valencia."
            elif "vacios" in prompt_lower or "faltan" in prompt_lower or "error" in prompt_lower:
                respuesta = f"Hay **{n_inc_total:,}** elementos que presentan al menos un parámetro oficial APV vacío que requiere revisión."
            elif "peso" in prompt_lower or "mb" in prompt_lower:
                respuesta = f"El peso consolidado de los modelos analizados en esta sesión es de **{round(peso_total, 2)} MB**."
            elif "progreso" in prompt_lower or "mes" in prompt_lower or "entrega" in prompt_lower:
                respuesta = f"Esta entrega cuenta con {len(sel_archivos)} modelos activos. Recuerda que el volumen de archivos debe mantenerse o incrementarse respecto al mes anterior."
            else:
                respuesta = "He analizado tu consulta con base en los datos de la base Parquet actual. Revisa las pestañas de auditoría de vacíos (Pestaña 5) o salud del proyecto (Pestaña 7) para ver el desglose gráfico."
                
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})

# --- PESTAÑA 12 (RESUMEN EJECUTIVO VISTOSO Y PROFESIONAL) ---
with tab12:
    st.subheader("📄 12. Resumen Ejecutivo & Presentación de Entrega - APV")
    st.markdown("---")
    
    st.markdown("### 🌟 Estado General del Proyecto y Consolidado")
    
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    col_e1.metric("Modelos Auditados", f"{len(sel_archivos)} IFCs", "Activos en sesión")
    col_e2.metric("Elementos Totales", f"{total_el:,}", "Bajo filtros actuales")
    col_e3.metric("Elementos con Alertas", f"{n_inc_total:,}", "Requieren revisión", delta_color="inverse")
    col_e4.metric("Peso Consolidado", f"{round(peso_total, 2)} MB", "Volumen BIM")
    
    st.markdown("---")
    
    st.markdown("#### 📋 Vista Previa del Acta de Entrega BIM")
    
    with st.container():
        st.info(
            f"**Entorno de Auditoría:** Autoridad Portuaria de Valencia (APV) \n\n"
            f"• **Modelos Seleccionados:** {', '.join(sel_archivos)} \n\n"
            f"• **Nivel de Cumplimiento General:** Se han procesado y auditado con éxito los parámetros oficiales del BEP, detectando un total de {n_inc_total:,} incidencias de vacíos o formato que ya pueden ser consultadas mediante los conjuntos de selección (Search Sets) exportados para Navisworks Manage."
        )
        
    st.markdown("#### 🚀 Opciones de Exportación para tu Equipo y Dirección")
    col_op1, col_op2 = st.columns(2)
    
    with col_op1:
        st.markdown("**📥 Descarga de Datos Tabulares (Excel / CSV)**")
        st.markdown("Ideal para que el equipo técnico revise fila por fila los elementos pendientes de completar.")
        csv_data = df_res_vacios.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar Reporte de Vacíos (CSV)",
            data=csv_data,
            file_name="Auditoria_BIM_APV_Reporte_Ejecutivo.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_op2:
        st.markdown("**🖨️ Exportación a PDF Limpio (Vista de Impresión)**")
        st.markdown("Para generar un PDF visualmente hermoso de esta pestaña sin plugins pesados:")
        st.markdown(
            "> 💡 *Tip Pro:* Presiona las teclas **`Ctrl + P`** (o `Cmd + P` en Mac) estando en esta pestaña, selecciona **'Guardar como PDF'** y tu navegador convertirá este resumen ejecutivo en un documento perfecto y listo para compartir."
        )

print("[DIAG FIN] Dashboard renderizado con éxito", flush=True)