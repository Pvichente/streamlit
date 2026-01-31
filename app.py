# =========================================
# 1) IMPORTS
# =========================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# =========================================
# 2) CONFIGURACIÓN DE PÁGINA
# =========================================
st.set_page_config(
    page_title="Socialize your knowledge | Desempeño de colaboradores",
    layout="wide"
)

# =========================================
# 3) TÍTULO + DESCRIPCIÓN (RÚBRICA #1)
# =========================================
st.title("Conociendo el desempeño de los colaboradores")
st.markdown(
    """
Esta aplicación presenta un análisis exploratorio del desempeño de los colaboradores de **Socialize your knowledge**.
Permite filtrar por **género**, **rango de puntaje de desempeño** y **estado civil**, y visualizar indicadores y gráficas
para identificar fortalezas y áreas de oportunidad.
"""
)

# =========================================
# 4) LOGOTIPO (RÚBRICA #2)
# =========================================
try:
    st.image("logo.png", width=220)
except Exception:
    st.warning("No se encontró el logo en 'assets/logo.png'. Agrega una imagen para visualizar el logotipo.")


# =========================================
# 5) CARGA DE DATOS
# =========================================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Limpieza mínima (muy importante en este CSV)
    df["department"] = df["department"].astype(str).str.strip()
    df["gender"] = df["gender"].astype(str).str.strip()  # venía como 'M ' en varias filas

    # Tipos numéricos
    for col in ["performance_score", "salary", "average_work_hours", "age"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data("Employee_data.csv")

# Validación rápida
required_cols = ["gender", "performance_score", "marital_status", "average_work_hours", "age", "salary"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Faltan columnas requeridas en el CSV: {missing}")
    st.stop()


# =========================================
# 6) CONTROLES (SIDEBAR) (RÚBRICA #3, #4, #5)
# =========================================
st.sidebar.header("Filtros")

# (RÚBRICA #3) Control de género
gender_options = sorted(df["gender"].dropna().unique().tolist())
gender_sel = st.sidebar.multiselect("Selecciona el género", options=gender_options, default=gender_options)

# (RÚBRICA #4) Control de rango de puntaje de desempeño
min_score = int(np.nanmin(df["performance_score"]))
max_score = int(np.nanmax(df["performance_score"]))
score_range = st.sidebar.slider(
    "Selecciona el rango del puntaje de desempeño",
    min_value=min_score,
    max_value=max_score,
    value=(min_score, max_score),
    step=1
)

# (RÚBRICA #5) Control de estado civil
marital_options = sorted(df["marital_status"].dropna().unique().tolist())
marital_sel = st.sidebar.multiselect(
    "Selecciona el estado civil",
    options=marital_options,
    default=marital_options
)

# Aplicar filtros
df_f = df[
    (df["gender"].isin(gender_sel)) &
    (df["performance_score"].between(score_range[0], score_range[1])) &
    (df["marital_status"].isin(marital_sel))
].copy()

st.sidebar.write(f"Registros filtrados: **{len(df_f)}** / {len(df)}")

if len(df_f) == 0:
    st.warning("No hay datos con los filtros actuales. Ajusta los filtros para continuar.")
    st.stop()


# =========================================
# 7) KPI’s PRINCIPALES (opcional, suma valor)
# =========================================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Empleados (filtrados)", f"{len(df_f)}")
c2.metric("Desempeño promedio", f"{df_f['performance_score'].mean():.2f}")
c3.metric("Satisfacción promedio", f"{df_f['satisfaction_level'].mean():.2f}")
c4.metric("Ausencias promedio", f"{df_f['absences'].mean():.2f}")


# =========================================
# 8) VISUALIZACIONES (RÚBRICA #6, #7, #8, #9)
# =========================================
st.subheader("Visualizaciones")

colA, colB = st.columns(2)

# (RÚBRICA #6) Distribución de puntajes de desempeño
with colA:
    st.markdown("### Distribución de puntajes de desempeño")
    fig, ax = plt.subplots()
    counts = df_f["performance_score"].value_counts().sort_index()
    ax.bar(counts.index.astype(str), counts.values)
    ax.set_xlabel("Puntaje de desempeño")
    ax.set_ylabel("Número de empleados")
    ax.set_title("Distribución de puntajes")
    st.pyplot(fig)

# (RÚBRICA #7) Promedio de horas trabajadas por género
with colB:
    st.markdown("### Promedio de horas trabajadas por género")
    fig, ax = plt.subplots()
    avg_hours = df_f.groupby("gender")["average_work_hours"].mean().sort_index()
    ax.bar(avg_hours.index.astype(str), avg_hours.values)
    ax.set_xlabel("Género")
    ax.set_ylabel("Promedio de horas trabajadas")
    ax.set_title("Horas trabajadas promedio por género")
    st.pyplot(fig)

colC, colD = st.columns(2)

# (RÚBRICA #8) Edad vs salario (scatter)
with colC:
    st.markdown("### Edad vs salario")
    fig, ax = plt.subplots()
    ax.scatter(df_f["age"], df_f["salary"], alpha=0.7)
    ax.set_xlabel("Edad")
    ax.set_ylabel("Salario")
    ax.set_title("Relación edad-salario")
    st.pyplot(fig)

# (RÚBRICA #9) Promedio de horas trabajadas vs puntaje de desempeño
with colD:
    st.markdown("### Promedio de horas trabajadas vs puntaje de desempeño")
    fig, ax = plt.subplots()
    avg_by_score = df_f.groupby("performance_score")["average_work_hours"].mean().sort_index()
    ax.plot(avg_by_score.index, avg_by_score.values, marker="o")
    ax.set_xlabel("Puntaje de desempeño")
    ax.set_ylabel("Promedio de horas trabajadas")
    ax.set_title("Horas promedio vs desempeño")
    st.pyplot(fig)


# =========================================
# 9) TABLA DE DATOS (opcional)
# =========================================
st.subheader("Detalle de empleados (filtrado)")
st.dataframe(
    df_f[["id_employee", "name_employee", "gender", "marital_status",
          "department", "position", "performance_score", "salary",
          "average_work_hours", "age", "employment_status"]]
)

csv = df_f.to_csv(index=False).encode("utf-8")
st.download_button("Descargar datos filtrados (CSV)", data=csv, file_name="employee_data_filtrado.csv", mime="text/csv")


# =========================================
# 10) CONCLUSIONES (RÚBRICA #10)
# =========================================
st.subheader("Conclusiones del análisis")

# Conclusiones simples pero basadas en datos (sobre el filtrado actual)
perf_counts = df_f["performance_score_desc"].value_counts(normalize=True) * 100
top_desc = perf_counts.index[0]
top_pct = perf_counts.iloc[0]

corr = df_f[["performance_score", "satisfaction_level"]].corr().iloc[0, 1]

st.markdown(
    f"""
- En los datos filtrados, la categoría de desempeño más frecuente es **{top_desc}** con **{top_pct:.1f}%**.
- El **desempeño promedio** es **{df_f['performance_score'].mean():.2f}** (escala observada {min_score} a {max_score}).
- La **satisfacción promedio** es **{df_f['satisfaction_level'].mean():.2f}** y muestra una correlación con desempeño de **{corr:.2f}** (tendencia positiva).
- El promedio de **ausencias** es **{df_f['absences'].mean():.2f}**; valores altos pueden asociarse a riesgos de continuidad/engagement.
"""
)
