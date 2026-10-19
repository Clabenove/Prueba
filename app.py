import os
import re
import gc
import time
import unicodedata
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Auditoría BIM & Cumplimiento BEP - APV",
    page_icon="📋",
    layout="wide"
)

# Estilos CSS para mejorar el acabado visual y permitir exportación limpia a PDF con Ctrl+P
st.markdown("""
<style>
@media print {
    section[data-testid="stSidebar"],
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    .stDownloadButton,
    .stButton,
    div[data-testid="stChatInput"] {
        display: none !important;
    }
    .main .block-container {
        padding-top: 0.5rem !important;
        max-width: 100% !important;
    }
}
.kpi-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}
.kpi-title {
    font-size: 0.85rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #f8fafc;
}
.kpi-sub {
    font-size: 0.8rem;
    color: #38bdf8;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

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
    "09-03_15_APV_PASA-0,16 (%)", "09-03_16_APV_PASA-